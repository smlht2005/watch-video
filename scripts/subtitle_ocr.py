#!/usr/bin/env python3
"""OCR a video's burned-in subtitles and diff them against transcript.md (docs/subtitle-ocr-vs-whisper.md).

Burned-in subtitles are the ground truth for names, book titles and terms that Whisper mishears, but they are
written language, not the speaker's words: use the diff to fix wording, never to overwrite whole lines.

Scope: it is slow (about an hour for a 74-minute video), so use it only for sutra lectures (佛經講解／講經) that have
burned-in subtitles; run `probe` first.

Usage:
  python3 scripts/subtitle_ocr.py probe <video> [--model v5|v4]          # are there burned-in subtitles at all?
  python3 scripts/subtitle_ocr.py run <video> --out ocr.json [--workers 2] [--every 3] [--model v5|v4] [--start S] [--end S]
                                            [--segment-min N|0] [--auto-segment-min 30] [--seg-dir DIR]
                                            [--low-priority] [--background]
  python3 scripts/subtitle_ocr.py status ocr.json [--seg-dir DIR]     # how many segments are done / left / running
  python3 scripts/subtitle_ocr.py compare <folder> --ocr ocr.json [--thr 0.85] [--out diff.txt]

`run` crops the subtitle band (--crop W:H:X:Y, ffmpeg expressions; default = bottom 18% / left 82%, which keeps a
vertical title on the right out of the band), grabs one frame every --every seconds, skips frames whose band is
unchanged, and OCRs the rest in parallel. Output is {"seconds": "text"}. The video is never committed (media/ is
gitignored); put ocr.json and the frames in the scratchpad.

Segments: a video longer than --auto-segment-min (30) minutes is OCR'd in 10-minute segments, each saved at once as
<out>.segs/seg_<start s>.json; rerun the same command to resume (existing segments are skipped; delete one to redo it);
when none is missing they are merged into --out. --segment-min N sets the length, 0 forces a single pass.

OCR needs RapidOCR; install it in its own venv so the system Python is untouched:
  python -m venv ocrenv && ocrenv/Scripts/pip install rapidocr-onnxruntime   (Windows; bin/ elsewhere)
and run `probe`/`run` with that venv's python (`compare` needs only opencc, so the normal python works).

Models (--model): `v5` (default) is PP-OCRv5 Chinese recognition, which reads traditional glyphs correctly; the RapidOCR
default `v4` is simplified-first and misreads traditional subtitles into fixed look-alikes (眾→罪, 從→筱, 遍→编, 竟→竞,
薩→隆, 祂→弛, 偈→偶) that OpenCC cannot repair. v5 downloads about 84 MB once into ~/.cache/watch/ppocrv5 and runs about
3x slower than v4 (its recognizer is larger; detection stays on the fast v4 model). With either model, read each
difference before applying it; `--model v4` output is also passed through FIXED_MISREADS in `compare`.
"""
import argparse
import difflib
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

DEFAULT_CROP = "iw*0.82:ih*0.18:0:ih*0.8"
PUNCT = re.compile(r"[\s，。、？！；：「」『』（）《》\"“”…—\-·,.?!:;\[\]()0-9a-zA-Z]")
CJK = re.compile(r"[一-鿿]")
LINE = re.compile(r"^\[(\d+):(\d+)(?::(\d+))?\] (.*)$")
# PP-OCRv5 Chinese recognizers: the mobile one (16 MB) reads the same subtitles as the server one (84 MB) about 20x faster
V5_MODELS = {
    "v5": ("ppocrv5-mobile", "https://huggingface.co/twmht/ppocr_v5_mobile/resolve/main/",
           {"rec.onnx": "rec_model_path", "ppocr_keys_ocrv5.txt": "rec_keys_path"}),
    "v5-server": ("ppocrv5", "https://huggingface.co/monkt/paddleocr-onnx/resolve/main/languages/chinese/",
                  {"rec.onnx": "rec_model_path", "dict.txt": "rec_keys_path"}),
}
MODEL_CHOICES = ["v5", "v5-server", "v4"]
# v4 misreads traditional glyphs as these look-alikes; applied only to v4 output (v5 does not need it). Only reads that
# have no legitimate use in sutra lectures: 编 (遍/編) and 竞 (竟/競) are real words too, so they are left for a human.
FIXED_MISREADS = {"罪生": "眾生", "筱": "從", "弛": "祂", "菩隆": "菩薩"}
AUTO_SEGMENT_MIN = 30   # videos longer than this many minutes are OCR'd in segments unless --segment-min says otherwise
SEGMENT_MIN = 10        # minutes per segment when segmenting automatically
LOCK_TTL = 30 * 60      # seconds after which a segment lock is considered abandoned
SLOW_IMAGE_S = 15       # an image slower than this gets its own trace line
OCR_BATCH = 10          # images per work item, so progress can be traced while a segment is running
UNCHANGED = 3.0   # mean 0-255 difference of a 48x12 thumbnail below which two band images count as the same


