#!/usr/bin/env python3
"""Build a readable report (<stem>_report.md + <stem>_report.docx) from an archived watch folder.

Reads  : meta.json, summary.md, transcript.md, frames.json, frames/*.jpg,
         transcript.zh.md (optional: Traditional Chinese translation of a foreign-language transcript,
         same "[mm:ss] text" lines; shown under the original text of each section),
         supplement.md (optional, hand-written, never overwritten by watch_archive: information the video
         does not show, e.g. the full text of a screen capture that was cut off, post captions, links)
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


def read_segs(path: Path):
    segs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = SEG_RE.match(line.strip())
        if m:
            segs.append((m.group(1), m.group(2)))
    return segs


def load(dest: Path):
    meta = json.loads((dest / "meta.json").read_text(encoding="utf-8"))
    summary = (dest / "summary.md").read_text(encoding="utf-8")
    segs = read_segs(dest / "transcript.md")
    zpath = dest / "transcript.zh.md"
    meta["_zh"] = read_segs(zpath) if zpath.exists() else []
    fpath = dest / "frames.json"
    frames = json.loads(fpath.read_text(encoding="utf-8")) if fpath.exists() else []
    return meta, summary, segs, frames


def join_text(parts):
    """Join transcript fragments: spaces for Latin-script text, Chinese commas otherwise."""
    parts = [p.strip() for p in parts if p and p.strip()]
    if not parts:
        return ""
    body = "".join(parts)
    if sum(c.isascii() for c in body) > 0.6 * len(body):
        text = " ".join(parts)
        return text if text[-1] in ".?!" else text + "."
    text = "".join(p if p[-1] in "，。？！；：、" else p + "，" for p in parts)
    return text.rstrip("，") + ("" if text.rstrip("，")[-1] in "。？！" else "。")


def text_lines(meta, segs, lo, hi):
    """Original text for [lo, hi) seconds, plus its translation from transcript.zh.md if present."""
    L = []
    text = join_text(t for ts, t in segs if lo <= to_sec(ts) < hi)
    if text:
        L += [text, ""]
    zh = "".join(t.strip() for ts, t in meta.get("_zh", []) if lo <= to_sec(ts) < hi)
    if zh:
        L += [f"**中譯：** {zh}", ""]
    return L


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


def slide_blocks(meta, segs):
    """One block per slide: one frame, optional note, then the transcript spoken while it is on screen."""
    slides = sorted(meta["slides"], key=lambda x: to_sec(x["start"]))
    end = meta.get("duration", "").split(" ")[0]
    L = []
    for n, sl in enumerate(slides):
        nxt = slides[n + 1]["start"] if n + 1 < len(slides) else end
        lo, hi = to_sec(sl["start"]), (to_sec(nxt) if nxt else 10 ** 9)
        title = f"：{sl['title']}" if sl.get("title") else ""
        L += [f"### 投影片 {n + 1}{title}（{sl['start']}–{nxt}）", "", f"![{sl['start']}](frames/{sl['frame']})", ""]
        if sl.get("note"):
            L += [f"**重點：** {sl['note']}", ""]
        if sl.get("keywords"):
            L += ["**標籤：** " + " ".join(f"#{k}" for k in sl["keywords"]), ""]
        L += text_lines(meta, segs, lo, hi)
    return L


def frame_blocks(meta, segs, frames):
    secs = [(f, it) for f, it in sections(segs, frames) if f is None or it]  # skip frames with no speech
    end = meta.get("duration", "").split(" ")[0]
    L = []
    for n, (frame, items) in enumerate(secs):
        nxt = secs[n + 1][0]["t"] if frame and n + 1 < len(secs) else end
        if frame:
            L += [f"### 畫面 {frame['t']}–{nxt}", "", f"![{frame['t']}](frames/{frame['file']})", ""]
            tags = meta.get("section_keywords", {}).get(frame["t"], [])
            if tags:
                L += ["**標籤：** " + " ".join(f"#{k}" for k in tags), ""]
        lo = to_sec(frame["t"]) if frame and n else 0
        hi = to_sec(nxt) if frame and nxt else 10 ** 9
        L += text_lines(meta, segs, lo, hi)
    return L


def supplement_lines(dest: Path):
    """Body of supplement.md for the report, under '## 補充資料'.

    The file's leading '# …' title is dropped; '#'/'##' headings -> '###' heading; '###' and deeper -> bold line
    (the docx converter handles at most three heading levels); fenced blocks (``` or ~~~) -> '> ' quotes.
    Returns [] when the file is missing or has no content besides its title.
    """
    path = dest / "supplement.md"
    if not path.exists():
        return []
    out, fenced, has_body, started = [], False, False, False
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fenced, has_body, started = not fenced, True, True
            out.append("")
        elif fenced:
            out.append(f"> {line}" if line.strip() else ">")
        elif (m := re.match(r"^(#{1,6})\s+(.*)$", line)):
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1 and not started:  # the file's own title; the section heading replaces it
                started = True
                continue
            started = has_body = True
            out.append(f"**{text}**" if level >= 3 else f"### {text}")
        else:
            if line.strip():
                started = has_body = True
            out.append(line)
    if not has_body:
        return []
    return ["## 補充資料（影片未呈現的資訊）", ""] + out + [""]


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
    L += supplement_lines(dest)
    L += ["## 圖文對照（畫面 + 逐字稿" + ("＋中譯）" if meta.get("_zh") else "）"), ""]
    if meta.get("slides"):
        L += slide_blocks(meta, segs)
    else:
        L += frame_blocks(meta, segs, frames)
    if meta.get("known_asr_errors"):
        L += ["## 已知轉錄錯誤", "", "| 時間 | 聽成 | 應為 |", "|---|---|---|"]
        for e in meta["known_asr_errors"]:
            L.append(f"| {e['time']} | {e['heard']} | {e['expected']} |")
        L.append("")
    if (dest / "supplement.md").exists():
        L += ["## 補充資料連結", "",
              "- 補充資料檔：[supplement.md](supplement.md)（與本報告同資料夾；內容已收錄於上方〈補充資料〉）", ""]
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
    for tok in re.split(r"(\[[^\]]+\]\([^)\s]+\)|\*\*[^*]+\*\*|`[^`]+`|https?://[A-Za-z0-9._~:/?#@!$&'*+,;=%-]+)", text):
        if not tok:
            continue
        if (lm := re.fullmatch(r"\[([^\]]+)\]\(([^)\s]+)\)", tok)):
            label, target = lm.groups()
            if URL_RE.fullmatch(target):
                add_hyperlink(par, target, size)
            else:
                set_font(par.add_run(label), size, mono=True)
        elif URL_RE.fullmatch(tok):
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
                import io
                pil = Image.open(img)
                w, h = pil.size  # cap height so portrait (vertical) videos don't fill whole pages
                buf = io.BytesIO()  # re-encode: some ffmpeg JPEGs lack a JFIF header that python-docx requires
                pil.convert("RGB").save(buf, "JPEG", quality=90)
                buf.seek(0)
                doc.add_picture(buf, width=Cm(min(12, 7 * w / h)))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith(">"):  # quoted block (fenced text from supplement.md): indented, monospace
            par = doc.add_paragraph()
            par.paragraph_format.left_indent = Cm(0.8)
            par.paragraph_format.space_after = Pt(0)
            set_font(par.add_run(line[2:] if line.startswith("> ") else line[1:]), 10, mono=True)
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
