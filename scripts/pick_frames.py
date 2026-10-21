#!/usr/bin/env python3
"""Pick one key frame per slide so each report section shows its point (.claude/skills/watch-archive/references/content.md 4a).

Scene-change frames often land mid-animation or on a transition (half-drawn slides, blank cards). This samples the
video once per second, scores every second inside each slide's time window (detail = how much is on screen,
stability = how little it changes from its neighbours, i.e. the animation has finished), and writes labelled
contact sheets so Claude can confirm or override the suggestion by eye. The chosen seconds are then grabbed at
1024px as frames/slide_NN.jpg and wired into meta.json slides + frames.json.

Usage:
  python3 scripts/pick_frames.py sheet <folder> --video <file> [--out <dir>]   # contact sheets + suggested seconds
  python3 scripts/pick_frames.py apply <folder> --video <file> --at "00:03,00:31,..."   # one time per slide
  python3 scripts/pick_frames.py text <folder> --video <file> --out <dir>   # full-res slides + what was said, for supplement.md

The video comes from `watch_archive.py --keep-media` (media/) or a yt-dlp download to the scratchpad; it is never
committed. A rerun of watch_archive.py wipes frames/, so apply again after a rerun.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_report import to_sec  # noqa: E402

THUMB_W = 216
CJK_FONTS = ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
             "C:/Windows/Fonts/msjh.ttc")


def label_font(size=16):
    """A CJK-capable font so slide titles are readable on the sheet; PIL's default font turns 中文 into boxes."""
    for f in CJK_FONTS:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def windows(starts, duration):
    """[start, end) seconds for each slide: from its start to the next slide's start (the last one to the end)."""
    s = [to_sec(t) for t in starts]
    return [(a, b) for a, b in zip(s, s[1:] + [int(duration) + 1])]


def scores(thumbs):
    """detail × stability² per second: rich, fully drawn and not mid-transition scores high."""
    gray = [Image.open(p).convert("L") for p in thumbs]
    detail = [ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).mean[0] for g in gray]
    out = []
    for i, g in enumerate(gray):
        diffs = [ImageStat.Stat(ImageChops.difference(g, gray[j])).mean[0] / 255
                 for j in (i - 1, i + 1) if 0 <= j < len(gray)]
        stability = 1 - max(diffs, default=0)
        out.append(detail[i] * stability ** 2)
    return out


def best_in_window(score, start, end, margin=2):
    """Highest-scoring second in [start, end); ties go to the later second (animations build up).

    The first `margin` seconds and the last second are skipped when the window is long enough: at a slide boundary
    the screen often still shows the previous slide or is mid-transition.
    """
    end = min(end, len(score))
    lo, hi = (start + margin, end - 1) if end - start >= margin + 4 else (start, end)
    rng = list(range(lo, hi))
    return max(rng, key=lambda i: (score[i], i)) if rng else start


def spoken_lines(transcript: str, start: int, end: int):
    """Transcript lines whose [mm:ss] falls in [start, end): what the speaker actually said while a slide was up."""
    out = []
    for line in transcript.splitlines():
        if line.startswith("[") and "]" in line:
            try:
                t = to_sec(line[1:line.index("]")])
            except ValueError:
                continue
            if start <= t < end:
                out.append(line)
    return out


def mmss(sec: int) -> str:
    return f"{sec // 60:02d}:{sec % 60:02d}"


def sample(video: Path, tmp: Path):
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps=1,scale={THUMB_W}:-2", str(tmp / "%04d.jpg")],
                   check=True)
    return sorted(tmp.glob("*.jpg"))  # file k (0-based) ≈ second k