def norm(s):
    """Drop punctuation, digits, Latin letters and spaces so only the wording is compared."""
    return PUNCT.sub("", s)


def band_changed(prev, cur, limit=UNCHANGED):
    """True when two equal-sized grayscale thumbnails (flat byte sequences) differ by more than `limit` on average."""
    if prev is None or len(prev) != len(cur):
        return True
    return sum(abs(a - b) for a, b in zip(prev, cur)) / max(len(cur), 1) > limit


def merge_events(ocr, every=2, similar=0.8):
    """Fold consecutive, near-identical OCR reads into subtitle events {start, end, n (normalised), raw}.

    The longest read of an event wins, since a subtitle that is fading in or out OCRs shorter.
    """
    events = []
    for t in sorted(ocr, key=int):
        t = int(t)
        raw = ocr[str(t)] if str(t) in ocr else ocr[t]
        n = norm(raw)
        if not n:
            continue
        last = events[-1] if events else None
        if (last and t - last["end"] <= every + 2
                and difflib.SequenceMatcher(None, last["n"], n).ratio() > similar):
            if len(n) > len(last["n"]):
                last["n"], last["raw"] = n, raw
            last["end"] = t + every
        else:
            events.append({"start": t, "end": t + every, "n": n, "raw": raw})
    return events


def parse_transcript(text):
    """[(seconds, original line, wording)] for each `[mm:ss] text` / `[h:mm:ss] text` line."""
    out = []
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        a, b, c, body = m.groups()
        sec = int(a) * 3600 + int(b) * 60 + int(c) if c else int(a) * 60 + int(b)
        out.append((sec, line, body))
    return out


