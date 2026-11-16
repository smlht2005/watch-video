#!/usr/bin/env python3
"""Export archived folders into one Obsidian vault (default: obsidian-vault/ at the repo root).

For each watch-output/<領域>/<資料夾>/ it writes
  <vault>/<領域>/<標題>.md          note: YAML properties + 思維導圖（文字） + 知識點 + 連結 + 補充資料
  <vault>/知識點/<知識點>.md        one atomic note per confirmed knowledge point (knowledge.md)
  <vault>/<領域>/<標題>_操作SOP.md  copy of kb/*_操作SOP.md when the folder has an SOP
  <vault>/_attachments/<video_id>/ 圖文對照 pictures (<=1024 px), knowledge-point pictures, SOP step images (relative links)
and rebuilds <vault>/00-索引.md (notes by 領域, knowledge points, 待建立節點).

Only what a human confirmed is exported, and links are never inferred from similarity:
  knowledge.md  `## 已確認` / `## 候選`; each `### 標題` block has 出處／引文／說明／標示／連結 lines (step 4f)
  links.md      `## 已確認` / `## 候選`; each line `- [[概念]]｜關係類型：說明` (step 4e)
Only `## 已確認` is exported; a file without those headings counts as all 候選 (printed, not exported). A link
line without a relation is rejected. The provenance link (point -> its video note) is mechanical and automatic.

A rerun overwrites only files carrying `generated_by: watch-archive` (matched by video_id, so a renamed title does
not leave a stale copy); notes and images you add to the vault yourself are never touched.

Usage:
  python3 scripts/obsidian_export.py watch-output/<領域>/<資料夾>        # into obsidian-vault/ (a vault of its own)
  python3 scripts/obsidian_export.py --all
  python3 scripts/obsidian_export.py <folder> --vault <your vault>      # into <your vault>/watch-archive/ only
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

from build_report import IMG_RE, gallery, read_segs, strip_h1 as _strip_h1, to_sec  # one copy shared with the report

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "watch-output"
DEFAULT_VAULT = ROOT / "obsidian-vault"
MARK = "generated_by: watch-archive"
MANIFEST = ".watch-archive.json"  # {video_id: [vault-relative paths we wrote]}; the only proof a file is ours
WIKI_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
NAME_MAX = 100  # note file names keep this many characters (60 cut real titles such as '…part2' to '…part')
UNSAFE = re.compile(r'[\\/:*?"<>|#^\[\]]')  # characters Windows or Obsidian link names cannot hold


def q(v) -> str:
    """A JSON string is a valid YAML scalar: no escaping surprises."""
    return json.dumps(str(v), ensure_ascii=False)


def safe_name(title: str) -> str:
    return UNSAFE.sub("", title).strip()[:NAME_MAX].strip() or "note"


def tag_of(word: str) -> str:
    """Obsidian tag: letters/digits/_/-//, not purely numeric."""
    t = re.sub(r"[^\w/-]+", "-", word.strip()).strip("-/")
    return "" if t.isdigit() else t


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def strip_h1(md: str) -> str:
    return _strip_h1(md.lstrip()).strip()


def frontmatter_of(path: Path) -> dict:
    """Flat `key: "value"` pairs of a note's leading YAML block (enough for video_id / generated_by)."""
    out = {}
    text = read_text(path)
    if not text.startswith("---\n"):
        return out
    for line in text[4:].split("\n---", 1)[0].splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out


def is_ours(path: Path) -> bool:
    """Legacy test (before the manifest): our mark in the properties. A copy the user made keeps the mark, so this is
    only used for vaults exported before the manifest existed."""
    return MARK in read_text(path)[:2000]


def load_manifest(vault: Path) -> dict:
    try:
        return json.loads(read_text(vault / MANIFEST) or "{}")
    except ValueError:
        return {}


