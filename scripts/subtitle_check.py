#!/usr/bin/env python3
"""針對第二輪校稿留下的疑問項目，用「畫面燒入字幕」核對（.claude/skills/watch-archive/references/proofread.md 3b）。

不是整支影片 OCR：只讀 meta.json `known_asr_errors` 裡 status 為 suspected 且有時間點的項目，每項取該秒前後幾秒的
原始解析度截圖、只裁字幕帶並放大、拼成一張圖，印出該處逐字稿上下文；Claude 用 Read 看圖判斷（字幕太小或太糊時才加 --ocr）。

字幕只用來確認用字、專有名詞與數字：它常是書面語、簡體、甚至翻譯字幕，不整句覆蓋逐字稿；確認後把該項改成
status "confirmed"，說明寫「來源：畫面字幕 MM:SS」，簡體字幕轉成繁體再用。

Usage:
  python3 scripts/subtitle_check.py <資料夾> [--video <檔>] [--out <目錄>] [--pad 3] [--band 0.55:1.0] [--ocr]
                                    [--only "03:03,04:31"] [--at "03:16"]

影片來源順序：--video → <資料夾>/media/ 的影片 → 用 yt-dlp 依 meta.json 的 url 下載到 --out（暫存區，不入庫）。
下載失敗不會中斷：改用 frames/ 的縮圖拼圖（標「低信心」），並把清單與時間點印出來，請使用者自己聽／看。
沒有時間點的項目（例如「全片」）只列出，不處理。
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_report import to_sec  # noqa: E402

TIME_RE = re.compile(r"\d{1,2}:\d{2}(?::\d{2})?")
LINE_RE = re.compile(r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s?(.*)$")
VIDEO_EXT = (".mp4", ".mkv", ".webm", ".mov", ".m4v")


def clock(sec: int) -> str:
    sec = max(int(sec), 0)
    return f"{sec // 60:02d}:{sec % 60:02d}"


def suspected_items(meta: dict, only=None):
    items, untimed = [], []
    for e in meta.get("known_asr_errors", []):
        if e.get("status") != "suspected":
            continue
        times = TIME_RE.findall(e.get("time", ""))
        if only:
            times = [t for t in times if clock(to_sec(t)) in only]
        if times:
            items.append((e, times[0]))  # 區間或多個時間點：取第一個
        elif not only:
            untimed.append(e)
    return items, untimed


def find_video(folder: Path, meta: dict, explicit, out: Path):
    if explicit:
        return Path(explicit)
    media = folder / "media"
    if media.is_dir():
        for p in sorted(media.iterdir()):
            if p.suffix.lower() in VIDEO_EXT:
                return p
    url = meta.get("url", "")
    if not url:
        return None
    target = out / "video.%(ext)s"
    r = subprocess.run(["yt-dlp", "-q", "-f", "best[height<=720]/best", "-o", str(target), url], capture_output=True, text=True)
    got = [p for p in out.glob("video.*") if p.suffix.lower() in VIDEO_EXT]
    if r.returncode != 0 or not got:
        print(f"WARNING: 下載影片失敗（{(r.stderr or r.stdout).strip().splitlines()[-1:] or ['?']}）", file=sys.stderr)
        return None
    return got[0]


def grab(video: Path, sec: int, dest: Path) -> bool:
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(max(sec, 0)), "-i", str(video), "-frames:v", "1", str(dest)],
                       capture_output=True)
    return r.returncode == 0 and dest.exists()


def crop_band(img: Image.Image, y0: float, y1: float) -> Image.Image:
    w, h = img.size
    band = img.crop((0, int(h * y0), w, int(h * y1)))
    if band.width < 900:  # 窄的直式影片放大，字才看得清
        k = 900 / band.width
        band = band.resize((int(band.width * k), int(band.height * k)))
    return band


def transcript_context(folder: Path, sec: int, span: int = 2):
    p = folder / "transcript.md"
    if not p.exists():
        return []
    rows = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(raw.strip())
        if m:
            rows.append((to_sec(m.group(1)), raw.strip()))
    idx = min(range(len(rows)), key=lambda i: abs(rows[i][0] - sec)) if rows else 0
    return [r[1] for r in rows[max(idx - span, 0): idx + span + 1]]


def make_sheet(frames, labels, dest: Path):
    cell_w = max(f.width for f in frames)
    rows = []
    for f, lab in zip(frames, labels):
        im = Image.new("RGB", (cell_w, f.height + 18), "black")
        im.paste(f, (0, 18))
        ImageDraw.Draw(im).text((4, 3), lab, fill="yellow")
        rows.append(im)
    sheet = Image.new("RGB", (cell_w, sum(r.height for r in rows)), "black")
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(dest, quality=88)


def low_res_sheet(folder: Path, sec: int, dest: Path, band):
    """沒有影片檔時：從 frames/ 取離該秒最近的幾張縮圖（低信心）。"""
    fj = folder / "frames.json"
    if not fj.exists():
        return False
    info = json.loads(fj.read_text(encoding="utf-8"))
    near = sorted(info, key=lambda f: abs(to_sec(f["t"]) - sec))[:3]
    ims, labs = [], []
    for f in sorted(near, key=lambda f: to_sec(f["t"])):
        p = folder / "frames" / f["file"]
        if p.exists():
            ims.append(crop_band(Image.open(p).convert("RGB"), *band))
            labs.append(f"{f['t']}（縮圖，低信心）")
    if not ims:
        return False
    make_sheet(ims, labs, dest)
    return True


def ocr_text(paths):
    from subtitle_ocr import load_ocr, read_text
    engine = load_ocr("v5")
    out = []
    for p in paths:
        try:
            t = read_text(engine, str(p)).strip()
        except Exception as exc:  # OCR 失敗不中斷
            t = f"(OCR 失敗：{exc})"
        if t and t not in out:
            out.append(t)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--video")
    ap.add_argument("--out")
    ap.add_argument("--pad", type=int, default=3, help="前後各取幾秒（每秒一張）")
    ap.add_argument("--band", default="0.55:1.0", help="字幕帶在畫面高度的範圍 y0:y1（預設下方 45%%）")
    ap.add_argument("--ocr", action="store_true", help="另外 OCR 這些字幕帶（PP-OCRv5；第一次會下載模型）")
    ap.add_argument("--only", default="", help="只處理這些時間點，例如 03:03,04:31")
    ap.add_argument("--at", default="", help="不看 known_asr_errors，直接檢查這些時間點，例如 03:16,05:20（例如前後秒數沒有字幕時往後多看）")
    args = ap.parse_args()

    folder = Path(args.folder)
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    y0, y1 = (float(x) for x in args.band.split(":"))
    only = {clock(to_sec(t)) for t in args.only.split(",") if t.strip()} if args.only else None
    items, untimed = suspected_items(meta, only)
    if args.at:
        items = [({"heard": "", "expected": "（手動指定時間點）"}, clock(to_sec(t))) for t in args.at.split(",") if t.strip()]
        untimed = []
    if not items and not untimed:
        print("沒有 status 為 suspected 的疑問項目，不需要字幕核對。")
        return
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="subcheck_"))
    out.mkdir(parents=True, exist_ok=True)
    video = find_video(folder, meta, args.video, out) if items else None
    mode = f"影片 {video.name}" if video else "frames/ 縮圖（低信心）"
    print(f"字幕核對：{len(items)} 項有時間點、{len(untimed)} 項無時間點；來源：{mode}；輸出：{out}")

    for n, (e, t) in enumerate(items, 1):
        sec = to_sec(t)
        dest = out / f"item_{n:02d}_{clock(sec).replace(':', '')}.jpg"
        ok = False
        paths = []
        if video:
            ims, labs = [], []
            for s in range(max(sec - args.pad, 0), sec + args.pad + 1):
                fp = out / f"raw_{n:02d}_{s}.jpg"
                if grab(video, s, fp):
                    paths.append(fp)
                    ims.append(crop_band(Image.open(fp).convert("RGB"), y0, y1))
                    labs.append(clock(s) + ("  ← 疑問處" if s == sec else ""))
            if ims:
                make_sheet(ims, labs, dest)
                ok = True
        if not ok:
            ok = low_res_sheet(folder, sec, dest, (y0, y1))
        print(f"\n[{n}] {clock(sec)}  逐字稿：「{e.get('heard', '')}」 → 推測：「{e.get('expected', '')}」")
        for line in transcript_context(folder, sec):
            print(f"      {line}")
        print(f"      字幕帶截圖：{dest if ok else '（無法產生）'}")
        if args.ocr and paths:
            for txt in ocr_text(paths):
                print(f"      OCR：{txt}")
    if untimed:
        print("\n無時間點，未處理（請另行確認）：")
        for e in untimed:
            print(f"  - {e.get('time', '?')}：「{e.get('heard', '')}」→ {e.get('expected', '')}")
    print("\n下一步：用 Read 看各 item_*.jpg；能確認的把 known_asr_errors 該項改 confirmed、說明加「來源：畫面字幕 MM:SS」，"
          "字幕只確認用字、不整句覆蓋；剩下的列給使用者確認。")


if __name__ == "__main__":
    main()
