#!/usr/bin/env python3
"""Transcribe a video via local WhisperX or the Groq/OpenAI Whisper APIs.

Strategy: extract audio (mono 16kHz mp3, tiny payload), upload to whichever
API has a key. Returns segments in the same shape as transcribe.parse_vtt so
the rest of the pipeline (filter_range, format_transcript) doesn't care where
the transcript came from.

Pure stdlib — no `pip install groq` or `pip install openai` needed.
"""
from __future__ import annotations

import os
import re
import io
import json
from collections import Counter
import math
import mimetypes
import shutil
import ssl
import sys
import time
import urllib.error
import uuid
from pathlib import Path
from urllib.request import Request, urlopen

from config import load_api_key, ConfigError
from runtime import configure_stdio, run_text
from transcribe import Segments, normalize_segments


GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_MODEL = "whisper-large-v3"

OPENAI_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"
OPENAI_MODEL = "whisper-1"

# Both Groq's free tier and OpenAI whisper-1 cap uploads at 25 MB. We target a
# margin under that so multipart framing overhead never pushes a chunk over.
MAX_UPLOAD_BYTES = 24_000_000
MAX_MULTIPART_BYTES = 25_000_000


def plan_chunks(
    total_seconds: float,
    total_bytes: int,
    max_bytes: int = MAX_UPLOAD_BYTES,
) -> list[tuple[float, float]]:
    """Split a duration into contiguous (offset, duration) chunks under max_bytes.

    Size scales linearly with duration (constant-bitrate mono mp3), so an even
    time split yields evenly-sized chunks. Returns a single full-length chunk
    when the audio already fits.
    """
    if not math.isfinite(total_seconds) or total_seconds < 0 or max_bytes <= 0 or total_bytes < 0:
        raise SystemExit("Invalid audio chunk duration or byte budget")
    if total_bytes > max_bytes and total_seconds <= 0:
        raise SystemExit("Cannot split oversized audio with unknown duration")
    if total_bytes <= max_bytes or total_seconds <= 0:
        return [(0.0, total_seconds)]

    n = math.ceil(total_bytes / max_bytes)
    chunk = total_seconds / n
    plan: list[tuple[float, float]] = []
    for i in range(n):
        offset = i * chunk
        # The last chunk absorbs any rounding remainder so durations sum exactly.
        duration = (total_seconds - offset) if i == n - 1 else chunk
        plan.append((round(offset, 3), round(duration, 3)))
    return plan


def extract_audio(video_path: str, out_path: Path) -> Path:
    """Extract mono 16kHz 64kbps mp3 — ~480 kB/min, fits any Whisper limit."""
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is not installed. Install with: brew install ffmpeg")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", str(Path(video_path).resolve()),
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "16000",
        "-ac", "1",
        "-b:a", "64k",
        str(out_path.resolve()),
    ]
    result = run_text(cmd)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg audio extraction failed: {result.stderr.strip()}")
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise SystemExit("ffmpeg produced no audio — video may have no audio track")
    return out_path


def audio_duration(audio_path: Path) -> float:
    from frames import get_metadata
    return get_metadata(str(audio_path))["duration_seconds"]


def split_audio(
    full_audio: Path,
    work_dir: Path,
    plan: list[tuple[float, float]],
) -> list[tuple[Path, float]]:
    """Slice full_audio into per-plan chunk files, returning (path, offset) pairs.

    Uses stream copy (`-c copy`) so there is no re-encode and no quality loss;
    mp3 frame boundaries are close enough for transcription's purposes.
    """
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is not installed. Install with: brew install ffmpeg")

    work_dir.mkdir(parents=True, exist_ok=True)
    chunks: list[tuple[Path, float]] = []
    for index, (offset, duration) in enumerate(plan):
        out_path = work_dir / f"chunk_{index:03d}.mp3"
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-ss", f"{offset:.3f}",
            "-i", str(full_audio.resolve()),
            "-t", f"{duration:.3f}",
            "-c", "copy",
            str(out_path.resolve()),
        ]
        result = run_text(cmd)
        if result.returncode != 0 or not out_path.exists() or out_path.stat().st_size == 0:
            raise SystemExit(
                f"ffmpeg failed to split audio chunk {index + 1}: {result.stderr.strip()}"
            )
        chunks.append((out_path, offset))
    return chunks