def save_manifest(vault: Path, manifest: dict):
    vault.mkdir(parents=True, exist_ok=True)
    (vault / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def rel(vault: Path, path: Path) -> str:
    return path.relative_to(vault).as_posix()


def owned(vault: Path, path: Path, vid: str, manifest: dict) -> bool:
    """Is `path` a file we generated for this video? The manifest decides; a video missing from it (vault exported
    before the manifest) falls back to the old mark + video_id test once."""
    if vid in manifest:
        return rel(vault, path) in manifest[vid]
    return is_ours(path) and frontmatter_of(path).get("video_id") == vid


def free_path(vault: Path, folder: Path, base: str, vid: str, manifest: dict, taken=()) -> Path:
    """First of '<base>.md', '<base> (<id>).md', '<base> (<id>) 2.md'… that is free or already ours for this video;
    a file the user owns is never overwritten."""
    names = [f"{base}.md", f"{base} ({vid[:12]}).md"] + [f"{base} ({vid[:12]}) {n}.md" for n in range(2, 100)]
    for name in names:
        p = folder / name
        if p in taken:
            continue
        if not p.exists() or owned(vault, p, vid, manifest):
            return p
    raise SystemExit(f"no free note name for {base!r} in {folder}")


def category_of(dest: Path, meta: dict) -> str:
    try:
        return dest.resolve().parent.relative_to(OUT_ROOT.resolve()).as_posix()
    except ValueError:  # folder outside watch-output/: fall back to meta.json
        return meta.get("category") or "未分類"


def note_path(vault: Path, cat: str, title: str, vid: str, manifest: dict) -> Path:
    """<vault>/<cat>/<title>.md; when another video or the user owns that name, a suffixed name keeps both."""
    return free_path(vault, vault / cat, safe_name(title), vid, manifest)


def drop_stale(vault: Path, vid: str, keep: set, manifest: dict):
    """Remove files we generated for this video earlier but not this time (renamed title, moved category, dropped
    knowledge point), then record what we own now. Only paths listed in the manifest are removed."""
    if vid in manifest:
        old = [vault / r for r in manifest[vid]]
    else:  # vault exported before the manifest: one-time scan by mark + video_id
        old = [md for md in vault.rglob("*.md") if "_attachments" not in md.parts and is_ours(md)
               and frontmatter_of(md).get("video_id") == vid]
    for p in old:
        if p not in keep and p.suffix == ".md":
            p.unlink(missing_ok=True)
    manifest[vid] = sorted(rel(vault, p) for p in keep)


LINK_RE = re.compile(r"^\s*[-*]\s*\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]\s*[｜|]\s*([^：:]+?)\s*[：:]\s*(.+?)\s*$")
POINT_DIR = "知識點"


def split_sections(md: str):
    """(confirmed text, candidate text, has_headings): text under '## 已確認' / '## 候選'."""
    parts = {"已確認": [], "候選": []}
    cur = None
    for line in md.splitlines():
        m = re.match(r"^##\s+(\S+)", line)  # an h2 (not ###) switches section; any other h2 ends it
        if m:
            cur = m.group(1) if m.group(1) in parts else None
        elif cur:
            parts[cur].append(line)
    has = bool(re.search(r"^##\s+(已確認|候選)", md, re.M))
    return "\n".join(parts["已確認"]), "\n".join(parts["候選"]), has


def parse_links(text: str):
    """([(target, relation, note)], [rejected lines]): a link line needs a relation; without one it is rejected."""
    ok, bad = [], []
    for line in text.splitlines():
        if not re.match(r"^\s*[-*]\s*\[\[", line):
            continue
        m = LINK_RE.match(line)
        (ok if m else bad).append(tuple(x.strip() for x in m.groups()) if m else line.strip())
    return ok, bad


def read_links(links_md: str):
    """(confirmed links, candidate links, problems). No headings at all -> everything is a candidate."""
    conf, cand, has = split_sections(links_md)
    if not has:
        conf, cand = "", links_md
    c_ok, c_bad = parse_links(conf)
    d_ok, d_bad = parse_links(cand)
    problems = [f"缺關係說明，已略過：{l}" for l in c_bad + d_bad]
    return c_ok, d_ok, problems


def parse_points(text: str):
    """Knowledge-point blocks: '### 標題' followed by '- 出處：／引文：／說明：／標示：／連結：' lines."""
    points, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            cur = {"title": m.group(1), "source": "", "quote": "", "note": "", "flag": "", "links": [], "bad": []}
            points.append(cur)
            continue
        f = re.match(r"^\s*[-*]\s*(出處|引文|說明|標示|連結)\s*[：:]\s*(.*?)\s*$", line)
        if cur and f:
            key, val = f.groups()
            if key == "連結":
                lm = LINK_RE.match("- " + val)
                cur["links"].append(tuple(x.strip() for x in lm.groups())) if lm else cur["bad"].append(val)
            else:
                cur[{"出處": "source", "引文": "quote", "說明": "note", "標示": "flag"}[key]] = val
    return points


def read_points(knowledge_md: str):
    """(confirmed points, candidate points, problems). No headings at all -> everything is a candidate."""
    conf, cand, has = split_sections(knowledge_md)
    if not has:
        conf, cand = "", knowledge_md
    ok, cands = parse_points(conf), parse_points(cand)
    problems = []
    for pt in ok:
        problems += [f"知識點「{pt['title']}」連結缺關係說明，已略過：{b}" for b in pt["bad"]]
        if not pt["note"] and not pt["quote"]:
            problems.append(f"知識點「{pt['title']}」沒有說明也沒有引文，仍匯出但內容空白")
    return ok, cands, problems


def relation_lines(links) -> list:
    return [f"- [[{t}]]｜{rel}：{note}" for t, rel, note in links]


def mind_map_text(dest: Path) -> str:
    """The mind map as text (mindmap.md's outline): it replaces both the summary and the PNG in the video note.
    HTML comments (the auto marker, also multi-line) and heading lines are dropped, and '•' bullets become '-' so
    Obsidian renders a list; '' when there is no mindmap.md."""
    text = re.sub(r"<!--.*?-->", "", read_text(dest / "mindmap.md"), flags=re.S)
    lines = [re.sub(r"^(\s*)•\s*", r"\1- ", l) for l in text.splitlines() if not l.lstrip().startswith("#")]
    return "\n".join(lines).strip("\n")


def gallery_lines(dest: Path, meta: dict, attach) -> list:
    """The report's 〈圖文對照〉 (build_report.gallery) with each picture copied through `attach` (a shrunk copy in
    _attachments/) and relinked; a picture missing from frames/ is left out."""
    tpath, zpath, fpath = dest / "transcript.md", dest / "transcript.zh.md", dest / "frames.json"
    segs = read_segs(tpath) if tpath.exists() else []
    frames = json.loads(read_text(fpath)) if fpath.exists() else []
    lines, _ = gallery(dict(meta, _zh=read_segs(zpath) if zpath.exists() else []), segs, frames)
    out = []
    for line in lines:
        m = IMG_RE.match(line)
        if not m:
            out.append(line)
            continue
        src = dest / m.group(1)
        if src.is_file():
            alt = line[2:line.index("](")]
            out.append(f"![{alt}]({attach(src, src.name)})")
        elif out and out[-1] == "":
            out.pop()  # drop the picture and its blank line together
    return out + [""]


def demote(md: str) -> str:
    """Hand-written side files: their '# title' is dropped and '#'/'##' become '###' under our own '## heading'."""
    out = []
    for line in strip_h1(md).splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        out.append(f"### {m.group(2)}" if m and len(m.group(1)) <= 2 else line)
    return "\n".join(out).strip()


def origin(dest: Path) -> str:
    try:
        return dest.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return dest.name


DEFAULT_FLAG = "講者／作者主張，未查證"  # CLAUDE.md hard rule: claims taken from a video or post are never facts
IMG_MAX = 1024


def source_image(dest: Path, meta: dict, source: str):
    """The picture a knowledge point's 出處 refers to: '第 N 頁' -> that page of a carousel; 'MM:SS' -> the frame
    closest in time. None when it cannot be resolved (the note is then exported without a picture)."""
    page = re.search(r"第\s*(\d+)\s*頁", source)
    if page and meta.get("slides"):
        slides = sorted(meta["slides"], key=lambda sl: to_sec(sl["start"]))
        n = int(page.group(1))
        if 1 <= n <= len(slides):
            f = dest / "frames" / slides[n - 1]["frame"]
            return f if f.exists() else None
    tm = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", source)
    if tm:
        try:
            frames = json.loads(read_text(dest / "frames.json") or "[]")
        except ValueError:
            return None
        cands = [(abs(to_sec(f["t"]) - to_sec(tm.group(1))), f["file"]) for f in frames if f.get("file") and f.get("t")]
        if cands:
            f = dest / "frames" / min(cands)[1]
            return f if f.exists() else None
    return None


def shrink_copy(src: Path, out: Path):
    """Vault copy of a picture: longest side <= IMG_MAX px, JPEG q80 (the original stays only in frames/)."""
    from PIL import Image
    img = Image.open(src).convert("RGB")
    img.thumbnail((IMG_MAX, IMG_MAX))
    img.save(out, "JPEG", quality=80)


def quote_found(dest: Path, quote: str) -> bool:
    """A quote must appear in the transcript or supplement (ignoring quote marks and whitespace), or it is a paraphrase."""
    norm = lambda t: re.sub(r"[\s「」『』\"“”]+", "", t)  # noqa: E731
    q_ = norm(quote)
    return not q_ or q_ in norm(read_text(dest / "transcript.md") + read_text(dest / "supplement.md"))


CONTEXT_SECS = 30   # 前後文: transcript lines within ±30 s of a knowledge point's 出處
CONTEXT_MAX = 12    # …at most this many lines, centred on the 出處 time
BAD_ANCHOR = re.compile(r"[#|^\[\]]")  # characters that break an Obsidian [[note#heading]] link


def mmss(sec: int) -> str:
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60:02d}:{sec % 60:02d}"


