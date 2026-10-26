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
WATCH_SCRIPTS = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "watch" / "scripts"
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
        return source_url(meta), tr.read_text(encoding="utf-8") if tr.exists() else ""
    return source, ""


def source_url(meta):
    """meta.json's url, or a CutError that says what is missing (local-file archives have none)."""
    url = meta.get("url")
    if not url:
        raise CutError("meta.json 沒有 url（本機影片歸檔？），沒有來源網址可下載")
    return url


class CutError(Exception):
    """A clip could not be downloaded or cut; the message says why and what to do."""


def auth_args():
    """yt-dlp cookie / JS-runtime args, the same as the main pipeline (WATCH_COOKIES_* from env or ~/.config/watch/.env)."""
    sys.path.insert(0, str(WATCH_SCRIPTS))
    try:
        try:
            import config
            import download as watch_download
        except ImportError:
            return []
        try:
            cfg = config.get_config()
        except config.ConfigError:
            return []
        return watch_download.auth_args(cfg["cookies_file"] or None, cfg["cookies_from_browser"] or None)
    finally:
        sys.path.remove(str(WATCH_SCRIPTS))


def run_tool(cmd):
    """Run yt-dlp / ffmpeg; a missing executable or non-zero exit becomes a CutError instead of a traceback."""
    try:
        run = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                             env={**os.environ, "PYTHONUTF8": "1"})
    except FileNotFoundError:
        raise CutError(f"找不到 {cmd[0]}，請先安裝並加入 PATH") from None
    if run.returncode:
        raise CutError(explain_failure(run.stderr, cmd[0]))
    return run


BLOCKED = re.compile(r"429|too many requests|sign in|confirm you.re not a bot|cookies", re.I)


def explain_failure(stderr, tool="yt-dlp"):
    """User-facing reason for a failed yt-dlp / ffmpeg run (YouTube blocking gets the cookies hint)."""
    last = (stderr or "").strip().splitlines()[-1:] or [f"{tool} failed"]
    if tool == "yt-dlp" and BLOCKED.search(stderr or ""):
        firefox_note = "（Windows 上 Chrome／Edge 的 App-Bound 加密 yt-dlp 解不開，只能用 Firefox）" if sys.platform == "win32" else ""
        return (f"YouTube 擋下載（429／要求登入）：{last[0]}。給 yt-dlp 登入後的 cookies 再重跑，三選一："
                f"WATCH_COOKIES_FROM_BROWSER=firefox{firefox_note}、WATCH_COOKIES_FILE=<cookies.txt 路徑>、"
                f"WATCH_COOKIES_CONTENT=<cookies.txt 全文>（可放在環境變數或 ~/.config/watch/.env）")
    return f"{tool} 失敗：{last[0]}"


# video-only stream first; sources that only offer one muxed stream (Facebook, Google Drive) fall back to it
VIDEO_FMT = "bv*[height<=720]/b[height<=720]"


def download(url, start, end, fmt_sel, dest):
    cmd = ["yt-dlp", "-q", "--no-warnings", "-f", fmt_sel, "--download-sections", f"*{start}-{end}",
           "--force-keyframes-at-cuts", "-o", str(dest) + ".%(ext)s", url]
    cmd[1:1] = auth_args()
    run_tool(cmd)
    found = sorted(dest.parent.glob(dest.name + ".*"))
    if not found:
        raise CutError("yt-dlp 沒下載到任何東西（被擋、私人影片，或直播沒有 DVR？）")
    return found[0]


SINGLE_TS = re.compile(r"^\d+:\d{2}(?::\d{2})?$")
BAD_NAME = re.compile(r'[\\/:*?"<>|\s()\[\]#%&]+')  # Windows-illegal plus what breaks a Markdown link
BEFORE, AFTER, MERGE_GAP, MAX_GROUP_SPAN = 5, 25, 30, 180


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


def link(label, name, ext, ok):
    return f"[{label}](./{name}.{ext})" if ok else "（下載失敗）"


