#!/usr/bin/env python3
"""Run the watch skill and archive the result into watch-output/.

Folder name: <date>_<platform>_<title>__<video-id>
A folder whose name ends with __<video-id> is reused (updated in place), so one
video always maps to exactly one folder.

Outputs per video: meta.json, transcript.md (Traditional; transcript.raw.md if converted), summary.md, frames/, <stem>_report.md, <stem>_report.docx, media/<stem>_video.<ext> (--keep-media)
where <stem> = <date>_<platform>_<title 20 chars>__<video-id>

Usage:
  python3 scripts/watch_archive.py URL [--question Q] [--whisper groq] [--detail balanced] [--keep-media]
"""
import argparse
import build_report
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
WATCH = ROOT / ".claude/skills/watch/scripts/watch.py"
OUT_ROOT = ROOT / "watch-output"
TITLE_MAX = 40
NAME_MAX = 120


def platform_and_id(url: str):
    u = urlparse(url)
    host = u.netloc.lower()
    parts = [p for p in u.path.split("/") if p]
    if "youtu.be" in host and parts:
        return "YouTube", parts[0]
    if "youtube.com" in host:
        if "v" in parse_qs(u.query):
            return "YouTube", parse_qs(u.query)["v"][0]
        if len(parts) >= 2 and parts[0] in ("shorts", "embed", "live"):
            return "YouTube", parts[1]
    if "facebook.com" in host or "fb.watch" in host:
        if "v" in parse_qs(u.query):
            return "Facebook", parse_qs(u.query)["v"][0]
        for key in ("v", "videos", "reel"):
            if key in parts and parts.index(key) + 1 < len(parts):
                return "Facebook", parts[parts.index(key) + 1]
        if parts:
            return "Facebook", parts[-1]
    name = host.removeprefix("www.").split(".")[0].capitalize() or "Web"
    return name, (parts[-1] if parts else re.sub(r"\W+", "", host))


try:
    from opencc import OpenCC
    _S2T = OpenCC("s2twp")  # Simplified -> Traditional (Taiwan standard + common phrases)
except ImportError:  # pip install opencc-python-reimplemented
    _S2T = None


def to_traditional(text: str) -> str:
    """Convert Simplified Chinese to Traditional (zh-TW). No-op for other languages."""
    return _S2T.convert(text) if _S2T else text


def tidy_title(raw: str, uploader: str = "") -> str:
    """Drop Facebook noise: '86K views · 1.3K reactions |' prefix, '| <uploader>' suffix, #hashtags."""
    parts = [p.strip() for p in raw.split("|")]
    parts = [p for p in parts if p and not re.search(r"\b(views?|reactions?|likes?)\b", p, re.I) and p != uploader]
    t = re.sub(r"#\S+", "", parts[0] if parts else raw).strip()
    return t or raw.strip()


def hashtags(raw: str):
    return list(dict.fromkeys(re.findall(r"#([^\s#|]+)", raw)))


def clean_title(title: str) -> str:
    t = re.sub(r'[\\/:*?"<>|]', "", title)
    t = re.sub(r"[\s｜，。！？、；：,.!?;（）()\[\]【】「」『』]+", "-", t).strip("-")
    t = t[:TITLE_MAX].strip("-")
    return t or "untitled"


def safe_id(vid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "", vid) or "unknown"


