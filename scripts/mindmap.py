#!/usr/bin/env python3
"""Mind map for a report: mindmap.md (indented bullet outline) -> mindmap.png (left-to-right tree, drawn with PIL).

Source of the outline, in order:
  1. mindmap.md written by Claude (step 4b; never overwritten): the first top-level item is the centre, its
     children are the branches, theirs the leaves (at most 3 levels are drawn). Several top-level items are
     taken as branches under the video title. Items may be '-', '*', '+', '•' or '1.' bullets.
  2. Otherwise generated from meta.json `slides` (centre = title, branches = slide titles, leaves = slide keywords;
     capped at MAX_BRANCHES / MAX_LEAVES / MAX_CHARS) and written to mindmap.md with AUTO_MARK on its first line,
     so a later rebuild regenerates it; delete that line to keep hand edits. The auto map cannot tag speaker claims
     （講者主張）; Claude still writes mindmap.md by hand.

Usage: python3 scripts/mindmap.py watch-output/<領域>/<資料夾>   (build_report.py calls ensure() itself)
"""
import functools
import re
import sys
from pathlib import Path

AUTO_TOKEN = "<!-- auto:"  # what marks a generated file; keep it stable, the wording after it may change
AUTO_MARK = AUTO_TOKEN + " 由 meta.json slides 自動產生；要手改請刪除這一行，重建報告就不會覆蓋 -->"
MAX_DEPTH, MAX_BRANCHES, MAX_LEAVES, MAX_CHARS = 3, 10, 3, 15
# Traditional-Chinese faces first; a .ttc collection is searched for its TC face (Noto's index 0 is Japanese)
CJK_FONTS = (
    "C:/Windows/Fonts/msjh.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/System/Library/Fonts/PingFang.ttc",
)
PALETTE = ("#2E86AB", "#E07A1F", "#3B9C5A", "#C0392B", "#8E44AD", "#16A085", "#B7950B", "#D35400", "#2C3E50", "#7F8C8D")
SIZES = (34, 26, 22)  # font px per depth
WRAP_PX = (300, 380, 420)  # max text width per depth before wrapping
PADS = (18, 12, 6)
GAP_X, GAP_Y, BRANCH_GAP = 60, 14, 14


# ---------- fonts (shared with pick_frames.py) ----------

@functools.lru_cache(maxsize=None)
def _font_face(path):
    """(path, index) of the Traditional-Chinese face in a font file, or index 0."""
    from PIL import ImageFont
    if path.lower().endswith(".ttc"):
        for i in range(12):
            try:
                family = " ".join(ImageFont.truetype(path, 12, index=i).getname())
            except OSError:
                break
            if re.search(r"\bTC\b|JhengHei", family):
                return i
    return 0


def find_font():
    for p in CJK_FONTS:
        if Path(p).exists():
            return p
    return None


@functools.lru_cache(maxsize=None)
def cjk_font(size):
    """A CJK-capable font (cached per size); PIL's default font turns 中文 into boxes."""
    from PIL import ImageFont
    fp = find_font()
    if not fp:
        return ImageFont.load_default()
    return ImageFont.truetype(fp, size, index=_font_face(fp))


# ---------- outline ----------

ITEM_RE = re.compile(r"^(\s*)(?:[-*+•]|\d+[.)、])\s+(.*\S)\s*$")


def parse_outline(md: str, fallback_root: str = ""):
    """Indented bullets -> (text, [children]); headings and other lines are ignored. None when there are no items."""
    root = ("", [])
    stack = [(-1, root)]
    for line in md.splitlines():
        m = ITEM_RE.match(line)
        if not m:
            continue
        indent = len(m.group(1).expandtabs(2))
        while stack[-1][0] >= indent:
            stack.pop()
        node = (m.group(2), [])
        stack[-1][1][1].append(node)
        stack.append((indent, node))
    tops = root[1]
    if not tops:
        return None
    return tops[0] if len(tops) == 1 else (fallback_root or "主題", tops)


def clip(text, n=MAX_CHARS):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text if len(text) <= n else text[:n - 1] + "…"


