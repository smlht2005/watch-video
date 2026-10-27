#!/usr/bin/env python3
"""Export archived folders into one Obsidian vault (default: obsidian-vault/ at the repo root).

For each watch-output/<領域>/<資料夾>/ it writes
  <vault>/<領域>/<標題>.md          note: YAML properties + 摘要 + 思維導圖 + 知識點 + 連結 + 補充資料
  <vault>/知識點/<知識點>.md        one atomic note per confirmed knowledge point (knowledge.md)
  <vault>/<領域>/<標題>_操作SOP.md  copy of kb/*_操作SOP.md when the folder has an SOP
  <vault>/_attachments/<video_id>/ mindmap.png, carousel pages, SOP step images (relative links)
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

ROOT = Path(__file__).resolve().parent.parent
OUT_ROOT = ROOT / "watch-output"
DEFAULT_VAULT = ROOT / "obsidian-vault"
MARK = "generated_by: watch-archive"
WIKI_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
UNSAFE = re.compile(r'[\\/:*?"<>|#^\[\]]')  # characters Windows or Obsidian link names cannot hold


def q(v) -> str:
    """A JSON string is a valid YAML scalar: no escaping surprises."""
    return json.dumps(str(v), ensure_ascii=False)


def safe_name(title: str) -> str:
    return UNSAFE.sub("", title).strip()[:60].strip() or "note"


def tag_of(word: str) -> str:
    """Obsidian tag: letters/digits/_/-//, not purely numeric."""
    t = re.sub(r"[^\w/-]+", "-", word.strip()).strip("-/")
    return "" if t.isdigit() else t


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def strip_h1(md: str) -> str:
    return re.sub(r"\A\s*# .*\n+", "", md).strip()


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
    return MARK in read_text(path)[:2000]


def category_of(dest: Path, meta: dict) -> str:
    try:
        return dest.resolve().parent.relative_to(OUT_ROOT.resolve()).as_posix()
    except ValueError:  # folder outside watch-output/: fall back to meta.json
        return meta.get("category") or "未分類"


def note_path(vault: Path, cat: str, title: str, vid: str) -> Path:
    """<vault>/<cat>/<title>.md; when another video already owns that name, '<title> (<id>)' keeps both."""
    base = safe_name(title)
    p = vault / cat / f"{base}.md"
    fm = frontmatter_of(p) if p.exists() else {}
    if p.exists() and (fm.get("video_id") != vid or MARK not in read_text(p)[:2000]):
        p = vault / cat / f"{base} ({vid[:12]}).md"
    return p


def drop_stale(vault: Path, vid: str, keep: set):
    """Remove generated notes of this video that a renamed title or a moved category left behind."""
    for md in vault.rglob("*.md"):
        if md in keep or "_attachments" in md.parts or not is_ours(md):
            continue
        if frontmatter_of(md).get("video_id") == vid:
            md.unlink()


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


def point_note_path(vault: Path, title: str, vid: str) -> Path:
    """<vault>/知識點/<title>.md; another video's (or the user's) note of that name is never overwritten."""
    base = safe_name(title)
    p = vault / POINT_DIR / f"{base}.md"
    if p.exists() and (frontmatter_of(p).get("video_id") != vid or not is_ours(p)):
        p = vault / POINT_DIR / f"{base} ({vid[:12]}).md"
    return p


def point_md(pt: dict, meta: dict, vid: str, cat: str, note_stem: str, tags: list) -> str:
    """One atomic note: the claim, its source quote and origin, a flag for unverified claims, relations chosen by a human."""
    targets = list(dict.fromkeys([t for t, _, _ in pt["links"]] + [note_stem]))
    front = ["---", f"title: {q(pt['title'])}", "type: knowledge-point", f"video_id: {q(vid)}",
             f"source_note: {q('[[' + note_stem + ']]')}", f"origin: {q(pt['source'])}", f"claim: {q(pt['flag'])}",
             f"category: {q(cat)}", f"date: {q(meta.get('last_updated', ''))}", "status: confirmed", MARK,
             "tags:"] + [f"  - {q(t)}" for t in dict.fromkeys(["knowledge-point", *tags[1:]])]
    front += ["related:"] + [f"  - {q('[[' + t + ']]')}" for t in targets] + ["---", ""]
    body = [f"# {pt['title']}", ""]
    if pt["note"]:
        body += [pt["note"], ""]
    if pt["quote"]:
        body += [f"> {pt['quote']}", ">", f"> — {pt['source'] or '出處未標'}", ""]
    if pt["flag"]:
        body += [f"**標示：** {pt['flag']}", ""]
    if pt["links"]:
        body += ["## 連結", "", *relation_lines(pt["links"]), ""]
    body += ["## 出處", "", f"- [[{note_stem}]]" + (f"（{pt['source']}）" if pt["source"] else ""), ""]
    return "\n".join(front + body)