def contact_sheet(thumbs, start, end, best, title, out: Path):
    sub = list(range(start, min(end, len(thumbs))))
    w, h = Image.open(thumbs[0]).size
    cols = min(8, max(1, len(sub)))
    rows = (len(sub) + cols - 1) // cols
    sheet = Image.new("RGB", (w * cols, h * rows + 28), "white")
    d = ImageDraw.Draw(sheet)
    d.text((6, 4), title, fill="black", font=label_font())
    for k, sec in enumerate(sub):
        x, y = (k % cols) * w, (k // cols) * h + 28
        sheet.paste(Image.open(thumbs[sec]), (x, y))
        color = "lime" if sec == best else "red"
        d.rectangle((x, y, x + 52, y + 18), fill=color)
        d.text((x + 3, y + 3), mmss(sec), fill="black")
        if sec == best:
            d.rectangle((x, y, x + w - 1, y + h - 1), outline="lime", width=4)
    sheet.save(out)


def register_slides(folder: Path, picks):
    """Point meta.json slides[i].frame at slide_NN.jpg and record them in frames.json (reason clean-slide)."""
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    frames = [f for f in json.loads((folder / "frames.json").read_text(encoding="utf-8")) if not f["file"].startswith("slide_")]
    for i, sec in enumerate(picks, 1):
        name = f"slide_{i:02d}.jpg"
        meta["slides"][i - 1]["frame"] = name
        frames.append({"file": name, "t": mmss(sec), "reason": "clean-slide"})
    for p, data in (("meta.json", meta), ("frames.json", frames)):
        (folder / p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sheet", "apply", "text"])
    ap.add_argument("folder")
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", help="where contact sheets go (default: a temp dir)")
    ap.add_argument("--at", help="apply: comma-separated MM:SS, one per slide in order")
    args = ap.parse_args()
    folder, video = Path(args.folder), Path(args.video)
    slides = json.loads((folder / "meta.json").read_text(encoding="utf-8")).get("slides", [])
    if not slides:
        sys.exit("meta.json has no slides yet: write slides (start/title/note) first, then pick frames")

    if args.mode == "text":
        # Claude reads these full-resolution frames (small code / prompt text is unreadable at report size) and compares
        # them with what was said; only what is on screen but NOT spoken goes into supplement.md.
        out = Path(args.out or tempfile.mkdtemp(prefix="screen_text_"))
        out.mkdir(parents=True, exist_ok=True)
        transcript = (folder / "transcript.md").read_text(encoding="utf-8")
        frames = {f["file"]: f["t"] for f in json.loads((folder / "frames.json").read_text(encoding="utf-8"))}
        duration = int(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                       str(video)], capture_output=True, text=True, check=True).stdout.strip().split(".")[0])
        for i, ((a, b), sl) in enumerate(zip(windows([s["start"] for s in slides], duration), slides), 1):
            t = frames.get(sl.get("frame", ""), sl["start"])
            img = out / f"slide_{i:02d}_full.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{to_sec(t)}.5", "-i", str(video), "-frames:v", "1",
                            str(img)], check=True)
            print(f"## {i:02d} {sl.get('title', '')}  [{mmss(a)}-{mmss(b)}]  screen at {t}: {img}")
            print("\n".join(spoken_lines(transcript, a, b)) or "(nothing said)")
            print()
        return

    if args.mode == "apply":
        picks = [to_sec(t.strip()) for t in (args.at or "").split(",") if t.strip()]
        if len(picks) != len(slides):
            sys.exit(f"--at has {len(picks)} times but meta.json has {len(slides)} slides")
        for i, sec in enumerate(picks, 1):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sec}.5", "-i", str(video), "-frames:v", "1",
                            "-vf", "scale=1024:-2", str(folder / "frames" / f"slide_{i:02d}.jpg")], check=True)
        register_slides(folder, picks)
        print(f"{len(picks)} slide frames written; now run build_report.py and look at the PDF")
        return

    out = Path(args.out or tempfile.mkdtemp(prefix="pick_frames_"))
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        thumbs = sample(video, Path(tmp))
        score = scores(thumbs)
        picks = []
        for i, ((a, b), sl) in enumerate(zip(windows([s["start"] for s in slides], len(thumbs)), slides), 1):
            best = best_in_window(score, a, b)
            picks.append(mmss(best))
            path = out / f"slide_{i:02d}.jpg"
            contact_sheet(thumbs, a, b, best, f"{i:02d} {sl.get('title', '')} [{mmss(a)}-{mmss(b)}] suggested {mmss(best)}", path)
            print(f"{i:02d} {mmss(a)}-{mmss(b)} suggested {mmss(best)}  sheet: {path}")
    print("suggested --at", ",".join(picks))


if __name__ == "__main__":
    main()