def from_slides(meta):
    """Fallback outline from slides, kept inside the map limits: slides are grouped into at most MAX_BRANCHES branches."""
    slides = [s for s in (meta.get("slides") or []) if isinstance(s, dict)]
    if not slides:
        return None
    per = -(-len(slides) // MAX_BRANCHES)  # ceil
    branches = []
    for g in range(0, len(slides), per):
        group = slides[g:g + per]
        first = group[0]
        title = clip(first.get("title") or first.get("start") or "")
        if len(group) == 1:
            kws = first.get("keywords") if isinstance(first.get("keywords"), list) else []
            leaves = [clip(k) for k in kws if str(k or "").strip()]
        else:  # merged slides: the other slide titles become the leaves
            title = clip(title, MAX_CHARS - 5) + f"（{len(group)} 段）"
            leaves = [clip(s.get("title") or s.get("start") or "") for s in group[1:]]
        branches.append((title, [(l, []) for l in leaves[:MAX_LEAVES]]))
    return (clip(meta.get("title") or "主題", 30), branches)


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
    """Hand-written mindmap.md wins; an auto one (or none) is regenerated from slides. A hand-written file with no
    items falls back to slides with a warning, and is left as it is."""
    path = dest / "mindmap.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if not text.lstrip().startswith(AUTO_TOKEN):
            tree = parse_outline(text, meta.get("title", ""))
            if tree:
                return tree
            print("WARNING: mindmap.md has no list items ('- 項目'); drawing the map from slides instead", file=sys.stderr)
            return from_slides(meta)
    tree = from_slides(meta)
    if tree:
        path.write_text(outline_md(tree, auto=True), encoding="utf-8")
    elif path.exists():
        path.unlink()  # stale auto outline, no slides any more
    return tree


# ---------- drawing ----------

def wrap(text, max_px, font, measure):
    """Break text into lines no wider than max_px: Latin words stay whole, CJK may break between any characters."""
    lines, cur = [], ""
    for tok in re.findall(r"[A-Za-z0-9_.,:;'’&+/#%$@!?()\-]+|\s+|.", str(text)):
        if measure(cur + tok, font) <= max_px:
            cur += tok
            continue
        if cur.strip():
            lines.append(cur.rstrip())
        cur = tok.lstrip()
        while measure(cur, font) > max_px:  # a word longer than a whole line: cut it
            i = max(j for j in range(1, len(cur) + 1) if j == 1 or measure(cur[:j], font) <= max_px)
            lines.append(cur[:i])
            cur = cur[i:]
    if cur.strip() or not lines:
        lines.append(cur.rstrip())
    return lines


def layout(tree, measure):
    """Nodes with x/y (y = top) so that no subtree overlaps another: each subtree is as tall as the larger of its
    own box and its stacked children, and its box is centred within that span."""
    def build(node, d):
        f = cjk_font(SIZES[d])
        lines = wrap(node[0], WRAP_PX[d], f, measure)
        lh = SIZES[d] + 8
        n = {"d": d, "lines": lines, "lh": lh, "pad": PADS[d], "font": f,
             "w": int(max(measure(l, f) for l in lines) + 2 * PADS[d]), "h": int(lh * len(lines) + 2 * PADS[d]),
             "kids": [build(c, d + 1) for c in node[1]] if d + 1 < MAX_DEPTH else []}
        gap = BRANCH_GAP + GAP_Y if d == 0 else GAP_Y
        kids_h = sum(k["span"] for k in n["kids"]) + gap * max(0, len(n["kids"]) - 1)
        n["span"] = max(n["h"], kids_h)
        n["kids_h"], n["gap"] = kids_h, gap
        return n

    root = build(tree, 0)
    col_w = {}

    def widths(n):
        col_w[n["d"]] = max(col_w.get(n["d"], 0), n["w"])
        for k in n["kids"]:
            widths(k)
    widths(root)
    xs = [30]
    for d in range(1, max(col_w) + 1):
        xs.append(xs[-1] + col_w[d - 1] + GAP_X)

    nodes = []

    def place(n, top, branch):
        n["branch"], n["x"] = branch, xs[n["d"]]
        n["y"] = top + (n["span"] - n["h"]) / 2
        y = top + (n["span"] - n["kids_h"]) / 2
        for i, k in enumerate(n["kids"]):
            place(k, y, i if n["d"] == 0 else branch)
            y += k["span"] + n["gap"]
        nodes.append(n)

    place(root, 30, 0)
    size = (int(xs[max(col_w)] + col_w[max(col_w)] + 30), int(root["span"] + 60))
    return nodes, size


def render(tree, out: Path):
    """Left-to-right tree: centre box on the left, coloured branch boxes, leaf text with an underline."""
    from PIL import Image, ImageDraw
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    nodes, (W, H) = layout(tree, lambda s, f: probe.textlength(s, font=f))
    img = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(img)

    def color(n):
        return "#34495E" if n["d"] == 0 else PALETTE[n["branch"] % len(PALETTE)]

    def anchor_in(k):  # where a connector reaches a node: box middle, or a leaf's underline
        return k["y"] + (k["h"] - 4 if k["d"] == 2 else k["h"] / 2)

    for n in nodes:  # connectors first, boxes on top
        for k in n["kids"]:
            x0, y0 = n["x"] + n["w"], n["y"] + n["h"] / 2
            x1, y1 = k["x"], anchor_in(k)
            pts = [(x0 + (x1 - x0) * t, y0 + (y1 - y0) * (3 * t * t - 2 * t ** 3)) for t in [i / 24 for i in range(25)]]
            dr.line(pts, fill=color(k), width=4 if k["d"] == 1 else 2)
    for n in nodes:
        x, y, w, h, c = n["x"], n["y"], n["w"], n["h"], color(n)
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
            dr.text((x + n["pad"], y + n["pad"] + i * n["lh"]), line, font=n["font"], fill=fg)
    img.save(out)
    return out


def ensure(dest: Path, meta):
    """Write mindmap.png (and an auto mindmap.md when there is no hand-written one). Returns the png path or None."""
    png = dest / "mindmap.png"
    tree = load_tree(dest, meta)
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