def export(dest: Path, vault: Path) -> list:
    meta = json.loads(read_text(dest / "meta.json"))
    vid = meta.get("video_id") or dest.name.rpartition("__")[2]
    cat = category_of(dest, meta)
    title = meta["title"]
    path = note_path(vault, cat, title, vid)
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

    summary = read_text(dest / "summary.md")
    links_conf, links_cand, problems = read_links(read_text(dest / "links.md"))
    points, points_cand, p_problems = read_points(read_text(dest / "knowledge.md"))
    problems += p_problems
    targets = list(dict.fromkeys([t for t, _, _ in links_conf]))
    point_paths = {}  # point title -> note path (decided first so the video note can link to them)
    for pt in points:
        point_paths[pt["title"]] = point_note_path(vault, pt["title"], vid)
    sop_src = next(iter(sorted((dest / "kb").glob("*_操作SOP.md"))), None) if (dest / "kb").is_dir() else None
    targets_sop = [sop_src.stem] if sop_src else []

    tags = ["watch-archive", tag_of(cat)] + [tag_of(k) for k in meta.get("keywords", [])]
    tags = [t for i, t in enumerate(tags) if t and t not in tags[:i]]
    carousel = meta.get("media_type") == "carousel"
    front = ["---", f"title: {q(title)}", f"type: {'carousel-note' if carousel else 'video-note'}",
             f"source: {q(meta.get('url', ''))}", f"platform: {q(meta.get('platform', ''))}",
             f"video_id: {q(vid)}", f"uploader: {q(meta.get('uploader', ''))}", f"category: {q(cat)}",
             f"date: {q(meta.get('last_updated', ''))}", "status: unreviewed", MARK, "aliases:", f"  - {q(title)}",
             "tags:"] + [f"  - {q(t)}" for t in tags]
    related = [f"[[{t}]]" for t in targets + targets_sop + [pp.stem for pp in point_paths.values()]]
    if related:
        front += ["related:"] + [f"  - {q(r)}" for r in related]
    front += ["---", ""]

    body = [f"# {title}", ""]
    body += ["## 摘要", "", demote(summary), ""]
    if (dest / "mindmap.png").exists():
        body += ["## 思維導圖", "", f"![思維導圖]({attach(dest / 'mindmap.png', 'mindmap.png')})", ""]
    if carousel:
        body += ["## 圖文原頁", ""]
        for i, sl in enumerate(sorted(meta.get("slides", []), key=lambda s: s["start"]), 1):
            src = dest / "frames" / sl["frame"]
            if src.exists():
                body += [f"**第 {i} 頁：{sl.get('title', '')}**", "", f"![第 {i} 頁]({attach(src, sl['frame'])})", ""]
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
    for pt in points:
        pp = point_paths[pt["title"]]
        pp.parent.mkdir(parents=True, exist_ok=True)
        pp.write_text(point_md(pt, meta, vid, cat, note_stem, tags), encoding="utf-8")
        keep.add(pp)
        written.append(pp)
    if sop_src:
        sop_text = read_text(sop_src)
        for img in sorted((dest / "kb" / "attachments").glob("step-*.jpg")):
            attach(img, img.name)
        sop_text = sop_text.replace("](attachments/", f"]({rel_att}/")
        sop_text = sop_text.replace("---\n", f"---\n{MARK}\n", 1)
        sop_path = path.parent / f"{sop_src.stem}.md"
        if not sop_path.exists() or is_ours(sop_path):
            sop_path.write_text(sop_text, encoding="utf-8")
            keep.add(sop_path)
            written.append(sop_path)
    drop_stale(vault, vid, keep)
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
    does not exist yet). Only notes carrying our mark are listed."""
    rows, points, stems, wanted = {}, {}, set(), {}
    for md in sorted(vault.rglob("*.md")):
        if "_attachments" in md.parts or md.name == "00-索引.md":
            continue
        stems.add(md.stem)
        if not is_ours(md):
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
    out = ["---", "title: \"索引\"", MARK, "---", "", "# watch-archive 知識庫索引", "",
           "_由 `scripts/obsidian_export.py` 產生；每次匯出重建。_", ""]
    for cat in sorted(rows):
        out += [f"## {cat.replace('/', '／')}（{len(rows[cat])}）", ""]
        out += [f"- {d} [[{stem}]]" for d, stem in sorted(rows[cat], reverse=True)]
        out.append("")
    if points:
        out += [f"## 知識點（{sum(len(v) for v in points.values())}）", ""]
        for src in sorted(points):
            out += [f"- [[{src}]]"] + [f"  - [[{t}]]" for t in sorted(points[src])]
        out.append("")
    pending = sorted(t for t in wanted if t not in stems)
    if pending:
        out += [f"## 待建立節點（{len(pending)}）", "", "_已被連結、但還沒有筆記；有空再補，或連結不適合就改 links.md。_", ""]
        out += [f"- [[{t}]]（被 {'、'.join(sorted(set(wanted[t])))} 連結）" for t in pending]
        out.append("")
    (vault / "00-索引.md").write_text("\n".join(out), encoding="utf-8")


def folders():
    return sorted([*OUT_ROOT.glob("*/*__*/meta.json"), *OUT_ROOT.glob("*/*/*__*/meta.json")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", help="watch-output/<領域>/<資料夾>")
    ap.add_argument("--all", action="store_true", help="export every archived folder")
    ap.add_argument("--vault", default=None,
                    help="your own vault: everything goes into <vault>/watch-archive/ and nothing else in it is touched "
                         "(default: this repo's obsidian-vault/, a vault of its own)")
    args = ap.parse_args()
    if bool(args.folder) == args.all:
        sys.exit("give either one folder or --all")
    vault = Path(args.vault) / "watch-archive" if args.vault else DEFAULT_VAULT
    dests = [mp.parent for mp in folders()] if args.all else [Path(args.folder)]
    for d in dests:
        for p in export(d, vault):
            print("wrote", p)
    write_index(vault)
    print("wrote", vault / "00-索引.md")


if __name__ == "__main__":
    main()