def coverage(wording, candidate):
    """Share of the transcript line's characters that also appear (in order) in the subtitle text."""
    a = norm(wording)
    if not a:
        return 1.0
    sm = difflib.SequenceMatcher(None, a, candidate, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / len(a)


def compare(lines, events, thr=0.85, window_pad=1):
    """Transcript lines whose wording the subtitles in the same time window cover by less than `thr`."""
    flagged = []
    for i, (t, line, body) in enumerate(lines):
        if not norm(body):
            continue
        nxt = lines[i + 1][0] if i + 1 < len(lines) else t + 4
        hit = [e for e in events if e["end"] > t - window_pad and e["start"] < max(nxt, t + 2) + window_pad]
        cov = coverage(body, "".join(e["n"] for e in hit))
        if cov < thr:
            flagged.append({"line": line, "subtitle": [e["raw"] for e in hit], "coverage": round(cov, 2)})
    return flagged


def download_file(url, dest, retrieve=None):
    """Download to `<dest>.part` and rename on success, so an interrupted download never looks like a finished model."""
    if retrieve is None:
        import urllib.request
        retrieve = urllib.request.urlretrieve
    part = Path(str(dest) + ".part")
    try:
        retrieve(url, part)
        if not part.exists() or part.stat().st_size == 0:
            raise OSError(f"empty download: {url}")
        os.replace(part, dest)
    except BaseException:
        part.unlink(missing_ok=True)
        raise


def v5_paths(model="v5"):
    """Local paths of a PP-OCRv5 Chinese recognizer and its dictionary, downloaded on first use."""
    folder, base, files = V5_MODELS[model]
    cache = Path.home() / ".cache" / "watch" / folder
    cache.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, kwarg in files.items():
        dest = cache / name
        if not dest.exists() or dest.stat().st_size == 0:
            print(f"downloading {model} {name} ...", file=sys.stderr, flush=True)
            download_file(base + name, dest)
        paths[kwarg] = str(dest)
    return paths


def load_ocr(model="v5"):
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        sys.exit("rapidocr_onnxruntime is not installed. Make a venv and `pip install rapidocr-onnxruntime`, "
                 "then run this script with that venv's python (see the header of this file).")
    return RapidOCR(**(v5_paths(model) if model in V5_MODELS else {}))


def join_boxes(result):
    """Text of the detected boxes, top-to-bottom then left-to-right."""
    if not result:
        return ""
    result = sorted(result, key=lambda r: (round(r[0][0][1] / 20), r[0][0][0]))
    return "".join(r[1] for r in result)


def read_text(engine, image_path):
    """One OCR pass over a band image; boxes are joined top-to-bottom, left-to-right."""
    result, _ = engine(str(image_path))
    return join_boxes(result)


def read_text_timed(engine, image_path):
    """read_text plus where the time went: (text, {wall, det, cls, rec, other, boxes, w, h}) in seconds.

    RapidOCR reports det/cls/rec itself; `other` is the rest (decode, resize, pre/post-processing, python overhead)."""
    from PIL import Image
    with Image.open(image_path) as im:
        w, h = im.size
    t0 = time.time()
    result, elapse = engine(str(image_path))
    wall = time.time() - t0
    det, cls, rec = (list(elapse) + [0.0, 0.0, 0.0])[:3] if elapse and len(elapse) == 3 else (0.0, 0.0, 0.0)
    return join_boxes(result), {"wall": wall, "det": det, "cls": cls, "rec": rec,
                                "other": max(wall - det - cls - rec, 0.0), "boxes": len(result or []), "w": w, "h": h}


_engine = None


def _ocr_chunk(job):
    global _engine
    model, paths = job
    if _engine is None:
        _engine = load_ocr(model)
    texts, infos = [], []
    for p in paths:
        text, info = read_text_timed(_engine, p)
        texts.append(text)
        infos.append(info)
    return texts, infos


def extract_band(video, outdir, every, crop, start=None, end=None):
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", str(video)]
    if end:
        cmd += ["-t", str(end - (start or 0))]
    cmd += ["-vf", f"fps=1/{every},crop={crop}", str(Path(outdir) / "s_%05d.png")]
    subprocess.run(cmd, check=True)
    return sorted(Path(outdir).glob("s_*.png"))


def thumbnails(paths):
    from PIL import Image
    return [list(Image.open(p).convert("L").resize((48, 12)).tobytes()) for p in paths]


def cmd_probe(args):
    """OCR ~12 evenly spaced frames; subtitles are 'present' when most of them read 4+ CJK characters."""
    duration = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", args.video],
        check=True, capture_output=True, text=True).stdout.strip())
    n = 12
    engine = load_ocr(args.model)
    hits = []
    with tempfile.TemporaryDirectory() as tmp:
        for k in range(n):
            t = duration * (k + 0.5) / n
            png = Path(tmp) / f"p{k}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.1f}", "-i", args.video, "-frames:v", "1",
                            "-vf", f"crop={args.crop}", str(png)], check=True)
            text = read_text(engine, png)
            hits.append(len(CJK.findall(text)) >= 4)
            print(f"  {int(t) // 60:02d}:{int(t) % 60:02d}  {text or '(none)'}")
    ratio = sum(hits) / n
    print(f"burned-in subtitles: {'yes' if ratio >= 0.5 else 'no'} ({sum(hits)}/{n} samples had text)")
    return 0 if ratio >= 0.5 else 1


def say(msg):
    print(msg, flush=True)


def mean_info(infos):
    n = max(len(infos), 1)
    return {k: sum(i[k] for i in infos) / n for k in ("wall", "det", "cls", "rec", "other", "boxes", "w", "h")}


def describe_info(i):
    """One trace fragment: total = det + cls + rec + other, then boxes and image size."""
    return (f"{i['wall']:.1f}s = det {i['det']:.1f} + cls {i['cls']:.1f} + rec {i['rec']:.1f} + other {i['other']:.1f}, "
            f"{i['boxes']:.1f} boxes, {i['w']:.0f}x{i['h']:.0f}px")