def _build_multipart(fields: dict[str, str], file_path: Path) -> tuple[bytes, str]:
    """Assemble a multipart/form-data body the Whisper APIs accept.

    Whisper's multipart upload is small and predictable — doing it by hand
    keeps us on pure stdlib instead of pulling requests/groq/openai SDKs.
    """
    boundary = f"----WatchBoundary{uuid.uuid4().hex}"
    eol = b"\r\n"
    buf = io.BytesIO()

    for name, value in fields.items():
        buf.write(f"--{boundary}".encode()); buf.write(eol)
        buf.write(f'Content-Disposition: form-data; name="{name}"'.encode()); buf.write(eol)
        buf.write(eol)
        buf.write(str(value).encode()); buf.write(eol)

    mimetype = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    buf.write(f"--{boundary}".encode()); buf.write(eol)
    buf.write(
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"'.encode()
    )
    buf.write(eol)
    buf.write(f"Content-Type: {mimetype}".encode()); buf.write(eol)
    buf.write(eol)
    buf.write(file_path.read_bytes())
    buf.write(eol)
    buf.write(f"--{boundary}--".encode()); buf.write(eol)

    return buf.getvalue(), boundary


MAX_ATTEMPTS = 4       # initial + 3 retries
MAX_429_RETRIES = 2
RETRY_BASE_DELAY = 2.0


def _post_whisper(endpoint: str, api_key: str, model: str, audio_path: Path) -> dict:
    if audio_path.stat().st_size > MAX_UPLOAD_BYTES:
        raise SystemExit("Audio file exceeds the 24,000,000-byte upload budget; split it before upload.")
    fields = {
        "model": model,
        "response_format": "verbose_json",
        "temperature": "0",
    }
    # Local patch: optional hints to improve accuracy (set by scripts/watch_archive.py).
    if os.environ.get("WATCH_WHISPER_LANGUAGE"):
        fields["language"] = os.environ["WATCH_WHISPER_LANGUAGE"]
    if os.environ.get("WATCH_WHISPER_PROMPT"):
        fields["prompt"] = os.environ["WATCH_WHISPER_PROMPT"][:800]
    body, boundary = _build_multipart(fields, audio_path)
    if len(body) > MAX_MULTIPART_BYTES:
        raise SystemExit("Multipart request exceeds the 25,000,000-byte limit.")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        # Groq sits behind Cloudflare — the default `Python-urllib/3.x` UA
        # trips WAF rule 1010 (403) before auth even runs. Any non-default
        # UA clears it; we identify honestly.
        "User-Agent": "watch-skill/1.0 (+claude-code; python-urllib)",
    }

    context = ssl.create_default_context()
    rate_limit_hits = 0
    last_exc: Exception | None = None
    last_detail = ""

    for attempt in range(MAX_ATTEMPTS):
        request = Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=300, context=context) as response:
                payload = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            detail = _read_error_body(exc)
            last_exc, last_detail = exc, detail

            # 4xx other than 429 are client errors — no retry will fix them.
            if 400 <= exc.code < 500 and exc.code != 429:
                raise SystemExit(f"Whisper request failed: {exc}{detail}")

            if exc.code == 429:
                rate_limit_hits += 1
                if rate_limit_hits >= MAX_429_RETRIES:
                    raise SystemExit(f"Whisper request failed: {exc}{detail}")
                delay = _retry_after(exc) or RETRY_BASE_DELAY * (2 ** attempt) + 1
            else:
                delay = RETRY_BASE_DELAY * (2 ** attempt)

            if attempt < MAX_ATTEMPTS - 1:
                print(
                    f"[watch] whisper HTTP {exc.code} — retrying in {delay:.1f}s "
                    f"(attempt {attempt + 2}/{MAX_ATTEMPTS})",
                    file=sys.stderr,
                )
                time.sleep(delay)
            continue
        except (urllib.error.URLError, TimeoutError, ConnectionResetError, OSError) as exc:
            last_exc, last_detail = exc, ""
            if attempt < MAX_ATTEMPTS - 1:
                delay = RETRY_BASE_DELAY * (attempt + 1)
                print(
                    f"[watch] whisper network error ({type(exc).__name__}: {exc}) — "
                    f"retrying in {delay:.1f}s (attempt {attempt + 2}/{MAX_ATTEMPTS})",
                    file=sys.stderr,
                )
                time.sleep(delay)
            continue

        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Whisper returned non-JSON response: {exc}")

    raise SystemExit(
        f"Whisper request failed after {MAX_ATTEMPTS} attempts: {last_exc}{last_detail}"
    )


