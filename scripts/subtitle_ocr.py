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
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

DEFAULT_CROP = "iw*0.82:ih*0.18:0:ih*0.8"
PUNCT = re.compile(r"[\s，。、？！；：「」『』（）《》\"“”…—\-·,.?!:;\[\]()0-9a-zA-Z]")
CJK = re.compile(r"[一-鿿]")
LINE = re.compile(r"^\[(\d+):(\d+)(?::(\d+))?\] (.*)$")
HF_V5 = "https://huggingface.co/monkt/paddleocr-onnx/resolve/main/languages/chinese/"
V5_FILES = {"rec.onnx": "rec_model_path", "dict.txt": "rec_keys_path"}
# v4 misreads traditional glyphs as these look-alikes; applied only to v4 output (v5 does not need it). Only reads that
# have no legitimate use in sutra lectures: 编 (遍/編) and 竞 (竟/競) are real words too, so they are left for a human.
FIXED_MISREADS = {"罪生": "眾生", "筱": "從", "弛": "祂", "菩隆": "菩薩"}
AUTO_SEGMENT_MIN = 30   # videos longer than this many minutes are OCR'd in segments unless --segment-min says otherwise
SEGMENT_MIN = 10        # minutes per segment when segmenting automatically
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


def v5_paths():
    """Local paths of the PP-OCRv5 Chinese recognizer and its dictionary, downloaded on first use."""
    import urllib.request
    cache = Path.home() / ".cache" / "watch" / "ppocrv5"
    cache.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, kwarg in V5_FILES.items():
        dest = cache / name
        if not dest.exists() or dest.stat().st_size == 0:
            print(f"downloading PP-OCRv5 {name} ...", file=sys.stderr, flush=True)
            urllib.request.urlretrieve(HF_V5 + name, dest)
        paths[kwarg] = str(dest)
    return paths


def load_ocr(model="v5"):
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        sys.exit("rapidocr_onnxruntime is not installed. Make a venv and `pip install rapidocr-onnxruntime`, "
                 "then run this script with that venv's python (see the header of this file).")
    return RapidOCR(**v5_paths()) if model == "v5" else RapidOCR()


def read_text(engine, image_path):
    """One OCR pass over a band image; boxes are joined top-to-bottom, left-to-right."""
    result, _ = engine(str(image_path))
    if not result:
        return ""
    result = sorted(result, key=lambda r: (round(r[0][0][1] / 20), r[0][0][0]))
    return "".join(r[1] for r in result)


_engine = None


def _ocr_chunk(job):
    global _engine
    model, paths = job
    if _engine is None:
        _engine = load_ocr(model)
    return [read_text(_engine, p) for p in paths]


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


