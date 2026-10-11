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
import os
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


def resolve_redirect(url: str) -> str:
    """Follow short-link redirects (e.g. vt.tiktok.com/XXXX) to the canonical URL; fall back to the input."""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.geturl()
    except Exception:
        return url


def platform_and_id(url: str):
    u = urlparse(url)
    if "tiktok.com" in u.netloc.lower():
        if "/video/" not in u.path:
            u = urlparse(resolve_redirect(url))
        m = re.search(r"/video/(\d+)", u.path)
        if m:
            return "TikTok", m.group(1)
        parts = [p for p in urlparse(url).path.split("/") if p]
        return "TikTok", (parts[-1] if parts else "unknown")
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


def detect_language(text: str) -> str:
    """Rough language of a transcript from its characters.

    Returns 'zh', 'ja', 'ko', 'en', 'other' (mixed / unclear) or 'unknown' (too little text to judge).
    Counts CJK ideographs, kana, hangul and Latin *words* (not letters), so Chinese transcripts full of English
    technical terms still count as Chinese. Whisper's own language guess is not surfaced in the watch report,
    so this judges the output text; it says nothing reliable when Whisper ran with a forced --lang.
    """
    body = re.sub(r"\[\d{1,2}:\d{2}(?::\d{2})?\]|```|^#.*$|^_Source:.*$", "", text, flags=re.M)
    han = len(re.findall(r"[\u4e00-\u9fff]", body))
    kana = len(re.findall(r"[\u3040-\u30ff]", body))
    hangul = len(re.findall(r"[\uac00-\ud7af]", body))
    latin = len(re.findall(r"[A-Za-z]+", body))
    cjk = han + kana + hangul
    total = cjk + latin
    if total < 10:
        return "unknown"
    if hangul >= 5 and hangul / cjk >= 0.3:
        return "ko"
    if kana >= 5 and kana / cjk >= 0.05:  # Chinese has essentially no kana; kanji-heavy Japanese still has some
        return "ja"
    if han >= 10 and han / total >= 0.2:
        return "zh"
    if cjk == 0 and len({w.lower() for w in re.findall(r"[A-Za-z]+", body)}) < 4:
        return "unknown"  # e.g. fifteen lines of "ok": plenty of words, no information
    if latin >= 10 and cjk / total < 0.05:
        return "en"  # Latin-script non-Chinese (may be Spanish etc.); the translation flag is what matters
    return "other"


def load_glossary(domains):
    """Merge glossary/common.json + glossary/domains/<name>.json (dir overridable via WATCH_GLOSSARY_DIR).

    Returns (terms, replace). Domain terms come first so the 200-char Whisper prompt favours them.
    """
    gdir = Path(os.environ.get("WATCH_GLOSSARY_DIR") or ROOT / "glossary")
    files = [gdir / "common.json"] + [gdir / "domains" / f"{d}.json" for d in domains]
    for d, f in zip(["common"] + list(domains), files):
        if not f.exists():
            avail = sorted(p.stem for p in (gdir / "domains").glob("*.json"))
            if d == "common":
                continue
            sys.exit(f"glossary domain '{d}' not found in {gdir}/domains (available: {', '.join(avail) or 'none'})")
    terms, replace = [], {}
    for f in files[1:] + files[:1]:  # domains first, common last
        if f.exists():
            g = json.loads(f.read_text(encoding="utf-8"))
            terms += g.get("terms", [])
            replace.update(g.get("replace", {}))
    return list(dict.fromkeys(terms)), replace


def apply_glossary(text: str, replace: dict):
    """Fixed replacements for known ASR mistakes. Returns (text, {wrong: count})."""
    applied = {}
    for wrong in sorted(replace, key=len, reverse=True):  # longest first
        n = text.count(wrong)
        if n:
            text = text.replace(wrong, replace[wrong])
            applied[wrong] = n
    return text, applied


def fullwidth_punct(text: str) -> str:
    """Whisper emits ASCII , . ? ! : ; next to Chinese; make them full-width (，。？！：；)."""
    table = {",": "，", ".": "。", "?": "？", "!": "！", ":": "：", ";": "；"}
    cjk = "\u4e00-\u9fff"
    return re.sub(rf"(?<=[{cjk}])([,.?!:;])(?!\d)", lambda m: table[m.group(1)], text)


def whisper_prompt(terms, lang: str, limit: int = 200) -> str:
    """Hint text for Whisper: whole terms only, in priority order, within `limit` characters."""
    out = "以下是繁體中文的逐字稿，含標點符號。" if lang.startswith("zh") else ""
    first = True
    for t in terms:
        piece = t if first else "、" + t
        if len(out) + len(piece) > limit:
            break
        out += piece
        first = False
    return out


