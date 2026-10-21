#!/usr/bin/env python3
"""Mind map for a report: mindmap.md (indented bullet outline) -> mindmap.png (left-to-right tree, drawn with PIL).

Source of the outline, in order:
  1. mindmap.md written by Claude (step 4b; never overwritten): the first top-level bullet is the centre, its
     children are the branches, theirs the leaves (at most 3 levels are drawn). Several top-level bullets are
     taken as branches under the video title.
  2. Otherwise generated from meta.json `slides` (centre = title, branches = slide titles, leaves = slide keywords)
     and written to mindmap.md with AUTO_MARK on its first line, so a later rebuild regenerates it; delete that
     line to keep hand edits.

Usage: python3 scripts/mindmap.py watch-output/<領域>/<資料夾>   (build_report.py calls ensure() itself)
"""
import re
import sys
from pathlib import Path

AUTO_MARK = "<!-- auto: 由 meta.json slides 自動產生；要手改請刪除這一行，重建報告就不會覆蓋 -->"
MAX_DEPTH = 3
FONT_CANDIDATES = (
    "C:/Windows/Fonts/msjh.ttc", "C:/Windows/Fonts/msjhbd.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/System/Library/Fonts/PingFang.ttc",
)
PALETTE = ("#2E86AB", "#E07A1F", "#3B9C5A", "#C0392B", "#8E44AD", "#16A085", "#B7950B", "#D35400", "#2C3E50", "#7F8C8D")


def parse_outline(md: str, fallback_root: str = ""):
    """Indented '- ' bullets -> (text, [children]). Lines that are not bullets (headings, comments) are ignored."""
    items = []
    for line in md.splitlines():
        m = re.match(r"^(\s*)[-*+]\s+(.*\S)\s*$", line)
        if m:
            items.append((len(m.group(1).expandtabs(2)), m.group(2)))
    root = ("", [])
    stack = [(-1, root)]
    for indent, text in items:
        while stack[-1][0] >= indent:
            stack.pop()
        node = (text, [])
        stack[-1][1][1].append(node)
        stack.append((indent, node))
    tops = root[1]
    if not tops:
        return None
    if len(tops) == 1:
        return tops[0]
    return (fallback_root or "主題", tops)


def from_slides(meta):
    slides = meta.get("slides") or []
    if not slides:
        return None
    branches = [(s.get("title") or s.get("start", ""), [(k, []) for k in s.get("keywords", [])]) for s in slides]
    return (meta.get("title", "主題"), branches)


def outline_md(tree, auto=False) -> str:
    L = [AUTO_MARK] if auto else []
    L += ["# 思維導圖", ""]

    def walk(node, depth):
        L.append("  " * depth + "- " + node[0])
        for c in node[1]:
            walk(c, depth + 1)
    walk(tree, 0)
    return "\n".join(L) + "\n"


def load_tree(dest: Path, meta):
    """(tree, wrote_auto). Hand-written mindmap.md wins; an auto one (or none) is regenerated from slides."""
    path = dest / "mindmap.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if not text.lstrip().startswith(AUTO_MARK):
            return parse_outline(text, meta.get("title", "")), False
    tree = from_slides(meta)
    if tree:
        path.write_text(outline_md(tree, auto=True), encoding="utf-8")
    elif path.exists():
        path.unlink()  # stale auto outline, no slides any more
    return tree, bool(tree)


def find_font():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    return None


def wrap(text, n):
    return [text[i:i + n] for i in range(0, len(text), n)] or [""]