def _read_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read()
    except Exception:
        return ""
    if not body:
        return ""
    try:
        return f" — {body.decode('utf-8', errors='replace')[:400]}"
    except Exception:
        return ""


def _retry_after(exc: urllib.error.HTTPError) -> float | None:
    header = exc.headers.get("Retry-After") if getattr(exc, "headers", None) else None
    if not header:
        return None
    try:
        return float(header)
    except ValueError:
        return None


def shift_segments(segments: list[dict], offset_seconds: float) -> list[dict]:
    """Return a copy of segments with start/end shifted by offset_seconds.

    Each chunk is transcribed in isolation, so Whisper returns 0-based timestamps
    per chunk; shifting by the chunk's offset stitches them into source time.
    """
    if offset_seconds == 0:
        return segments
    return [
        {
            "start": round(seg["start"] + offset_seconds, 2),
            "end": round(seg["end"] + offset_seconds, 2),
            "text": seg["text"],
        }
        for seg in segments
    ]


def _segments_from_response(data: dict) -> list[dict]:
    try:
        return normalize_segments(data)
    except (ValueError, TypeError) as exc:
        raise SystemExit(f"Whisper returned malformed segments: {exc}") from None


def transcribe_chunks(
    chunks: list[tuple[Path, float]],
    transcribe_one,
) -> list[dict]:
    """Transcribe each chunk, shift its segments by the chunk offset, concatenate.

    A chunk that fails after its own retries is logged and skipped so one bad
    slice doesn't discard the whole transcript. Raises only if every chunk fails.
    """
    segments = Segments()
    failures = 0
    languages: list[str] = []  # Local patch: language reported per chunk
    for index, (path, offset) in enumerate(chunks):
        try:
            chunk_segments = transcribe_one(path)
        except SystemExit as exc:
            failures += 1
            end = chunks[index + 1][1] if index + 1 < len(chunks) else None
            segments.gaps.append({"start": offset, "end": end})
            print(
                f"[watch] chunk {index + 1}/{len(chunks)} failed — skipping ({exc})",
                file=sys.stderr,
            )
            continue
        segments.extend(shift_segments(chunk_segments, offset))
        if chunk_segments and getattr(chunk_segments, "language", ""):  # only chunks that actually had speech vote
            languages.append(chunk_segments.language)
        print(
            f"[watch] chunk {index + 1}/{len(chunks)} → {len(chunk_segments)} segments",
            file=sys.stderr,
        )

    if failures == len(chunks):
        raise SystemExit("Whisper failed on every audio chunk")
    segments.no_speech = not segments and not failures
    if languages:
        segments.language = Counter(languages).most_common(1)[0][0]  # ties keep the earliest chunk's language
    return segments