def ocr_range(video, workers, every, crop, model, start=None, end=None, log=say):
    """OCR one time range of the video; returns {seconds (absolute, as str): text}. Logs a `[trace]` line per stage
    and per batch of images so a slow run shows where the time goes."""
    t_all = time.time()
    log(f"[trace] pid {os.getpid()} priority {priority_name()}, {os.cpu_count()} cpus, workers {workers}, "
        f"model {model}, power {power_status()}")
    with tempfile.TemporaryDirectory() as tmp:
        t0 = time.time()
        paths = extract_band(video, tmp, every, crop, start, end)
        log(f"[trace] extract {len(paths)} band images: {time.time() - t0:.0f}s")
        t0 = time.time()
        thumbs = thumbnails(paths)
        todo, source = [], {}   # indexes to OCR; every other index copies the nearest earlier OCR'd one
        prev, prev_i = None, None
        for i, th in enumerate(thumbs):
            if band_changed(prev, th):
                todo.append(i)
                prev, prev_i = th, i
            source[i] = prev_i
        log(f"[trace] thumbnails + change detection: {time.time() - t0:.0f}s; OCR on {len(todo)} changed images "
            f"(skipping {len(paths) - len(todo)})")
        batches = [todo[k:k + OCR_BATCH] for k in range(0, len(todo), OCR_BATCH)]
        text, done, infos, t0 = {}, 0, [], time.time()
        with ProcessPoolExecutor(workers) as pool:
            futures = {pool.submit(_ocr_chunk, (model, [paths[i] for i in c])): c for c in batches}
            for fut in as_completed(futures):
                texts, batch = fut.result()
                text.update(zip(futures[fut], texts))
                done += len(texts)
                infos += batch
                for i, info in zip(futures[fut], batch):
                    if info["wall"] >= SLOW_IMAGE_S:
                        log(f"[trace] slow image at {(start or 0) + i * every}s: {describe_info(info)}")
                log(f"[trace] OCR {done}/{len(todo)} images, {time.time() - t0:.0f}s elapsed, "
                    f"slowest {max(x['wall'] for x in infos):.1f}s | avg per image: {describe_info(mean_info(infos))}")
    log(f"[trace] range done in {time.time() - t_all:.0f}s, power {power_status()}")
    base = start or 0
    return {str(base + i * every): text[source[i]] for i in range(len(paths))}


def video_duration(video):
    return float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        check=True, capture_output=True, text=True).stdout.strip())


def resolve_segment_min(requested, duration, auto_min=AUTO_SEGMENT_MIN):
    """Minutes per segment, or 0 for a single pass. None = decide by length: longer than `auto_min` minutes -> SEGMENT_MIN."""
    if requested is not None:
        return max(requested, 0)
    return SEGMENT_MIN if duration > auto_min * 60 else 0