def render(tree, out: Path):
    """Left-to-right tree: centre box on the left, coloured branch boxes, leaf text with an underline."""
    from PIL import Image, ImageDraw, ImageFont
    fp = find_font()
    sizes = (34, 26, 22)

    def font(d):
        return ImageFont.truetype(fp, sizes[min(d, 2)]) if fp else ImageFont.load_default()
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    def box(text, d):
        lines = wrap(text, (8, 14, 16)[min(d, 2)])
        f = font(d)
        w = max(probe.textlength(l, font=f) for l in lines)
        lh = sizes[min(d, 2)] + 8
        pad = (18, 12, 6)[min(d, 2)]
        return lines, int(w + 2 * pad), int(lh * len(lines) + 2 * pad), pad, lh

    # layout: each node gets (x, y-centre); leaves stacked top to bottom, parents centred on their children
    nodes = []
    gap_x, gap_y = 60, 14
    col_w = {}

    def measure(node, d):
        lines, w, h, pad, lh = box(node[0], d)
        col_w[d] = max(col_w.get(d, 0), w)
        kids = [measure(c, d + 1) for c in node[1]] if d + 1 < MAX_DEPTH else []
        return {"text": node[0], "d": d, "lines": lines, "w": w, "h": h, "pad": pad, "lh": lh, "kids": kids}

    root = measure(tree, 0)
    y_cursor = [30]

    def place(n, branch):
        n["branch"] = branch
        if n["kids"]:
            for i, k in enumerate(n["kids"]):
                place(k, i if n["d"] == 0 else branch)
            top, bot = n["kids"][0]["y"], n["kids"][-1]["y"]
            n["y"] = (top + bot) / 2
            span = n["kids"][-1]["y"] + n["kids"][-1]["h"] / 2 - (n["kids"][0]["y"] - n["kids"][0]["h"] / 2)
            if span < n["h"]:  # parent taller than its children: push the cursor down
                y_cursor[0] = max(y_cursor[0], n["y"] + n["h"] / 2 + gap_y)
        else:
            n["y"] = y_cursor[0] + n["h"] / 2
            y_cursor[0] += n["h"] + gap_y
        if n["d"] == 1:
            y_cursor[0] += gap_y  # extra space between branches
        nodes.append(n)

    place(root, 0)
    xs = [30]
    for d in range(1, MAX_DEPTH):
        xs.append(xs[-1] + col_w.get(d - 1, 0) + gap_x)
    deepest = max(col_w)
    W = int(xs[deepest] + col_w[deepest] + 30)
    H = int(y_cursor[0] + 20)
    img = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(img)

    def color(n):
        return "#34495E" if n["d"] == 0 else PALETTE[n["branch"] % len(PALETTE)]

    for n in nodes:
        n["x"] = xs[n["d"]]
    for n in nodes:  # connectors first, boxes on top
        for k in n["kids"]:
            x0, y0 = n["x"] + n["w"], n["y"]
            x1, y1 = k["x"], k["y"] + (k["h"] / 2 - 4 if k["d"] == 2 else 0)
            pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * (3 * t * t - 2 * t ** 3)) for t in [i / 24 for i in range(25)]]
            dr.line(pts, fill=color(k), width=4 if k["d"] == 1 else 2)
    for n in nodes:
        x, y, w, h, c = n["x"], n["y"] - n["h"] / 2, n["w"], n["h"], color(n)
        f = font(n["d"])
        if n["d"] == 0:
            dr.rounded_rectangle([x, y, x + w, y + h], radius=16, fill=c)
            fg = "white"
        elif n["d"] == 1:
            dr.rounded_rectangle([x, y, x + w, y + h], radius=12, fill="white", outline=c, width=3)
            fg = c
        else:
            dr.line([(x, y + h - 4), (x + w, y + h - 4)], fill=c, width=2)
            fg = "#222222"
        for i, line in enumerate(n["lines"]):
            dr.text((x + n["pad"], y + n["pad"] + i * n["lh"]), line, font=f, fill=fg)
    img.save(out)
    return out


def ensure(dest: Path, meta):
    """Write mindmap.png (and an auto mindmap.md when there is no hand-written one). Returns the png path or None."""
    png = dest / "mindmap.png"
    tree, _ = load_tree(dest, meta)
    if not tree:
        png.unlink(missing_ok=True)
        return None
    if not find_font():
        print("WARNING: no CJK font found; mindmap.png text may show as boxes", file=sys.stderr)
    return render(tree, png)


if __name__ == "__main__":
    import json
    d = Path(sys.argv[1])
    print("wrote", ensure(d, json.loads((d / "meta.json").read_text(encoding="utf-8"))))