def render_index(title, rows):
    out = [f"# 待確認音檔：{title}", "",
           "點 ▶ 重聽，聽完告訴 Claude 結果；片段從「時間點前 5 秒」開始。", "",
           "| # | 時間點 | 逐字稿該行 | 逐字稿寫法 | 目前寫法／候選 | 重聽 | 片段內位置 | 截圖 |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['n']} | {fmt(r['at'])} | {cell(r['line'])} | {cell(r['heard'])} | {cell(r['expected'])} "
                   f"| {link('▶ 重聽', r['audio'], 'mp3', r['audio_ok'])} | 第 {r['offset']} 秒 "
                   f"| {link('截圖', r['name'], 'jpg', r['frame_ok'])} |")
    return "\n".join(out) + "\n"


def group_rows(rows):
    """Split time-sorted rows into groups. A row within MERGE_GAP seconds of the previous one joins its group (chained),
    unless that would stretch the group past MAX_GROUP_SPAN seconds."""
    groups = []
    for r in rows:
        if groups and r["at"] - groups[-1][-1]["at"] <= MERGE_GAP and r["at"] - groups[-1][0]["at"] <= MAX_GROUP_SPAN:
            groups[-1].append(r)
        else:
            groups.append([r])
    return groups


def cut_audio(url, start, end, mp3):
    """Default audio cutter: video window start-end (seconds) -> mono mp3."""
    with tempfile.TemporaryDirectory() as tmp:
        raw = download(url, start, end, "ba", Path(tmp) / "a")
        run_tool(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-b:a", "96k", str(mp3)])


def cut_frames(url, start, end, items):
    """Default screenshot cutter: download the video window once, then one 720p frame per (at, jpg) in `items`.
    Returns the list of `at` values whose frame failed; a failed download raises CutError."""
    failed = []
    with tempfile.TemporaryDirectory() as tmp:
        vid = download(url, start, end, VIDEO_FMT, Path(tmp) / "v")
        for at, jpg in items:
            try:
                run_tool(["ffmpeg", "-v", "error", "-y", "-ss", str(at - start), "-i", str(vid), "-frames:v", "1", str(jpg)])
            except CutError:
                failed.append(at)
    return failed


def attempt(fn, *args, warn, what):
    """Run one cutter; on CutError warn and return None so the other entries still go on, else its result."""
    try:
        return fn(*args) or []
    except CutError as e:
        warn(f"{what} failed: {e}")
        return None


def clear_old(out):
    """Remove the files a previous run wrote (numbering shifts as entries get confirmed, so old names go stale)."""
    if out.is_dir():
        for p in out.iterdir():
            if p.suffix in (".mp3", ".jpg") or p.name == "index.md":
                p.unlink()


def wait_confirm(folder, cut_audio=cut_audio, cut_frames=cut_frames,
                 warn=lambda m: print(f"WARNING: {m}", file=sys.stderr)):
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
    out = folder / "waitConfirm"
    clear_old(out)
    if not rows:
        warn("no suspected entry to cut")
        return []
    url = source_url(meta)
    out.mkdir(exist_ok=True)
    for group in group_rows(rows):
        start = window(group[0]["at"], BEFORE, AFTER)[0]
        end = group[-1]["at"] + AFTER
        audio_ok = attempt(cut_audio, url, start, end, out / f"{group[0]['name']}.mp3", warn=warn,
                           what=f"audio {fmt(start)}-{fmt(end)}") is not None
        fs, fe = max(0, group[0]["at"] - 1), group[-1]["at"] + 2
        failed = attempt(cut_frames, url, fs, fe, [(r["at"], out / f"{r['name']}.jpg") for r in group], warn=warn,
                         what=f"screenshots {fmt(fs)}-{fmt(fe)}")
        for r in group:
            r["audio"], r["offset"] = group[0]["name"], r["at"] - start
            r["audio_ok"] = audio_ok
            r["frame_ok"] = failed is not None and r["at"] not in failed
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
        if not rows:
            print("waitConfirm: 沒有可剪的項目（原因見上方警告），未產生 index.md", file=sys.stderr)
            return 1
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
        run_tool(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-b:a", "96k", str(mp3)])
        if args.frame:
            vid = download(url, start, end, VIDEO_FMT, Path(tmp) / "v")
            run_tool(["ffmpeg", "-v", "error", "-y", "-i", str(vid), "-vf", f"fps=1/{args.step}",
                      str(out / "frame_%02d.jpg")])

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
    try:
        sys.exit(main())
    except CutError as e:
        sys.exit(f"ERROR: {e}")
