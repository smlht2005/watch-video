#!/usr/bin/env python3
"""Export archived folders into one Obsidian vault (default: obsidian-vault/ at the repo root).

For each watch-output/<領域>/<資料夾>/ it writes
  <vault>/<領域>/<標題>.md          knowledge note: YAML properties + 摘要 + 思維導圖 + 連結 + 補充資料
  <vault>/<領域>/<標題>_操作SOP.md  copy of kb/*_操作SOP.md when the folder has an SOP
  <vault>/_attachments/<video_id>/ mindmap.png, carousel pages, SOP step images (relative links)
and rebuilds <vault>/00-索引.md (one section per 領域, [[wikilinks]]).

Links are never inferred from similarity: the `## 連結` section comes only from the hand-written links.md
(step 4e: `- [[概念]]｜關係：為什麼連`; the user confirms them). `related:` in the properties lists the same targets.

A rerun overwrites only files carrying `generated_by: watch-archive` (matched by video_id, so a renamed title does
not leave a stale copy); notes and images you add to the vault yourself are never touched.

Usage:
  python3 scripts/obsidian_export.py watch-output/<領域>/<資料夾> [--vault obsidian-vault]
  python3 scripts/obsidian_export.py --all [--vault obsidian-vault]
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


def link_targets(links_md: str) -> list:
    seen, out = set(), []
    for t in WIKI_RE.findall(links_md):
        t = t.strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


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
    links_md = read_text(dest / "links.md")
    targets = link_targets(links_md)
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
    related = [f"[[{t}]]" for t in targets + targets_sop]
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
    if links_md.strip():
        body += ["## 連結", "", "_由人選定並寫明關係；新增連結請改 links.md 再匯出。_", "", demote(links_md), ""]
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
    return written


def write_index(vault: Path):
    """00-索引.md: every generated note by 領域 (MOC). Only notes carrying our mark are listed."""
    rows = {}
    for md in sorted(vault.rglob("*.md")):
        if "_attachments" in md.parts or md.name == "00-索引.md" or not is_ours(md):
            continue
        fm = frontmatter_of(md)
        if fm.get("type") == "sop":
            continue
        rows.setdefault(fm.get("category", "未分類"), []).append((fm.get("date", ""), md.stem))
    out = ["---", "title: \"索引\"", MARK, "---", "", "# watch-archive 知識庫索引", "",
           "_由 `scripts/obsidian_export.py` 產生；每次匯出重建。_", ""]
    for cat in sorted(rows):
        out += [f"## {cat.replace('/', '／')}（{len(rows[cat])}）", ""]
        out += [f"- {d} [[{stem}]]" for d, stem in sorted(rows[cat], reverse=True)]
        out.append("")
    (vault / "00-索引.md").write_text("\n".join(out), encoding="utf-8")


def folders():
    return sorted([*OUT_ROOT.glob("*/*__*/meta.json"), *OUT_ROOT.glob("*/*/*__*/meta.json")])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", help="watch-output/<領域>/<資料夾>")
    ap.add_argument("--all", action="store_true", help="export every archived folder")
    ap.add_argument("--vault", default=str(DEFAULT_VAULT))
    args = ap.parse_args()
    if bool(args.folder) == args.all:
        sys.exit("give either one folder or --all")
    vault = Path(args.vault)
    dests = [mp.parent for mp in folders()] if args.all else [Path(args.folder)]
    for d in dests:
        for p in export(d, vault):
            print("wrote", p)
    write_index(vault)
    print("wrote", vault / "00-索引.md")


if __name__ == "__main__":
    main()
