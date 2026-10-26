#!/usr/bin/env python3
"""Cut a short audio clip (and optional screenshots) from a video so you can hear/see a doubtful transcript line.

Usage:
  python3 scripts/clip_check.py <folder|URL> --at MM:SS [--before 5] [--after 30] [--frame] [--open] [--out DIR]
  python3 scripts/clip_check.py watch-output/佛學/<資料夾> --at 01:41 --frame --open
  python3 scripts/clip_check.py watch-output/佛學/<資料夾> --wait-confirm

--wait-confirm (lecture / 佛學 folders only): for every known_asr_errors entry with status "suspected" and a single
MM:SS time, cut one audio clip + one screenshot into <資料夾>/waitConfirm/ and write an index.md to click and re-listen.

<folder> is a watch-output folder: the URL comes from its meta.json and the transcript lines in the window are
printed with their offset inside the clip (clip time = video time - window start), so you know where to listen.
--frame also saves one 720p screenshot every --step seconds (default 5) for checking what the slide says.
Only the requested window is downloaded (yt-dlp --download-sections). Output goes to ~/.cache/watch/clips (outside
the repo; other people's videos are never committed). Needs yt-dlp and ffmpeg on PATH.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LINE = re.compile(r"^\[(\d+):(\d+)(?::(\d+))?\] (.*)$")
OUT_ROOT = Path.home() / ".cache" / "watch" / "clips"


def parse_ts(text):
    """'95', '01:35' or '1:02:03' -> seconds."""
    parts = [int(p) for p in str(text).strip().split(":")]
    if not parts or len(parts) > 3:
        raise ValueError(f"bad time: {text!r}")
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return sec


def fmt(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60:02d}:{sec % 60:02d}"


def window(at, before, after):
    """(start, end) seconds around `at`, never before 0."""
    start = max(0, at - before)
    return start, at + after


def lines_in_window(text, start, end):
    """[(seconds, offset in clip, wording)] for transcript lines inside the window."""
    out = []
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        a, b, c, body = m.groups()
        sec = int(a) * 3600 + int(b) * 60 + int(c) if c else int(a) * 60 + int(b)
        if start <= sec < end:
            out.append((sec, sec - start, body))
    return out


def resolve(source):
    """(url, transcript text or '') from a watch-output folder or a bare URL."""
    p = Path(source)
    if p.is_dir():
        meta = json.loads((p / "meta.json").read_text(encoding="utf-8"))
        tr = p / "transcript.md"
        return meta["url"], tr.read_text(encoding="utf-8") if tr.exists() else ""
    return source, ""


def download(url, start, end, fmt_sel, dest):
    cmd = ["yt-dlp", "-q", "--no-warnings", "-f", fmt_sel, "--download-sections", f"*{start}-{end}",
           "--force-keyframes-at-cuts", "-o", str(dest) + ".%(ext)s", url]
    subprocess.run(cmd, check=True, env={**os.environ, "PYTHONUTF8": "1"})
    found = sorted(dest.parent.glob(dest.name + ".*"))
    if not found:
        sys.exit("yt-dlp downloaded nothing (blocked, private or live without DVR?)")
    return found[0]


SINGLE_TS = re.compile(r"^\d+:\d{2}(?::\d{2})?$")
BAD_NAME = re.compile(r'[\\/:*?"<>|\s]+')
BEFORE, AFTER = 5, 25


def in_scope(meta):
    return meta.get("video_type") == "lecture" or meta.get("category") == "佛學"


def pick_suspected(errors):
    """([(seconds, entry)] sorted by time, [warning]) for status == suspected entries with one MM:SS time."""
    picked, warnings = [], []
    for e in errors:
        if e.get("status") != "suspected":
            continue
        t = str(e.get("time", "")).strip()
        if not SINGLE_TS.match(t):
            warnings.append(f"skip '{e.get('heard', '')}': time '{t}' is not a single MM:SS")
            continue
        picked.append((parse_ts(t), e))
    return sorted(picked, key=lambda x: x[0]), warnings


def clip_name(n, at, heard):
    word = BAD_NAME.sub("", heard.split("／")[0])[:12] or "clip"
    return f"{n:02d}_{fmt(at).replace(':', '-')}_{word}"


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_index(title, rows):
    out = [f"# 待確認音檔：{title}", "",
           "點 ▶ 重聽，聽完告訴 Claude 結果；片段從「時間點前 5 秒」開始。", "",
           "| # | 時間點 | 逐字稿該行 | 逐字稿寫法 | 目前寫法／候選 | 重聽 | 截圖 |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['n']} | {fmt(r['at'])} | {cell(r['line'])} | {cell(r['heard'])} | {cell(r['expected'])} "
                   f"| [▶ 重聽](./{r['name']}.mp3) | [截圖](./{r['name']}.jpg) |")
    return "\n".join(out) + "\n"


def cut_clip(url, at, before, after, mp3, jpg):
    """Default cutter: audio window -> mp3, one 720p screenshot at `at` -> jpg."""
    start, end = window(at, before, after)
    with tempfile.TemporaryDirectory() as tmp:
        raw = download(url, start, end, "ba", Path(tmp) / "a")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-b:a", "96k", str(mp3)], check=True)
        fs, fe = max(0, at - 1), at + 2
        vid = download(url, fs, fe, "bv*[height<=720]", Path(tmp) / "v")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(at - fs), "-i", str(vid), "-frames:v", "1", str(jpg)],
                       check=True)


def wait_confirm(folder, cut=cut_clip, warn=lambda m: print(f"WARNING: {m}", file=sys.stderr)):
    """Cut waitConfirm/ clips for the suspected entries of a watch-output folder; returns the rows written."""
    folder = Path(folder)
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    if not in_scope(meta):
        warn("not a lecture / 佛學 folder; waitConfirm skipped")
        return []
    tr = folder / "transcript.md"
    transcript = tr.read_text(encoding="utf-8") if tr.exists() else ""
    picked, warnings = pick_suspected(meta.get("known_asr_errors", []))
    for w in warnings:
        warn(w)
    rows = []
    for at, e in picked:
        start, end = window(at, BEFORE, AFTER)
        near = lines_in_window(transcript, start, end)
        if not near:
            warn(f"skip '{e.get('heard', '')}': no transcript line within {fmt(start)}-{fmt(end)}")
            continue
        heard = str(e.get("heard", ""))
        keys = [k for k in heard.split("／") if k]
        line = next((b for _, _, b in near if any(k in b for k in keys)), None)
        if line is None:
            line = min(near, key=lambda x: abs(x[0] - at))[2]
        n = len(rows) + 1
        rows.append({"n": n, "at": at, "name": clip_name(n, at, heard), "line": line,
                     "heard": heard, "expected": str(e.get("expected", ""))})
    if not rows:
        warn("no suspected entry to cut")
        return []
    out = folder / "waitConfirm"
    out.mkdir(exist_ok=True)
    for r in rows:
        cut(meta["url"], r["at"], BEFORE, AFTER, out / f"{r['name']}.mp3", out / f"{r['name']}.jpg")
    (out / "index.md").write_text(render_index(meta.get("title", folder.name), rows), encoding="utf-8")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="watch-output folder or video URL")
    ap.add_argument("--at", help="the doubtful moment, MM:SS or H:MM:SS")
    ap.add_argument("--before", type=int, default=5, help="seconds before --at (default 5)")
    ap.add_argument("--after", type=int, default=30, help="seconds after --at (default 30)")
    ap.add_argument("--frame", action="store_true", help="also save screenshots")
    ap.add_argument("--step", type=int, default=5, help="seconds between screenshots (default 5)")
    ap.add_argument("--open", action="store_true", help="open the audio in the default player")
    ap.add_argument("--out", help="output folder (default ~/.cache/watch/clips/<start>-<end>)")
    ap.add_argument("--wait-confirm", action="store_true", help="cut waitConfirm/ clips for suspected entries (folder only)")
    args = ap.parse_args(argv)

    if args.wait_confirm:
        if not Path(args.source).is_dir():
            ap.error("--wait-confirm needs a watch-output folder")
        rows = wait_confirm(args.source)
        print(f"waitConfirm: {len(rows)} clip(s) -> {Path(args.source) / 'waitConfirm' / 'index.md'}")
        return 0
    if not args.at:
        ap.error("--at is required (unless --wait-confirm)")

    url, transcript = resolve(args.source)
    start, end = window(parse_ts(args.at), args.before, args.after)
    out = Path(args.out) if args.out else OUT_ROOT / f"{fmt(start).replace(':', '-')}_{fmt(end).replace(':', '-')}"
    out.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        raw = download(url, start, end, "ba", Path(tmp) / "a")
        mp3 = out / f"clip_{fmt(start).replace(':', '-')}_to_{fmt(end).replace(':', '-')}.mp3"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-b:a", "96k", str(mp3)], check=True)
        if args.frame:
            vid = download(url, start, end, "bv*[height<=720]", Path(tmp) / "v")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-vf", f"fps=1/{args.step}",
                            str(out / "frame_%02d.jpg")], check=True)

    print(f"audio : {mp3}   (clip 00:00 = video {fmt(start)})")
    if args.frame:
        print(f"frames: {out}\\frame_NN.jpg   (every {args.step}s; frame_01 = video {fmt(start)})")
    for sec, off, body in lines_in_window(transcript, start, end):
        print(f"  video {fmt(sec)}  clip {fmt(off)}  {body}")
    if args.open:
        try:
            os.startfile(mp3)  # Windows
        except AttributeError:
            subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(mp3)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
