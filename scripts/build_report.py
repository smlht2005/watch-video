#!/usr/bin/env python3
"""Build a readable report (<stem>_report.md + <stem>_report.docx) from an archived watch folder.

Reads  : meta.json, summary.md, transcript.md, frames.json, frames/*.jpg
Writes : <stem>_report.md   (frames interleaved with the transcript)
         <stem>_report.docx (same content as a Word document)

Usage: python3 scripts/build_report.py watch-output/<folder>
"""
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

CJK_FONT = "Microsoft JhengHei"
SEG_RE = re.compile(r"^\[(\d+:\d+(?::\d+)?)\]\s*(.*)$")


def file_stem(dest: Path) -> str:
    """<date>_<platform>_<title (<=20 chars)>__<video-id>, derived from the folder name."""
    head, _, vid = dest.name.rpartition("__")
    date, platform, title = (head.split("_", 2) + ["", ""])[:3]
    return f"{date}_{platform}_{title[:20].rstrip('-')}__{vid}"


def to_sec(ts: str) -> int:
    n = [int(x) for x in ts.split(":")]
    while len(n) < 3:
        n.insert(0, 0)
    return n[0] * 3600 + n[1] * 60 + n[2]


def load(dest: Path):
    meta = json.loads((dest / "meta.json").read_text(encoding="utf-8"))
    summary = (dest / "summary.md").read_text(encoding="utf-8")
    segs = []
    for line in (dest / "transcript.md").read_text(encoding="utf-8").splitlines():
        m = SEG_RE.match(line.strip())
        if m:
            segs.append((m.group(1), m.group(2)))
    fpath = dest / "frames.json"
    frames = json.loads(fpath.read_text(encoding="utf-8")) if fpath.exists() else []
    return meta, summary, segs, frames


def sections(segs, frames):
    """Group transcript segments under the frame whose time window contains them."""
    if not frames:
        return [(None, segs)]
    frames = sorted(frames, key=lambda f: to_sec(f["t"]))
    out = [(f, []) for f in frames]
    for ts, text in segs:
        s = to_sec(ts)
        idx = 0
        for i, f in enumerate(frames):  # first frame among those sharing the latest start time
            if to_sec(f["t"]) <= s and to_sec(f["t"]) > to_sec(frames[idx]["t"]) or i == 0:
                idx = i
        out[idx][1].append((ts, text))
    return out


def strip_h1(md: str) -> str:
    return re.sub(r"\A# .*\n+", "", md)


def build_md(dest: Path, meta, summary, segs, frames) -> str:
    L = [f"# {meta['title']}", ""]
    L += [f"- 來源：{meta['url']}",
          f"- 平台 / 上傳者：{meta['platform']} / {meta.get('uploader', '')}",
          f"- 長度：{meta.get('duration', '')}",
          f"- 逐字稿來源：{meta.get('transcript_source', '')}",
          f"- 更新日期：{meta.get('last_updated', '')}"]
    if meta.get("keywords"):
        L.append("- **關鍵字：** " + " ".join(f"#{k}" for k in meta["keywords"]))
    L.append("")
    L += ["## 摘要與名詞說明", "", strip_h1(summary).strip(), ""]
    L += ["## 圖文對照（畫面 + 逐字稿）", ""]
    secs = [(f, it) for f, it in sections(segs, frames) if f is None or it]  # skip frames with no speech
    end = meta.get("duration", "").split(" ")[0]
    for n, (frame, items) in enumerate(secs):
        if frame:
            nxt = secs[n + 1][0]["t"] if n + 1 < len(secs) else end
            L += [f"### 畫面 {frame['t']}–{nxt}", "", f"![{frame['t']}](frames/{frame['file']})", ""]
            tags = meta.get("section_keywords", {}).get(frame["t"], [])
            if tags:
                L += ["**標籤：** " + " ".join(f"#{k}" for k in tags), ""]
        text = "，".join(t for _, t in items if t)
        if text:
            L += [text + "。", ""]
    if meta.get("known_asr_errors"):
        L += ["## 已知轉錄錯誤", "", "| 時間 | 聽成 | 應為 |", "|---|---|---|"]
        for e in meta["known_asr_errors"]:
            L.append(f"| {e['time']} | {e['heard']} | {e['expected']} |")
        L.append("")
    return "\n".join(L)