def ocr_range(video, workers, every, crop, model, start=None, end=None):
    """OCR one time range of the video; returns {seconds (absolute, as str): text}."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = extract_band(video, tmp, every, crop, start, end)
        print(f"{len(paths)} band images", flush=True)
        thumbs = thumbnails(paths)
        todo, source = [], {}   # indexes to OCR; every other index copies the nearest earlier OCR'd one
        prev, prev_i = None, None
        for i, th in enumerate(thumbs):
            if band_changed(prev, th):
                todo.append(i)
                prev, prev_i = th, i
            source[i] = prev_i
        print(f"OCR on {len(todo)} changed images (skipping {len(paths) - len(todo)})", flush=True)
        chunks = [todo[k::workers] for k in range(workers)]
        with ProcessPoolExecutor(workers) as pool:
            parts = list(pool.map(_ocr_chunk, [(model, [paths[i] for i in c]) for c in chunks]))
        text = {}
        for c, texts in zip(chunks, parts):
            text.update(zip(c, texts))
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
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def clock(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def run_segmented(out, seg_dir, segments, ocr_segment, log=print, every=None):
    """OCR each segment that has no seg file yet, then merge them all into `out` once none is missing.

    ocr_segment(start, end) -> {seconds: text}. Logs one line per segment. plan.json in seg_dir records the plan so
    `status` can tell how much is left. Returns the segment starts still missing (empty = merged)."""
    Path(seg_dir).mkdir(parents=True, exist_ok=True)
    write_atomic(Path(seg_dir) / "plan.json", {"out": str(out), "every": every, "segments": segments})
    todo = len(segments)
    for n, (a, b) in enumerate(segments, 1):
        span = f"{clock(a)}-{clock(b)}"
        if seg_path(seg_dir, a).exists():
            log(f"[seg {n}/{todo}] {span} already done, skipping")
            continue
        t0 = time.time()
        data = ocr_segment(a, b)
        write_atomic(seg_path(seg_dir, a), data)
        log(f"[seg {n}/{todo}] {span} done: {len(data)} samples, {time.time() - t0:.0f}s")
    missing = [a for a, _ in segments if not seg_path(seg_dir, a).exists()]
    if missing:
        return missing
    merged = {}
    for a, _ in segments:
        merged.update(json.loads(seg_path(seg_dir, a).read_text(encoding="utf-8")))
    write_atomic(out, dict(sorted(merged.items(), key=lambda kv: int(kv[0]))))
    return []


def status_report(out, seg_dir=None):
    """Lines describing how far a segmented run got: done / left / running, last activity, merged or not."""
    seg_dir = Path(seg_dir or str(out) + ".segs")
    plan_file = seg_dir / "plan.json"
    if not plan_file.exists():
        return [f"no segmented run found in {seg_dir} (run with --segment-min, or wrong --out/--seg-dir)"]
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    segs = [tuple(x) for x in plan["segments"]]
    done = [s for s in segs if seg_path(seg_dir, s[0]).exists()]
    running = [s for s in segs if s not in done and (seg_dir / f"seg_{s[0]:05d}.lock").exists()]
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


def cmd_run(args):
    total = video_duration(args.video) if args.segment_min is None or args.segment_min else None
    if args.segment_min is None:
        step_min = resolve_segment_min(None, total, args.auto_segment_min)
        if step_min:
            print(f"video is {total / 60:.0f} min (> {args.auto_segment_min}): OCR in {step_min}-minute segments "
                  f"(--segment-min 0 to disable)", flush=True)
    else:
        step_min = args.segment_min
    if not step_min:
        out = ocr_range(args.video, args.workers, args.every, args.crop, args.model, args.start, args.end)
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    seg_dir = args.seg_dir or str(args.out) + ".segs"
    segments = plan_segments(total, step_min, args.every, args.start, args.end)
    missing = run_segmented(
        args.out, seg_dir, segments,
        lambda a, b: ocr_range(args.video, args.workers, args.every, args.crop, args.model, a, b), every=args.every)
    if missing:
        print(f"{len(missing)} segment(s) missing (starts: {missing}); {args.out} not written", file=sys.stderr)
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
    p.add_argument("--model", choices=["v5", "v4"], default="v5")
    p.set_defaults(fn=cmd_probe)
    p = sub.add_parser("run", help="OCR the subtitle band into a JSON file")
    p.add_argument("video")
    p.add_argument("--out", required=True)
    p.add_argument("--crop", default=DEFAULT_CROP)
    p.add_argument("--every", type=int, default=2, help="seconds between sampled frames")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--model", choices=["v5", "v4"], default="v5")
    p.add_argument("--start", type=int)
    p.add_argument("--end", type=int)
    p.add_argument("--segment-min", type=int, help="OCR in segments of N minutes, each saved to --seg-dir so a rerun "
                   "resumes; 0 = one pass; default: segments of 10 min when the video is longer than --auto-segment-min")
    p.add_argument("--auto-segment-min", type=int, default=AUTO_SEGMENT_MIN)
    p.add_argument("--seg-dir", help="where segment files go (default <out>.segs)")
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
    p.add_argument("--model", choices=["v5", "v4"], default="v5", help="model the ocr.json came from (v4 gets the misread fixes)")
    p.set_defaults(fn=cmd_compare)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