def plan_segments(total, step_min, every, start=None, end=None):
    """[(seg_start, seg_end)] covering [start, end or total); each segment is a multiple of `every` seconds long so the
    sample points of all segments together are the same as one pass."""
    step = max(step_min * 60 // every, 1) * every
    lo, hi = start or 0, int(min(end, total)) if end else int(total + 0.999)
    return [(a, min(a + step, hi)) for a in range(lo, hi, step)]


def seg_path(seg_dir, start):
    return Path(seg_dir) / f"seg_{start:05d}.json"


def write_atomic(path, data):
    """Write JSON so a killed process never leaves a half-written segment that looks finished."""
    tmp = Path(f"{path}.{os.getpid()}.tmp")   # per process: two runs on one dir must not share a tmp file
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def clock(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def _kernel32():
    """kernel32 with explicit signatures: ctypes' default int types truncate 64-bit handles and the call silently fails."""
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k32.SetPriorityClass.restype = wintypes.BOOL
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.GetExitCodeProcess.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.GetPriorityClass.argtypes = [wintypes.HANDLE]
    k32.GetPriorityClass.restype = wintypes.DWORD
    return k32


def pid_alive(pid):
    """Is a process with this pid running on this machine? (os.kill(pid, 0) would kill it on Windows, so ask the OS.)"""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k32 = _kernel32()
        handle = k32.OpenProcess(0x1000, False, int(pid))   # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = wintypes.DWORD()
        ok = k32.GetExitCodeProcess(handle, ctypes.byref(code))
        k32.CloseHandle(handle)
        return bool(ok) and code.value == 259   # STILL_ACTIVE
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def lock_path(seg_dir, start):
    return Path(seg_dir) / f"seg_{start:05d}.lock"


def lock_is_stale(path, ttl=LOCK_TTL, now=time.time, alive=pid_alive):
    """A lock is abandoned when its process no longer runs (taken on this machine: age does not matter, a slow
    segment can outlast `ttl`), or, for a lock from another machine we cannot ask, when it is older than `ttl`."""
    try:
        info = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True   # empty/garbled lock: the taker died while writing it
    if info.get("host") == socket.gethostname():
        return not alive(info.get("pid", -1))
    return now() - info.get("time", 0) > ttl


def claim_segment(seg_dir, start, ttl=LOCK_TTL, now=time.time, alive=pid_alive):
    """Take the lock for one segment. Exactly one caller wins; an abandoned lock is taken over."""
    path = lock_path(seg_dir, start)
    for _ in range(3):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if not lock_is_stale(path, ttl, now, alive):
                return False
            grabbed = f"{path}.grab.{os.getpid()}"
            try:   # rename (not delete) so that only one of several takers gets hold of the dead lock
                os.rename(path, grabbed)
            except OSError:
                continue   # someone else already took it over: loop and see who holds it now
            if lock_is_stale(grabbed, ttl, now, alive):
                os.replace(grabbed, f"{path}.stale.{os.getpid()}.{int(now())}")
                continue
            try:   # we grabbed a live lock another process created after our check: give it back, never over a newer one
                os.link(grabbed, path)
            except OSError:
                pass   # the name was taken meanwhile: that process holds the segment now
            finally:
                os.remove(grabbed)
            return False
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "host": socket.gethostname(), "time": now()}, f)
        return True
    return False


def release_segment(seg_dir, start):
    try:
        os.remove(lock_path(seg_dir, start))
    except OSError:
        pass


class PlanMismatch(RuntimeError):
    """The segment files in a seg_dir were made with other parameters than this run's."""


def check_plan_params(plan_file, params):
    """Refuse to resume (and merge) segments made with a different model / sampling / crop / video / range."""
    if params is None or not Path(plan_file).exists():
        return
    try:
        old = json.loads(Path(plan_file).read_text(encoding="utf-8")).get("params")
    except (OSError, ValueError):
        return
    if old is None or old == params:   # a plan from before params were recorded cannot be checked
        return
    diff = ", ".join(f"{k}: {old.get(k)!r} -> {params.get(k)!r}" for k in sorted(set(old) | set(params))
                     if old.get(k) != params.get(k))
    raise PlanMismatch(f"segments in {Path(plan_file).parent} were made with different settings ({diff}); "
                       f"use a new --out, or delete that folder to start over")


def run_segmented(out, seg_dir, segments, ocr_segment, log=say, every=None, ttl=LOCK_TTL, params=None):
    """OCR each segment that has no seg file yet, then merge them all into `out` once none is missing.

    ocr_segment(start, end) -> {seconds: text}. Several processes may run this on the same seg_dir: each segment is
    claimed with a lock file, so they never OCR the same one; segments held by others are left for them. Logs one line per segment. plan.json in seg_dir records the plan so
    `status` can tell how much is left. Returns the segment starts still missing (empty = merged)."""
    Path(seg_dir).mkdir(parents=True, exist_ok=True)
    check_plan_params(Path(seg_dir) / "plan.json", params)
    write_atomic(Path(seg_dir) / "plan.json", {"out": str(out), "every": every, "segments": segments, "params": params})
    todo = len(segments)
    for n, (a, b) in enumerate(segments, 1):
        span = f"{clock(a)}-{clock(b)}"
        if seg_path(seg_dir, a).exists():
            log(f"[seg {n}/{todo}] {span} already done, skipping")
            continue
        if not claim_segment(seg_dir, a, ttl):
            log(f"[seg {n}/{todo}] {span} is being run by another process, skipping")
            continue
        try:
            if seg_path(seg_dir, a).exists():   # finished by someone else between our check and our claim
                continue
            t0 = time.time()
            data = ocr_segment(a, b)
            write_atomic(seg_path(seg_dir, a), data)
            log(f"[seg {n}/{todo}] {span} done: {len(data)} samples, {time.time() - t0:.0f}s")
        finally:
            release_segment(seg_dir, a)
    missing = [a for a, _ in segments if not seg_path(seg_dir, a).exists()]
    if missing:
        return missing
    merged = {}
    for a, _ in segments:
        merged.update(json.loads(seg_path(seg_dir, a).read_text(encoding="utf-8")))
    write_atomic(out, dict(sorted(merged.items(), key=lambda kv: int(kv[0]))))
    return []