def field(report: str, label: str) -> str:
    m = re.search(rf"^- \*\*{re.escape(label)}:\*\*\s*(.+)$", report, re.M)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--question", default="請摘要影片內容並附時間戳")
    ap.add_argument("--whisper", default="groq")
    ap.add_argument("--detail", default="balanced")
    ap.add_argument("--keep-media", action="store_true", help="also keep the full video in media/ (local only, gitignored)")
    args = ap.parse_args()

    platform, raw_id = platform_and_id(args.url)
    vid = safe_id(raw_id)

    work = Path(tempfile.mkdtemp(prefix="watch-archive-"))
    proc = subprocess.run(
        [sys.executable, str(WATCH), args.url, "--question", args.question,
         "--whisper", args.whisper, "--detail", args.detail, "--out-dir", str(work)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print(f"watch.py failed (exit {proc.returncode}):\n{proc.stderr[-2000:]}", file=sys.stderr)
        sys.exit(proc.returncode)
    report = proc.stdout

    title_raw = field(report, "Title") or "untitled"
    title = tidy_title(title_raw, field(report, "Uploader"))
    tm = re.search(r"## Transcript\s*\n(.*?)(?:\n---\n_Work dir|\Z)", report, re.S)
    transcript_raw = tm.group(1).strip() if tm else ""
    transcript = to_traditional(transcript_raw)
    title = to_traditional(title)
    if _S2T is None:
        print("WARNING: opencc not installed; transcript left as-is (pip install opencc-python-reimplemented)", file=sys.stderr)
    src_m = re.search(r"_Source:\s*(.+?)\._", transcript)
    transcript_source = src_m.group(1) if src_m else "unknown"

    frames = []
    for m in re.finditer(r"^- `([^`]+)` \(t=([\d:]+), reason=([^)]*)\)", report, re.M):
        frames.append({"src": m.group(1), "t": m.group(2), "reason": m.group(3)})

    # Reuse an existing folder for the same video ID; otherwise create a new one.
    OUT_ROOT.mkdir(exist_ok=True)
    existing = sorted(OUT_ROOT.glob(f"*__{vid}"))
    if existing:
        dest = existing[0]
        # keep the original date prefix but follow title changes (e.g. Simplified -> Traditional)
        renamed = OUT_ROOT / f"{dest.name.split('_')[0]}_{platform}_{clean_title(title)}__{vid}"[:NAME_MAX]
        if renamed != dest and not renamed.exists():
            dest = dest.rename(renamed)
    else:
        name = f"{dt.date.today():%Y-%m-%d}_{platform}_{clean_title(title)}__{vid}"
        dest = OUT_ROOT / name[:NAME_MAX]
    dest.mkdir(exist_ok=True)

    prev = json.loads((dest / "meta.json").read_text(encoding="utf-8")) if (dest / "meta.json").exists() else {}
    meta = {
        "url": args.url,
        "platform": platform,
        "video_id": vid,
        "title": title,
        "title_raw": title_raw,
        "source_hashtags": hashtags(title_raw),
        "uploader": to_traditional(field(report, "Uploader")),
        "duration": field(report, "Duration"),
        "detail": args.detail,
        "transcript_source": transcript_source,
        "question": args.question,
        "first_archived": prev.get("first_archived", dt.date.today().isoformat()),
        "last_updated": dt.date.today().isoformat(),
        "known_asr_errors": prev.get("known_asr_errors", []),  # hand-curated: never overwrite
        "keywords": prev.get("keywords", []),  # hand-curated: never overwrite
        "section_keywords": prev.get("section_keywords", {}),  # keyed by frame start time
    }
    (dest / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (dest / "transcript.md").write_text(f"# {title}\n\n{transcript}\n", encoding="utf-8")
    raw_path = dest / "transcript.raw.md"  # untouched ASR output, kept only if conversion changed it
    if transcript_raw != transcript:
        raw_path.write_text(f"# {title_raw}\n\n{transcript_raw}\n", encoding="utf-8")
    else:
        raw_path.unlink(missing_ok=True)
    # summary.md is written by the agent/user after reading the transcript; keep any existing one.
    if not (dest / "summary.md").exists():
        (dest / "summary.md").write_text(f"# 摘要：{title}\n\n_待補：請依逐字稿撰寫含時間戳的摘要。_\n", encoding="utf-8")

    # Frames are small (~25 KB each) and make the report readable: always keep them.
    fdir = dest / "frames"
    if fdir.exists():
        shutil.rmtree(fdir)
    fdir.mkdir()
    saved = []
    for f in frames:
        src = Path(f["src"])
        if src.exists():
            shutil.copy2(src, fdir / src.name)
            saved.append({"file": src.name, "t": f["t"], "reason": f["reason"]})
    (dest / "frames.json").write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # The full video is large: only with --keep-media (gitignored).
    if args.keep_media:
        media = dest / "media"
        if media.exists():
            shutil.rmtree(media)
        media.mkdir()
        for p in work.rglob("video.*"):
            shutil.move(str(p), media / f"{build_report.file_stem(dest)}_video{p.suffix}")
            break
    shutil.rmtree(work, ignore_errors=True)

    build_report.build(dest)

    update_index(dest, meta)
    print(f"archived -> {dest.relative_to(ROOT)}")


def update_index(dest: Path, meta: dict):
    idx = OUT_ROOT / "index.md"
    header = ("# watch-output 索引\n\n"
              "| 日期 | 平台 | 標題 | 長度 | 轉錄來源 | 資料夾 |\n|---|---|---|---|---|---|\n")
    rows = []
    if idx.exists():
        rows = [l for l in idx.read_text(encoding="utf-8").splitlines()
                if l.startswith("| ") and not l.startswith("| 日期") and f"__{meta['video_id']}/" not in l]
    safe_title = meta["title"].replace("|", "｜")
    rows.append(f"| {meta['last_updated']} | {meta['platform']} | {safe_title} | {meta['duration']} | "
                f"{meta['transcript_source']} | [開啟](./{dest.name}/) |")
    idx.write_text(header + "\n".join(sorted(rows)) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