# ---------- Markdown -> docx (small subset: headings, tables, bullets, images, **bold**, `code`) ----------

def set_font(run, size=None, bold=None, mono=False):
    name = "Consolas" if mono else CJK_FONT
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rpr.rFonts.set(qn("w:eastAsia"), CJK_FONT)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


URL_RE = re.compile(r"https?://[A-Za-z0-9._~:/?#@!$&'*+,;=%-]+")


def add_hyperlink(par, url, size):
    """Append a real clickable hyperlink run to a python-docx paragraph."""
    rid = par.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    for tag, attrs in (("w:rStyle", {"w:val": "Hyperlink"}), ("w:color", {"w:val": "0563C1"}), ("w:u", {"w:val": "single"}),
                       ("w:sz", {"w:val": str(int(size * 2))})):
        el = OxmlElement(tag)
        for k, v in attrs.items():
            el.set(qn(k), v)
        rpr.append(el)
    run.append(rpr)
    text = OxmlElement("w:t")
    text.text = url
    run.append(text)
    link.append(run)
    par._p.append(link)


def add_inline(par, text, size=10.5):
    for tok in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|https?://[A-Za-z0-9._~:/?#@!$&'*+,;=%-]+)", text):
        if not tok:
            continue
        if URL_RE.fullmatch(tok):
            add_hyperlink(par, tok, size)
        elif tok.startswith("**"):
            set_font(par.add_run(tok[2:-2]), size, bold=True)
        elif tok.startswith("`"):
            set_font(par.add_run(tok[1:-1]), size - 1, mono=True)
        else:
            set_font(par.add_run(tok), size)


def md_to_docx(dest: Path, md: str, out: Path, kw=None):
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2)
    for name, size in (("Normal", 10.5), ("Heading 1", 20), ("Heading 2", 15), ("Heading 3", 12)):
        st = doc.styles[name]
        st.font.name = CJK_FONT
        st.element.rPr.rFonts.set(qn("w:eastAsia"), CJK_FONT)
        st.font.size = Pt(size)

    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            ncol = max(len(r) for r in rows)
            t = doc.add_table(rows=len(rows), cols=ncol)
            t.style = "Table Grid"
            for r, row in enumerate(rows):
                for c in range(ncol):
                    cell = t.cell(r, c)
                    cell.text = ""
                    par = cell.paragraphs[0]
                    add_inline(par, row[c] if c < len(row) else "", 9.5)
                    if r == 0:
                        for run in par.runs:
                            run.bold = True
            doc.add_paragraph()
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            doc.add_heading(m.group(2), level=len(m.group(1)))
        elif (im := re.match(r"^!\[[^\]]*\]\(([^)]+)\)$", line.strip())):
            img = dest / im.group(1)
            if img.exists():
                from PIL import Image
                w, h = Image.open(img).size  # cap height so portrait (vertical) videos don't fill whole pages
                doc.add_picture(str(img), width=Cm(min(12, 7 * w / h)))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("- "):
            add_inline(doc.add_paragraph(style="List Bullet"), line[2:])
        elif line.strip():
            add_inline(doc.add_paragraph(), line.strip())
        i += 1
    if kw:
        doc.core_properties.keywords = ", ".join(kw)
    doc.save(str(out))


def build(dest: Path):
    meta, summary, segs, frames = load(dest)
    md = build_md(dest, meta, summary, segs, frames)
    stem = file_stem(dest)
    for old in ("report.md", "report.docx", *dest.glob("*_report.*")):  # drop stale / legacy names
        (dest / old).unlink(missing_ok=True)
    out_md, out_docx = dest / f"{stem}_report.md", dest / f"{stem}_report.docx"
    out_md.write_text(md, encoding="utf-8")
    md_to_docx(dest, md, out_docx, meta.get("keywords"))
    return out_md, out_docx


if __name__ == "__main__":
    for p in build(Path(sys.argv[1])):
        print("wrote", p)