def status_report(out, seg_dir=None, ttl=LOCK_TTL):
    """Lines describing how far a segmented run got: done / left / running, last activity, merged or not."""
    seg_dir = Path(seg_dir or str(out) + ".segs")
    plan_file = seg_dir / "plan.json"
    if not plan_file.exists():
        return [f"no segmented run found in {seg_dir} (run with --segment-min, or wrong --out/--seg-dir)"]
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    segs = [tuple(x) for x in plan["segments"]]
    done = [s for s in segs if seg_path(seg_dir, s[0]).exists()]
    running = [s for s in segs if s not in done and lock_path(seg_dir, s[0]).exists()
               and not lock_is_stale(lock_path(seg_dir, s[0]), ttl)]
    left = [s for s in segs if s not in done]
    lines = [f"{len(done)}/{len(segs)} segments done, {len(left)} left"]
    if running:
        lines.append("running: " + ", ".join(f"{clock(a)}-{clock(b)}" for a, b in running))
    waiting = [s for s in left if s not in running]
    if waiting:
        lines.append("waiting: " + ", ".join(f"{clock(a)}-{clock(b)}" for a, b in waiting))
    if done:
        newest = max(seg_path(seg_dir, a).stat().st_mtime for a, _ in done)
        lines.append(f"last segment finished {int((time.time() - newest) / 60)} min ago")
    if not left:
        lines.append(f"all segments done; {'merged into ' + str(out) if Path(out).exists() else 'rerun the same run command to merge into ' + str(out)}")
    return lines


def cmd_status(args):
    for line in status_report(args.out, args.seg_dir):
        print(line)
    return 0


PRIORITY_NAMES = {0x40: "Idle", 0x4000: "BelowNormal", 0x20: "Normal", 0x8000: "AboveNormal", 0x80: "High", 0x100: "Realtime"}


def priority_name():
    """This process's priority, for the trace log (Windows class name; elsewhere the nice value)."""
    if os.name == "nt":
        k32 = _kernel32()
        return PRIORITY_NAMES.get(k32.GetPriorityClass(k32.GetCurrentProcess()), "unknown")
    return f"nice {os.nice(0)}"


def power_status():
    """'AC 88%' / 'battery 62%' / 'unknown' for the trace log: on battery a laptop CPU is power-limited and runs several
    times slower (measured 4 s vs 11-35 s per image), which looks like a hang unless the log says so."""
    try:
        if os.name == "nt":
            import ctypes

            class Status(ctypes.Structure):
                _fields_ = [("ac", ctypes.c_ubyte), ("flag", ctypes.c_ubyte), ("percent", ctypes.c_ubyte),
                            ("saver", ctypes.c_ubyte), ("life", ctypes.c_ulong), ("full", ctypes.c_ulong)]
            st = Status()
            if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(st)):
                return "unknown"
            return format_power(st.ac, st.percent)
        base = Path("/sys/class/power_supply")
        ac = [int((d / "online").read_text()) for d in base.glob("A*") if (d / "online").exists()]
        pct = [int((d / "capacity").read_text()) for d in base.glob("BAT*") if (d / "capacity").exists()]
        return format_power(1 if any(ac) else 0 if ac else 255, pct[0] if pct else 255)
    except (OSError, ValueError, IndexError):
        return "unknown"


def format_power(ac, percent):
    """ac: 1 = on AC, 0 = on battery, anything else unknown (GetSystemPowerStatus values); percent 255 = unknown."""
    state = {1: "AC", 0: "battery"}.get(ac, "unknown power")
    return state + ("" if percent > 100 else f" {percent}%")