def section_anchors(meta: dict, segs: list, frames: list) -> list:
    """(start seconds, heading text) of every 〈圖文對照〉 section, taken from the same gallery() that writes the video
    note, so a knowledge point's link always matches the heading actually written (whatever its label)."""
    lines, _ = gallery(meta, segs, frames)
    out = []
    for i, line in enumerate(lines):
        if not line.startswith("### "):
            continue
        img = next((m for m in (re.match(r"^!\[([^\]]*)\]\(", l) for l in lines[i + 1:i + 4]) if m), None)
        alt = img.group(1) if img else ""
        if re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2})?", alt):
            out.append((to_sec(alt), line[4:].strip()))
    return sorted(out, key=lambda a: a[0])


def source_section(source: str, anchors: list, carousel: bool):
    """Index into `anchors` of the section a 出處 points at ('第 N 頁' -> page N; 'MM:SS' -> the section whose start
    is the latest one at or before that time, or the first section), or None when the 出處 has neither."""
    if not anchors:
        return None
    page = re.search(r"第\s*(\d+)\s*頁", source)
    if page:
        n = int(page.group(1))
        return n - 1 if 1 <= n <= len(anchors) else None
    tm = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", source)
    if not tm or carousel:
        return None
    t = to_sec(tm.group(1))
    return max([i for i, (s, _) in enumerate(anchors) if s <= t] or [0])