def tidy_title(raw: str, uploader: str = "") -> str:
    """Drop Facebook noise: '86K views · 1.3K reactions |' prefix, '| <uploader>' suffix, #hashtags."""
    parts = [p.strip() for p in raw.split("|")]
    parts = [p for p in parts if p and not re.search(r"\b(views?|reactions?|likes?)\b", p, re.I) and p != uploader]
    t = re.sub(r"#\S+", "", parts[0] if parts else raw).strip()
    return t or " ".join(hashtags(raw)) or raw.strip()  # hashtag-only titles (e.g. TikTok): keep the tags, minus '#'


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
    ap.add_argument("--title", help="override the display title/folder name (remembered in meta.json as title_override)")
    ap.add_argument("--glossary", default=None, help="comma-separated glossary domains, e.g. ai-chips,electronics (common is always loaded)")
    ap.add_argument("--lang", default="", help="force Whisper language, e.g. zh. Leave empty (default) so the language is auto-detected and reported; forcing a wrong language yields garbage")
    ap.add_argument("--terms", default="", help="extra comma-separated terms to hint Whisper (names, jargon)")
    ap.add_argument("--whisper", default="groq")
    ap.add_argument("--detail", default="balanced")
    ap.add_argument("--keep-media", action="store_true", help="also keep the full video in media/ (local only, gitignored)")
    args = ap.parse_args()

    platform, raw_id = platform_and_id(args.url)
    vid = safe_id(raw_id)

    early = sorted(OUT_ROOT.glob(f"*__{vid}"))
    early_meta = json.loads((early[0] / "meta.json").read_text(encoding="utf-8")) if early and (early[0] / "meta.json").exists() else {}
    domains = [d.strip() for d in args.glossary.split(",") if d.strip()] if args.glossary is not None else early_meta.get("glossaries", [])
    gl_terms, gl_replace = load_glossary(domains)
    terms = [t.strip() for t in args.terms.split(",") if t.strip()] + gl_terms
    env = dict(os.environ)
    if args.lang:
        env["WATCH_WHISPER_LANGUAGE"] = args.lang
    if terms:
        env["WATCH_WHISPER_PROMPT"] = whisper_prompt(terms, args.lang)

    work = Path(tempfile.mkdtemp(prefix="watch-archive-"))
    proc = subprocess.run(
        [sys.executable, str(WATCH), args.url, "--question", args.question,
         "--whisper", args.whisper, "--detail", args.detail, "--out-dir", str(work)],
        capture_output=True, text=True, env=env,
    )
    if proc.returncode != 0:
        print(f"watch.py failed (exit {proc.returncode}):\n{proc.stderr[-2000:]}", file=sys.stderr)
        sys.exit(proc.returncode)
    report = proc.stdout

    title_raw = field(report, "Title") or "untitled"
    prev_dirs = sorted(OUT_ROOT.glob(f"*__{vid}"))
    prev0 = json.loads((prev_dirs[0] / "meta.json").read_text(encoding="utf-8")) if prev_dirs and (prev_dirs[0] / "meta.json").exists() else {}
    title_override = args.title or prev0.get("title_override", "")
    title = title_override or tidy_title(title_raw, field(report, "Uploader"))
    tm = re.search(r"## Transcript\s*\n(.*?)(?:\n---\n_Work dir|\Z)", report, re.S)
    transcript_raw = tm.group(1).strip() if tm else ""
    detected_language = detect_language(transcript_raw)
    if detected_language in ("ja", "ko"):  # OpenCC / full-width punctuation would corrupt Japanese and Korean text
        transcript, glossary_applied = apply_glossary(transcript_raw, gl_replace)
    else:
        transcript, glossary_applied = apply_glossary(fullwidth_punct(to_traditional(transcript_raw)), gl_replace)
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
        "title_override": title_override,
        "whisper_hints": {"language": args.lang or "auto", "prompt": env.get("WATCH_WHISPER_PROMPT", "")},
        "detected_language": detected_language,
        "forced_lang": args.lang,
        "needs_zh_translation": detected_language not in ("zh", "unknown"),
        "glossaries": domains,
        "glossary_applied": glossary_applied,
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
        "slides": prev.get("slides", []),  # hand-curated: one entry per slide, overrides per-frame sections
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
    if args.lang:
        print(f"WARNING: --lang {args.lang} was forced to Whisper, so a wrong language would NOT be caught; "
              "if the audio is another language the transcript will be garbage. Rerun without --lang if unsure.", file=sys.stderr)
    if detected_language == "zh":
        print("language: zh (converted to Traditional zh-TW)")
    elif detected_language == "unknown":
        print("language: unknown（逐字稿太短或缺失，請自行判斷是否需要中譯）")
    elif detected_language == "other":
        print("language: other（混雜或無法判斷）：請讀逐字稿確認；若非中文，請依 SKILL 步驟 4b 寫 transcript.zh.md")
    else:
        print(f"language: {detected_language} -> 非中文影片：請依 SKILL 步驟 4b 寫 transcript.zh.md（繁體中文中譯，時間戳沿用原文）")


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