def apply_low_priority():
    """Lower this process's priority (Windows: Idle class, elsewhere nice 19); worker processes inherit it."""
    if os.name == "nt":
        k32 = _kernel32()
        if not k32.SetPriorityClass(k32.GetCurrentProcess(), 0x40):   # IDLE_PRIORITY_CLASS
            raise OSError("SetPriorityClass failed")
    else:
        os.nice(19)


def background_command(argv, script):
    """The command that re-runs this `run` invocation detached: no --background, with --low-priority, unbuffered."""
    rest = [a for a in argv if a != "--background"]
    if "--low-priority" not in rest:
        rest.append("--low-priority")
    return [sys.executable, "-u", str(script)] + rest


def start_background(cmd, log_path, popen=subprocess.Popen):
    """Start `cmd` detached from this session (it survives closing the terminal / Claude), appending output to log_path."""
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    log = open(log_path, "a", encoding="utf-8")
    kw = {"stdin": subprocess.DEVNULL, "stdout": log, "stderr": subprocess.STDOUT, "close_fds": True,
          "env": {**os.environ, "PYTHONUTF8": "1"}}
    if os.name == "nt":
        kw["creationflags"] = 0x00000008 | 0x00000200 | 0x08000000   # DETACHED_PROCESS | NEW_PROCESS_GROUP | NO_WINDOW
    else:
        kw["start_new_session"] = True
    proc = popen(cmd, **kw)
    log.close()
    return proc


def segment_min_arg(text):
    """argparse type for --segment-min: minutes, 0 or more."""
    n = int(text)
    if n < 0:
        raise argparse.ArgumentTypeError("--segment-min must be 0 (single pass) or a positive number of minutes")
    return n


def check_video(video):
    """Stop early (before a background process hides the error in its log) when the video file is not there."""
    if not Path(video).is_file():
        sys.exit(f"video not found: {video}")


def cmd_run(args):
    check_video(args.video)
    if args.background:
        seg_dir = args.seg_dir or str(args.out) + ".segs"
        log_path = Path(seg_dir) / "progress.log"
        proc = start_background(background_command(args.raw_argv, Path(__file__).resolve()), log_path)
        print(f"started in the background (pid {proc.pid}, low priority); progress: {log_path}")
        print(f"check with: python3 scripts/subtitle_ocr.py status {args.out}"
              + (f" --seg-dir {args.seg_dir}" if args.seg_dir else ""))
        print("closing this terminal / Claude does not stop it; a reboot does (rerun the same command to resume)")
        return 0
    if args.low_priority:
        apply_low_priority()
    total = video_duration(args.video) if args.segment_min is None or args.segment_min else None
    if args.segment_min is None:
        step_min = resolve_segment_min(None, total, args.auto_segment_min)
        if step_min:
            print(f"video is {total / 60:.0f} min (> {args.auto_segment_min}): OCR in {step_min}-minute segments "
                  f"(--segment-min 0 to disable)", flush=True)
    else:
        step_min = args.segment_min
    if not step_min:
        if args.seg_dir:
            print("warning: --seg-dir is ignored with --segment-min 0 (a single pass writes only --out, no resume)",
                  file=sys.stderr)
        out = ocr_range(args.video, args.workers, args.every, args.crop, args.model, args.start, args.end)
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    seg_dir = args.seg_dir or str(args.out) + ".segs"
    segments = plan_segments(total, step_min, args.every, args.start, args.end)
    params = {"video": str(args.video), "model": args.model, "every": args.every, "crop": args.crop,
              "start": args.start, "end": args.end}
    try:
        missing = run_segmented(
            args.out, seg_dir, segments,
            lambda a, b: ocr_range(args.video, args.workers, args.every, args.crop, args.model, a, b),
            every=args.every,
            ttl=args.lock_ttl,
            params=params)
    except PlanMismatch as e:
        print(str(e), file=sys.stderr)
        return 2
    if missing:
        busy = [a for a in missing if lock_path(seg_dir, a).exists()]
        print(f"{len(missing)} segment(s) missing (starts: {missing}); {args.out} not written", file=sys.stderr)
        if busy:
            print(f"{len(busy)} of them are being run by another process; run `status {args.out}` and rerun this "
                  f"command when they finish to merge", file=sys.stderr)
        return 1
    print(f"wrote {args.out} from {len(segments)} segments in {seg_dir}")
    return 0