def youtube_at(url: str, sec: int) -> str:
    """The YouTube URL opened at `sec`; '' for any other platform (no time parameter to rely on)."""
    if not re.search(r"(youtube\.com|youtu\.be)/", url or ""):
        return ""
    url = re.sub(r"([?&])t=\d+s?&?", r"\1", url).rstrip("?&")
    return f"{url}{'&' if '?' in url else '?'}t={sec}s"


def context_lines(source: str, quote: str, segs: list, anchors: list, carousel: bool):
    """(label, lines) for the 前後文 callout: transcript lines within ±CONTEXT_SECS of the 出處 time (at most
    CONTEXT_MAX, centred on it), or a carousel page's whole text; lines carrying the quote (alone or across two
    adjacent lines) are bold. None when the 出處 has no time/page or nothing falls in the window."""
    norm = lambda t: re.sub(r"[\s，。、！？；：「」『』\"“”,.!?]+", "", t)  # noqa: E731
    if carousel:
        i = source_section(source, anchors, True)
        if i is None:
            return None
        lo, hi = anchors[i][0], (anchors[i + 1][0] if i + 1 < len(anchors) else 10 ** 9)
        win = [(ts, t) for ts, t in segs if lo <= to_sec(ts) < hi]
        label = re.search(r"第\s*\d+\s*頁", source).group(0)
    else:
        tm = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", source)
        if not tm:
            return None
        t0 = to_sec(tm.group(1))
        win = [(ts, t) for ts, t in segs if abs(to_sec(ts) - t0) <= CONTEXT_SECS]
        if len(win) > CONTEXT_MAX:
            mid = min(range(len(win)), key=lambda k: abs(to_sec(win[k][0]) - t0))
            start = max(0, min(mid - CONTEXT_MAX // 2, len(win) - CONTEXT_MAX))
            win = win[start:start + CONTEXT_MAX]
        label = f"{win[0][0]}–{win[-1][0]}" if win else ""
    if not win:
        return None
    q_ = norm(quote)
    bold = set()
    for k, (_, t) in enumerate(win):
        if q_ and (q_ in norm(t) or (len(norm(t)) >= 2 and norm(t) in q_)):
            bold.add(k)
        if q_ and k + 1 < len(win) and q_ in norm(t + win[k + 1][1]) and q_ not in norm(t) and q_ not in norm(win[k + 1][1]):
            bold |= {k, k + 1}
    rows = [f"**[{ts}] {t.strip()}**" if k in bold else f"[{ts}] {t.strip()}" for k, (ts, t) in enumerate(win)]
    return label, rows


def point_context(dest: Path, meta: dict, pt: dict, note_stem: str, anchors: list, segs: list, zh: list) -> dict:
    """Where a knowledge point's 出處 leads: the [[video note#section]] link target, a YouTube URL at that time, and
    the 前後文 callout (translation when transcript.zh.md exists; none when the quote only comes from supplement.md)."""
    carousel = meta.get("media_type") == "carousel"
    i = source_section(pt["source"], anchors, carousel)
    heading = anchors[i][1] if i is not None else ""
    target = f"{note_stem}#{heading}" if heading and not BAD_ANCHOR.search(heading) else note_stem
    tm = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", pt["source"])
    ext = youtube_at(meta.get("url", ""), to_sec(tm.group(1))) if tm and not carousel else ""
    ctx = None
    if pt["quote"]:
        norm = lambda t: re.sub(r"[\s「」『』\"“”]+", "", t)  # noqa: E731
        q_ = norm(pt["quote"])
        only_supplement = (q_ and q_ not in norm(read_text(dest / "transcript.md"))
                           and q_ in norm(read_text(dest / "supplement.md")))
        if segs and not only_supplement:
            ctx = context_lines(pt["source"], pt["quote"], zh or segs, anchors, carousel)
    return {"target": target, "heading": heading, "ext": ext, "context": ctx, "zh": bool(zh)}


def point_note_path(vault: Path, title: str, vid: str, manifest: dict, taken=()) -> Path:
    """<vault>/知識點/<title>.md; another video's (or the user's) note of that name is never overwritten."""
    return free_path(vault, vault / POINT_DIR, safe_name(title), vid, manifest, taken)


def point_md(pt: dict, meta: dict, vid: str, cat: str, note_stem: str, tags: list, image_rel: str = "",
             ctx: dict = None) -> str:
    """One atomic note: the claim, its source quote and origin (linked to the video note's section, with the
    transcript around it), a flag for unverified claims, relations chosen by a human."""
    ctx = ctx or {"target": note_stem, "heading": "", "ext": "", "context": None, "zh": False}
    src = pt["source"]
    src_link = f"[[{ctx['target']}|{src}]]" if src else "出處未標"
    if ctx["ext"]:
        src_link += f" · [▶ 原影片 {src}]({ctx['ext']})"
    targets = list(dict.fromkeys([t for t, _, _ in pt["links"]] + [note_stem]))
    front = ["---", f"title: {q(pt['title'])}", "type: knowledge-point", f"video_id: {q(vid)}",
             f"source_note: {q('[[' + note_stem + ']]')}", f"origin: {q(pt['source'])}", f"claim: {q(pt['flag'] or DEFAULT_FLAG)}",
             f"category: {q(cat)}", f"date: {q(meta.get('last_updated', ''))}", "status: confirmed", MARK,
             "tags:"] + [f"  - {q(t)}" for t in dict.fromkeys(["knowledge-point", *tags[1:]])]
    front += ["related:"] + [f"  - {q('[[' + t + ']]')}" for t in targets] + ["---", ""]
    body = [f"# {pt['title']}", ""]
    if pt["note"]:
        body += [pt["note"], ""]
    if pt["quote"]:
        body += [f"> {pt['quote']}", ">", f"> — {src_link}", ""]
        if ctx["context"]:
            label, rows = ctx["context"]
            body += [f"> [!quote]- 前後文{'（中譯）' if ctx['zh'] else ''}（{label}）", *[f"> - {r}" for r in rows], ""]
    if image_rel:
        body += [f"![出處圖]({image_rel})", ""]
    body += [f"**標示：** {pt['flag'] or DEFAULT_FLAG}", ""]
    if pt["links"]:
        body += ["## 連結", "", *relation_lines(pt["links"]), ""]
    body += ["## 出處", "", f"- [[{ctx['target']}|{note_stem}]]" + (f"（{src}）" if src else ""), ""]
    return "\n".join(front + body)


def export(dest: Path, vault: Path, with_pages: bool = False) -> list:
    meta = json.loads(read_text(dest / "meta.json"))
    vid = meta.get("video_id") or dest.name.rpartition("__")[2]
    cat = category_of(dest, meta)
    title = meta["title"]
    manifest = load_manifest(vault)
    path = note_path(vault, cat, title, vid, manifest)
    path.parent.mkdir(parents=True, exist_ok=True)
    att = vault / "_attachments" / vid
    rel_att = os.path.relpath(att, path.parent).replace(os.sep, "/")
    for old in att.glob("*") if att.is_dir() else []:  # our own folder per video: rebuilt every run
        old.unlink()
    written = []

    def attach(src: Path, name: str):
        att.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, att / name)
        return f"{rel_att}/{name}"

    def attach_small(src: Path, name: str):
        att.mkdir(parents=True, exist_ok=True)
        out = att / (Path(name).stem + ".jpg")
        shrink_copy(src, out)
        return f"{rel_att}/{out.name}"

    links_conf, links_cand, problems = read_links(read_text(dest / "links.md"))
    points, points_cand, p_problems = read_points(read_text(dest / "knowledge.md"))
    problems += p_problems
    for pt in points:
        if pt["quote"] and not quote_found(dest, pt["quote"]):
            problems.append(f"知識點「{pt['title']}」的引文在 transcript.md／supplement.md 找不到，可能是轉述")
    targets = list(dict.fromkeys([t for t, _, _ in links_conf]))
    # note path per point, decided first so the video note can link to them; two titles that become the same file
    # name (identical, or equal in their first NAME_MAX characters) would overwrite each other: keep the first only
    point_paths, by_name = {}, {}
    for pt in points:
        key = safe_name(pt["title"])
        if key in by_name:
            problems.append(f"知識點「{pt['title']}」與「{by_name[key]}」的檔名相同（標題重複或前 {NAME_MAX} 字相同），已略過後者，請改名")
            continue
        by_name[key] = pt["title"]
        point_paths[pt["title"]] = point_note_path(vault, pt["title"], vid, manifest, set(point_paths.values()))
    points = [pt for pt in points if pt["title"] in point_paths and by_name.get(safe_name(pt["title"])) == pt["title"]]
    sop_src = next(iter(sorted((dest / "kb").glob("*_操作SOP.md"))), None) if (dest / "kb").is_dir() else None
    targets_sop = [sop_src.stem] if sop_src else []

    tags = ["watch-archive", tag_of(cat)] + [tag_of(k) for k in meta.get("keywords", [])]
    tags = [t for i, t in enumerate(tags) if t and t not in tags[:i]]
    carousel = meta.get("media_type") == "carousel"
    front = ["---", f"title: {q(title)}", f"type: {'carousel-note' if carousel else 'video-note'}",
             f"source: {q(meta.get('url', ''))}", f"platform: {q(meta.get('platform', ''))}",
             f"video_id: {q(vid)}", f"uploader: {q(meta.get('uploader', ''))}", f"category: {q(cat)}",
             f"date: {q(meta.get('last_updated', ''))}", f"status: {'reviewed' if (links_conf or points) else 'unreviewed'}",
             f"origin_folder: {q(origin(dest))}", MARK, "aliases:", f"  - {q(title)}",
             "tags:"] + [f"  - {q(t)}" for t in tags]
    related = [f"[[{t}]]" for t in targets + targets_sop + [pp.stem for pp in point_paths.values()]]
    if related:
        front += ["related:"] + [f"  - {q(r)}" for r in related]
    front += ["---", ""]

    body = [f"# {title}", ""]
    outline = mind_map_text(dest)
    if outline:
        body += ["## 思維導圖", "", outline, ""]
    elif read_text(dest / "summary.md").strip():  # no mind map yet (older folders): the summary is all there is
        body += ["## 摘要", "", demote(read_text(dest / "summary.md")), ""]
    if with_pages:
        print("WARNING: --with-pages 已停用：頁面圖已收在〈圖文對照〉", file=sys.stderr)
    body += gallery_lines(dest, meta, attach_small)
    if point_paths:
        body += ["## 知識點", "", *[f"- [[{pp.stem}]]" for pp in point_paths.values()], ""]
    if links_conf:
        body += ["## 連結", "", "_由人選定並經使用者確認，每條寫明關係；要增減請改 links.md 的「已確認」區再匯出。_", "",
                 *relation_lines(links_conf), ""]
    if sop_src:
        body += ["## 操作 SOP", "", f"- [[{sop_src.stem}]]", ""]
    sup = demote(read_text(dest / "supplement.md"))
    if sup:
        body += ["## 補充資料", "", sup, ""]
    body += ["## 來源", "", f"- 原始資料夾：`{origin(dest)}`",
             f"- 逐字稿來源：{meta.get('transcript_source', '')}", ""]
    path.write_text("\n".join(front + body), encoding="utf-8")
    written.append(path)

    keep = {path}
    note_stem = path.stem
    tpath, zpath, fpath = dest / "transcript.md", dest / "transcript.zh.md", dest / "frames.json"
    segs = read_segs(tpath) if tpath.exists() else []
    zh = read_segs(zpath) if zpath.exists() else []
    anchors = section_anchors(dict(meta, _zh=zh), segs, json.loads(read_text(fpath) or "[]") if fpath.exists() else [])
    for pt in points:
        pp = point_paths[pt["title"]]
        pp.parent.mkdir(parents=True, exist_ok=True)
        img = source_image(dest, meta, pt["source"])
        rel = os.path.relpath(att, pp.parent).replace(os.sep, "/")
        out_name = Path(attach_small(img, img.name)).name if img else ""
        ctx = point_context(dest, meta, pt, note_stem, anchors, segs, zh)
        pp.write_text(point_md(pt, meta, vid, cat, note_stem, tags, f"{rel}/{out_name}" if out_name else "", ctx),
                      encoding="utf-8")
        keep.add(pp)
        written.append(pp)
    if sop_src:
        sop_text = read_text(sop_src)
        for img in sorted((dest / "kb" / "attachments").glob("step-*.jpg")):
            attach(img, img.name)
        sop_text = sop_text.replace("](attachments/", f"]({rel_att}/")
        sop_text = sop_text.replace("---\n", f"---\n{MARK}\n", 1)
        sop_path = path.parent / f"{sop_src.stem}.md"
        if not sop_path.exists() or owned(vault, sop_path, vid, manifest):
            sop_path.write_text(sop_text, encoding="utf-8")
            keep.add(sop_path)
            written.append(sop_path)
    drop_stale(vault, vid, keep, manifest)
    save_manifest(vault, manifest)
    if links_cand:
        problems.append(f"links.md 有 {len(links_cand)} 條候選連結未匯出（確認後移到「## 已確認」）")
    if points_cand:
        problems.append(f"knowledge.md 有 {len(points_cand)} 個候選知識點未匯出（確認後移到「## 已確認」）")
    for msg in problems:
        print(f"WARNING: {dest.name}: {msg}", file=sys.stderr)
    return written


def related_targets(md: Path) -> list:
    """[[targets]] listed under `related:` in a note's properties."""
    text = read_text(md)
    if not text.startswith("---\n"):
        return []
    block = text[4:].split("\n---", 1)[0]
    m = re.search(r"^related:\n((?:  - .*\n?)+)", block + "\n", re.M)
    return WIKI_RE.findall(m.group(1)) if m else []


def write_index(vault: Path):
    """00-索引.md: generated notes by 領域, knowledge points by source note, and 待建立節點 (a [[link]] whose note
    does not exist yet). Only notes we generated (per the manifest) are listed."""
    rows, points, stems, wanted, orphans = {}, {}, set(), {}, []
    manifest = load_manifest(vault)
    listed = {vault / r for paths in manifest.values() for r in paths}
    ours = (lambda md: md in listed) if manifest else is_ours  # a copy the user made of our note is not ours
    for md in sorted(vault.rglob("*.md")):
        if "_attachments" in md.parts or md.name == "00-索引.md":
            continue
        stems.add(md.stem)
        if not ours(md):
            continue
        fm = frontmatter_of(md)
        for t in related_targets(md):
            wanted.setdefault(t.strip(), []).append(md.stem)
        if fm.get("type") == "sop":
            continue
        if fm.get("type") == "knowledge-point":
            points.setdefault(fm.get("source_note", "").strip("[]"), []).append(md.stem)
            continue
        rows.setdefault(fm.get("category", "未分類"), []).append((fm.get("date", ""), md.stem))
        if fm.get("origin_folder") and not (ROOT / fm["origin_folder"]).exists():
            orphans.append((md.stem, fm["origin_folder"]))
    out = ["---", "title: \"索引\"", MARK, "---", "", "# watch-archive 知識庫索引", "",
           "_由 `scripts/obsidian_export.py` 產生；每次匯出重建。_", ""]
    for cat in sorted(rows):
        out += [f"## {cat.replace('/', '／')}（{len(rows[cat])}）", ""]
        out += [f"- {d} [[{stem}]]" for d, stem in sorted(rows[cat], reverse=True)]
        out.append("")
    if points:
        out += [f"## 知識點（{sum(len(v) for v in points.values())}）", ""]
        base = lambda t: re.sub(r" \([\w-]{1,12}\)$", "", t)  # noqa: E731
        names = [base(t) for v in points.values() for t in v]
        for src in sorted(points):
            out += [f"- [[{src}]]"] + [f"  - [[{t}]]" + ("（同名，待人工合併）" if names.count(base(t)) > 1 else "")
                                       for t in sorted(points[src])]
        out.append("")
    pending = sorted(t for t in wanted if t not in stems)
    if pending:
        out += [f"## 待建立節點（{len(pending)}）", "", "_已被連結、但還沒有筆記；有空再補，或連結不適合就改 links.md。_", ""]
        out += [f"- [[{t}]]（被 {'、'.join(sorted(set(wanted[t])))} 連結）" for t in pending]
        out.append("")
    if orphans:
        out += [f"## 來源資料夾已不存在（{len(orphans)}）", "", "_不會自動刪除；不要了請自行刪筆記。_", ""]
        out += [f"- [[{stem}]]（原：`{folder}`）" for stem, folder in sorted(orphans)]
        out.append("")
    (vault / "00-索引.md").write_text("\n".join(out), encoding="utf-8")


def folders():
    return sorted([*OUT_ROOT.glob("*/*__*/meta.json"), *OUT_ROOT.glob("*/*/*__*/meta.json")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", help="watch-output/<領域>/<資料夾>")
    ap.add_argument("--all", action="store_true", help="export every archived folder")
    ap.add_argument("--with-pages", action="store_true",
                    help="deprecated, no effect: every page/frame is now in the note's 圖文對照")
    ap.add_argument("--vault", default=None,
                    help="your own vault: everything goes into <vault>/watch-archive/ and nothing else in it is touched "
                         "(default: this repo's obsidian-vault/, a vault of its own)")
    args = ap.parse_args()
    if bool(args.folder) == args.all:
        sys.exit("give either one folder or --all")
    vault = Path(args.vault) / "watch-archive" if args.vault else DEFAULT_VAULT
    dests = [mp.parent for mp in folders()] if args.all else [Path(args.folder)]
    for d in dests:
        for p in export(d, vault, args.with_pages):
            print("wrote", p)
    write_index(vault)
    print("wrote", vault / "00-索引.md")


if __name__ == "__main__":
    main()