# Local patch: Groq's long-form transcription sometimes ends a 30 s window right after a short heading,
# silently dropping the rest of that window's speech; the same span sent alone transcribes fine.
GAP_REFILL_SECONDS = 15.0
REFILL_PIECE_SECONDS = 30.0
MAX_GAP_REFILLS = 40  # bounds extra API calls on long music / silence (a failed chunk costs 1, see limit_refills)
SPARSE_WINDOW_SECONDS = 20.0  # sparse-text scan: windows this long ...
SPARSE_MIN_CPS = 1.0  # ... with fewer characters per second than this are sent again
SPARSE_MIN_WINDOW = 5.0  # a leftover window shorter than this at the end is not worth a call
REFILL_PAD_SECONDS = 2.0  # context sent on each side of a refill span


def _split_pieces(edges: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Cut each span into pieces of at most REFILL_PIECE_SECONDS."""
    pieces = []
    for start, end in edges:
        while end - start > REFILL_PIECE_SECONDS:
            pieces.append((start, start + REFILL_PIECE_SECONDS))
            start += REFILL_PIECE_SECONDS
        pieces.append((start, end))
    return pieces


def _merge_spans(spans: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Sort spans and join the ones that touch or overlap."""
    out: list[list[float]] = []
    for start, end in sorted(spans):
        if out and start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return [(a, b) for a, b in out]


def _gap_edges(segments: list[dict], total_seconds: float, min_gap: float) -> list[tuple[float, float]]:
    edges, cursor = [], 0.0
    for seg in segments:
        if seg["start"] - cursor >= min_gap:
            edges.append((cursor, seg["start"]))
        cursor = max(cursor, seg["end"])
    if total_seconds - cursor >= min_gap:
        edges.append((cursor, total_seconds))
    return edges


def find_gaps(segments: list[dict], total_seconds: float,
              min_gap: float = GAP_REFILL_SECONDS) -> list[tuple[float, float]]:
    """Spans with no segment for at least min_gap seconds, split into pieces of at most 30 s."""
    return _split_pieces(_gap_edges(segments, total_seconds, min_gap))


def _wording(text: str) -> str:
    return re.sub(r"[\W_]+", "", text)


def is_prompt_leak(text: str, prompt: str) -> bool:
    """True when a segment is just words of the Whisper prompt (Whisper echoes the prompt on thin audio)."""
    wording = _wording(text)
    return len(wording) >= 3 and wording in _wording(prompt)


def find_sparse_spans(segments: list[dict], total_seconds: float, prompt: str = "",
                      window: float = SPARSE_WINDOW_SECONDS,
                      min_cps: float = SPARSE_MIN_CPS) -> list[tuple[float, float]]:
    """Windows that hold speech-sized time but almost no text: a long segment that kept only a heading,
    or one that is only prompt words. find_gaps cannot see these because the timeline has no hole."""
    spans, start = [], 0.0
    while total_seconds - start >= SPARSE_MIN_WINDOW:
        end = min(start + window, total_seconds)
        chars = 0.0
        for seg in segments:
            if seg["end"] <= start or seg["start"] >= end or (prompt and is_prompt_leak(seg["text"], prompt)):
                continue
            share = (min(seg["end"], end) - max(seg["start"], start)) / max(seg["end"] - seg["start"], 0.01)
            chars += len(_wording(seg["text"])) * share
        if chars / (end - start) < min_cps:
            spans.append((start, end))
        start = end
    return _merge_spans(spans)


def find_refill_spans(segments: list[dict], total_seconds: float, prompt: str = "") -> list[tuple[float, float]]:
    """Everything worth sending to Whisper again: timeline holes plus sparse windows, in pieces of <= 30 s."""
    edges = _gap_edges(segments, total_seconds, GAP_REFILL_SECONDS) + find_sparse_spans(segments, total_seconds, prompt)
    return _split_pieces(_merge_spans(edges))


def limit_refills(pieces: list[tuple[float, float]], failed_chunks: list[dict],
                  budget: int = MAX_GAP_REFILLS) -> list[tuple[float, float]]:
    """Keep pieces in time order until the budget is spent. A chunk that failed whole shows up as many pieces
    but costs 1, so one bad upload cannot use up the budget meant for real speech gaps elsewhere."""
    def chunk_of(piece):
        for index, gap in enumerate(failed_chunks):
            if piece[0] >= gap["start"] and (gap["end"] is None or piece[1] <= gap["end"] + 1):
                return index
        return None

    kept, spent, charged = [], 0, set()
    for piece in pieces:
        chunk = chunk_of(piece)
        cost = 0 if chunk in charged else 1
        if spent + cost > budget:
            continue
        spent += cost
        if chunk is not None:
            charged.add(chunk)
        kept.append(piece)
    if len(kept) < len(pieces):
        print(f"[watch] {len(pieces)} refill spans found; refilling only {len(kept)} (budget {budget})",
              file=sys.stderr)
    return kept


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def _chars_in(segs: list[dict]) -> int:
    return sum(len(_wording(seg["text"])) for seg in segs)


def _subtract(gap: dict, filled: list[tuple[float, float]]) -> list[dict]:
    """The parts of a missing interval that no successful refill covered."""
    end = float("inf") if gap["end"] is None else gap["end"]
    parts, cursor = [], gap["start"]
    for start, stop in sorted(filled):
        if stop <= cursor or start >= end:
            continue
        if start > cursor:
            parts.append((cursor, start))
        cursor = max(cursor, stop)
    if cursor < end:
        parts.append((cursor, end))
    return [{"start": a, "end": None if b == float("inf") else b} for a, b in parts
            if b == float("inf") or b - a >= 1.0]


def fill_gaps(segments: Segments, gaps: list[tuple[float, float]], slice_audio, transcribe_one,
              pad: float = 0.0) -> Segments:
    """Re-transcribe each span on its own and merge the results back in time order.

    slice_audio(start, duration) returns an audio file for that span, widened by `pad` seconds on both sides so
    a word cut at the edge is heard whole; transcribe_one(file) returns its 0-based segments. Only refill
    segments that start inside the span are kept. Original segments mostly inside the span are replaced, but
    only when the refill has more text than they did. A failed or empty refill is logged and the span stays
    missing: segments.gaps is rewritten to the intervals no refill covered.
    """
    if not gaps:
        return segments
    merged = list(segments)
    filled: list[tuple[float, float]] = []
    still_empty = 0
    for start, end in gaps:
        lo = max(0.0, start - pad) if pad else start
        try:
            refill = transcribe_one(slice_audio(lo, end + pad - lo))
        except SystemExit as exc:
            print(f"[watch] gap {start:.0f}-{end:.0f}s refill failed — skipping ({exc})", file=sys.stderr)
            still_empty += 1
            continue
        new = [seg for seg in shift_segments(refill, lo) if start <= seg["start"] < end]
        inside = [seg for seg in merged
                  if _overlap(seg["start"], seg["end"], start, end) >= 0.5 * max(seg["end"] - seg["start"], 0.01)]
        if not new or _chars_in(new) <= _chars_in(inside):
            if not new and not inside:
                still_empty += 1
            continue
        merged = [seg for seg in merged if not any(seg is old for old in inside)] + new
        filled.append((start, end))
    remaining = [part for gap in segments.gaps for part in _subtract(gap, filled)]
    out = Segments(sorted(merged, key=lambda seg: seg["start"]),
                   gaps=remaining, no_speech=segments.no_speech, language=segments.language)
    print(f"[watch] refilled {len(filled)} gap(s), {still_empty} still empty: "
          f"{len(segments)} → {len(out)} segments", file=sys.stderr)
    return out


def _transcribe_file(backend: str, api_key: str, audio_path: Path) -> list[dict]:
    """Upload one audio file and return its 0-based segments."""
    if backend == "groq":
        response = _post_whisper(GROQ_ENDPOINT, api_key, GROQ_MODEL, audio_path)
    elif backend == "openai":
        response = _post_whisper(OPENAI_ENDPOINT, api_key, OPENAI_MODEL, audio_path)
    else:
        raise SystemExit(f"Unknown whisper backend: {backend}")
    return _segments_from_response(response)


def transcribe_video(
    video_path: str,
    audio_out: Path,
    backend: str | None = None,
    api_key: str | None = None,
) -> tuple[list[dict], str]:
    """Run the full flow: extract audio → upload → parse segments.

    Returns (segments, backend_used). Raises SystemExit on any failure.
    """
    if api_key is not None and backend is None:
        raise SystemExit("An API key requires an explicit groq or openai backend.")
    if backend == "whisperx":
        if api_key is not None:
            raise SystemExit("WhisperX does not accept an API key.")
        from local_whisperx import transcribe_audio
        segments = transcribe_audio(extract_audio(video_path, audio_out))
        return segments, "whisperx"
    if backend not in (None, "groq", "openai"):
        raise SystemExit("Unknown transcription backend.")
    if backend is None or api_key is None:
        detected_backend, detected_key = load_api_key(preferred=backend)
        backend = backend or detected_backend
        api_key = api_key or detected_key

    if not backend or not api_key:
        setup_py = Path(__file__).resolve().parent / "setup.py"
        raise SystemExit(
            "No Whisper API key available. Set GROQ_API_KEY (preferred) or OPENAI_API_KEY "
            "in the environment or in ~/.config/watch/.env. "
            f"Run `python3 {setup_py}` to configure."
        )

    print(f"[watch] extracting audio for Whisper ({backend})…", file=sys.stderr)
    audio_path = extract_audio(video_path, audio_out)
    audio_bytes = audio_path.stat().st_size

    def transcribe_one(path: Path) -> list[dict]:
        return _transcribe_file(backend, api_key, path)

    if audio_bytes <= MAX_UPLOAD_BYTES:
        print(
            f"[watch] audio: {audio_bytes / 1024:.0f} kB — uploading to {backend} Whisper…",
            file=sys.stderr,
        )
        segments = transcribe_one(audio_path)
    else:
        duration = audio_duration(audio_path)
        plan = plan_chunks(duration, audio_bytes, MAX_UPLOAD_BYTES - 64_000)
        print(
            f"[watch] audio: {audio_bytes / (1024 * 1024):.0f} MB exceeds "
            f"{MAX_UPLOAD_BYTES // (1024 * 1024)} MB — splitting into {len(plan)} chunks…",
            file=sys.stderr,
        )
        chunks = split_audio(audio_path, audio_out.parent / "chunks", plan)
        if any(path.stat().st_size > MAX_UPLOAD_BYTES for path, _ in chunks):
            raise SystemExit("A split audio chunk exceeds the upload budget; no chunks were uploaded.")
        segments = transcribe_chunks(chunks, transcribe_one)

    gaps = []
    if segments:
        gaps = find_refill_spans(segments, audio_duration(audio_path), os.environ.get("WATCH_WHISPER_PROMPT", ""))
        gaps = limit_refills(gaps, getattr(segments, "gaps", []))
    if gaps:
        def slice_audio(start: float, duration: float) -> Path:
            return split_audio(audio_path, audio_out.parent / "gaps" / f"{start:.0f}", [(start, duration)])[0][0]
        segments = fill_gaps(segments, gaps, slice_audio, transcribe_one, pad=REFILL_PAD_SECONDS)

    if not segments:
        print("[watch] Whisper detected no speech", file=sys.stderr)

    print(f"[watch] transcribed {len(segments)} segments via {backend}", file=sys.stderr)
    return segments, backend


if __name__ == "__main__":
    import argparse
    configure_stdio()
    parser = argparse.ArgumentParser(description="Transcribe local media with the selected Whisper backend.")
    parser.add_argument("video")
    parser.add_argument("audio_out", nargs="?", default="audio.mp3", type=Path)
    parser.add_argument("--backend", choices=["groq", "openai", "whisperx"])
    args = parser.parse_args()
    try:
        segments, backend = transcribe_video(args.video, Path(args.audio_out), backend=args.backend)
    except ConfigError as exc:
        raise SystemExit(str(exc)) from None
    print(json.dumps({"backend": backend, "segments": segments}, indent=2))