def to_traditional(ocr):
    """OCR reads simplified glyphs even from traditional subtitles; convert so they compare with transcript.md."""
    try:
        from opencc import OpenCC
    except ImportError:
        print("opencc not installed: simplified subtitle glyphs will show up as false differences", file=sys.stderr)
        return ocr
    cc = OpenCC("s2t")
    return {k: cc.convert(v) for k, v in ocr.items()}


def fix_misreads(ocr):
    """Undo the fixed look-alike misreads of the v4 model (see FIXED_MISREADS)."""
    out = {}
    for k, v in ocr.items():
        for bad, good in FIXED_MISREADS.items():
            v = v.replace(bad, good)
        out[k] = v
    return out


def cmd_compare(args):
    ocr = json.loads(Path(args.ocr).read_text(encoding="utf-8"))
    ocr = to_traditional(fix_misreads(ocr) if args.model == "v4" else ocr)
    lines = parse_transcript((Path(args.folder) / "transcript.md").read_text(encoding="utf-8"))
    lo, hi = args.start or 0, args.end or float("inf")
    lines = [l for l in lines if lo <= l[0] < hi]
    flagged = compare(lines, merge_events(ocr, args.every), args.thr)
    body = "\n".join(f"{f['line']}\n    字幕: {' | '.join(f['subtitle']) or '(無)'}   [{f['coverage']:.2f}]"
                     for f in flagged)
    if args.out:
        Path(args.out).write_text(body, encoding="utf-8")
    else:
        print(body)
    print(f"{len(flagged)} flagged of {len(lines)} lines (coverage < {args.thr}); short or time-shifted lines "
          f"give false alarms, so read each one", file=sys.stderr)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe", help="check whether the video has burned-in subtitles")
    p.add_argument("video")
    p.add_argument("--crop", default=DEFAULT_CROP)
    p.add_argument("--model", choices=MODEL_CHOICES, default="v5")
    p.set_defaults(fn=cmd_probe)
    p = sub.add_parser("run", help="OCR the subtitle band into a JSON file")
    p.add_argument("video")
    p.add_argument("--out", required=True)
    p.add_argument("--crop", default=DEFAULT_CROP)
    p.add_argument("--every", type=int, default=2, help="seconds between sampled frames")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--model", choices=MODEL_CHOICES, default="v5")
    p.add_argument("--start", type=int)
    p.add_argument("--end", type=int)
    p.add_argument("--segment-min", type=segment_min_arg, help="OCR in segments of N minutes, each saved to --seg-dir so a rerun "
                   "resumes; 0 = one pass; default: segments of 10 min when the video is longer than --auto-segment-min")
    p.add_argument("--auto-segment-min", type=int, default=AUTO_SEGMENT_MIN)
    p.add_argument("--seg-dir", help="where segment files go (default <out>.segs)")
    p.add_argument("--low-priority", action="store_true", help="run at idle priority so the laptop stays usable")
    p.add_argument("--background", action="store_true",
                   help="start detached from this session (implies --low-priority), log to <seg-dir>/progress.log, return at once")
    p.add_argument("--lock-ttl", type=int, default=LOCK_TTL, help="seconds after which a segment lock counts as abandoned")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("status", help="show how far a segmented run got")
    p.add_argument("out", help="the --out of the run")
    p.add_argument("--seg-dir")
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("compare", help="list transcript lines the subtitles do not cover")
    p.add_argument("folder")
    p.add_argument("--ocr", required=True)
    p.add_argument("--thr", type=float, default=0.85)
    p.add_argument("--every", type=int, default=2)
    p.add_argument("--start", type=int)
    p.add_argument("--end", type=int)
    p.add_argument("--out")
    p.add_argument("--model", choices=MODEL_CHOICES, default="v5", help="model the ocr.json came from (v4 gets the misread fixes)")
    p.set_defaults(fn=cmd_compare)
    args = ap.parse_args(argv)
    args.raw_argv = list(sys.argv[1:] if argv is None else argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
