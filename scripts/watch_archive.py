#!/usr/bin/env python3
"""Run the watch skill and archive the result into watch-output/.

Folder name: <date>_<platform>_<title>__<video-id>
A folder whose name ends with __<video-id> is reused (updated in place), so one
video always maps to exactly one folder.

Outputs per video: meta.json, transcript.md (Traditional; transcript.raw.md if converted), summary.md, frames/, <stem>_report.md, <stem>_report.docx, media/<stem>_video.<ext> (--keep-media)
where <stem> = <date>_<platform>_<title 20 chars>__<video-id>

Usage:
  python3 scripts/watch_archive.py URL [--question Q] [--local | --whisper groq|openai|whisperx] [--detail balanced] [--keep-media]

Transcription (only when the video has no captions): --whisper > --local (WhisperX) > the choice remembered in
meta.json > groq when GROQ_API_KEY exists (env or ~/.config/watch/.env) > WATCH_WHISPER_BACKEND saved by setup.py.
"""
import argparse
import build_report
import clean_fillers
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
sys.path.insert(0, str(WATCH.parent))
import config as watch_config  # noqa: E402  (the watch skill's key / backend settings)
OUT_ROOT = ROOT / "watch-output"
TITLE_MAX = 40
NAME_MAX = 120
DEFAULT_CATEGORY = "未分類"
# coarse category (the subfolder under watch-output/) inferred from the glossary domain when --category is not given
CATEGORY_BY_DOMAIN = {
    "ai-chips": "AI", "ai-video": "AI", "claude-code": "AI", "neo4j": "AI",
    "kubernetes": "雲端", "electronics": "電子", "pure-land": "佛學", "lengyan": "佛學",
}


def safe_category(name: str) -> str:
    """One path segment only: no separators, no leading dots."""
    c = re.sub(r'[\\/:*?"<>|\s]+', "-", (name or "").strip()).strip(".-")
    return c or DEFAULT_CATEGORY


def pick_category(arg: str, prev: str, domains) -> str:
    if arg:
        return safe_category(arg)
    if prev:
        return prev
    for d in domains:
        if d in CATEGORY_BY_DOMAIN:
            return CATEGORY_BY_DOMAIN[d]
    return DEFAULT_CATEGORY


def find_dirs(vid: str):
    """Existing archive folder(s) for a video ID: <category>/<folder>, or a legacy flat <folder>."""
    return sorted(OUT_ROOT.glob(f"*/*__{vid}")) + sorted(p for p in OUT_ROOT.glob(f"*__{vid}") if p.is_dir())


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
    if "drive.google.com" in host:  # /file/d/<id>/view or open?id=<id>
        if "d" in parts and parts.index("d") + 1 < len(parts):
            return "GoogleDrive", parts[parts.index("d") + 1]
        if "id" in parse_qs(u.query):
            return "GoogleDrive", parse_qs(u.query)["id"][0]
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
    hira = len(re.findall(r"[\u3040-\u309f]", body))  # particles (の は を です…) exist only in Japanese; katakana brands appear in Chinese too
    hangul = len(re.findall(r"[\uac00-\ud7af]", body))
    latin = len(re.findall(r"[A-Za-z]+", body))
    cjk = han + kana + hangul
    total = cjk + latin
    if total < 10:
        return "unknown"
    if hangul >= 5 and hangul / cjk >= 0.3:
        return "ko"
    if hira >= 5:
        # Real Japanese has hiragana (particles) on almost every line; Chinese quoting a Japanese phrase or title
        # has it on a minority of lines, and then falls through to the Chinese check below.
        cjk_lines = [ln for ln in body.splitlines() if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", ln)]
        hira_share = sum(1 for ln in cjk_lines if re.search(r"[\u3040-\u309f]", ln)) / max(len(cjk_lines), 1)
        if hira_share >= 0.5:
            if hira / cjk >= 0.15:  # real Japanese prose is typically 30-60% hiragana
                return "ja"
            if hira / cjk >= 0.05:
                return "other"  # kanji-heavy Japanese (headlines, noun lists): a human decides
    if han >= 10 and han / total >= 0.2:
        return "zh"
    if cjk == 0 and len({w.lower() for w in re.findall(r"[A-Za-z]+", body)}) < 4:
        return "unknown"  # e.g. fifteen lines of "ok": plenty of words, no information
    if latin >= 10 and cjk / total < 0.05:
        return "en"  # Latin-script non-Chinese (may be Spanish etc.); the translation flag is what matters
    return "other"


# Whisper's language names -> codes (99 languages; 'cantonese' / 'yue' count as Chinese for our purposes)
_WHISPER_NAMES = (
    "afrikaans af|albanian sq|amharic am|arabic ar|armenian hy|assamese as|azerbaijani az|bashkir ba|basque eu|"
    "belarusian be|bengali bn|bosnian bs|breton br|bulgarian bg|burmese my|catalan ca|chinese zh|croatian hr|"
    "czech cs|danish da|dutch nl|english en|estonian et|faroese fo|finnish fi|french fr|galician gl|georgian ka|"
    "german de|greek el|gujarati gu|haitian_creole ht|hausa ha|hawaiian haw|hebrew he|hindi hi|hungarian hu|"
    "icelandic is|indonesian id|italian it|japanese ja|javanese jw|kannada kn|kazakh kk|khmer km|korean ko|lao lo|"
    "latin la|latvian lv|lingala ln|lithuanian lt|luxembourgish lb|macedonian mk|malagasy mg|malay ms|"
    "malayalam ml|maltese mt|maori mi|marathi mr|mongolian mn|nepali ne|norwegian no|occitan oc|pashto ps|"
    "persian fa|polish pl|portuguese pt|punjabi pa|romanian ro|russian ru|sanskrit sa|serbian sr|shona sn|"
    "sindhi sd|sinhala si|slovak sk|slovenian sl|somali so|spanish es|sundanese su|swahili sw|swedish sv|"
    "tagalog tl|tajik tg|tamil ta|tatar tt|telugu te|thai th|tibetan bo|turkish tr|turkmen tk|ukrainian uk|"
    "urdu ur|uzbek uz|vietnamese vi|welsh cy|yiddish yi|yoruba yo|cantonese zh|mandarin zh"
)
WHISPER_LANGUAGES = {pair.split()[0].replace("_", " "): pair.split()[1] for pair in _WHISPER_NAMES.split("|")}
WHISPER_CODES = set(WHISPER_LANGUAGES.values()) | {"yue"}
# Whisper often emits these on silence / music; they are not trustworthy language ids
UNRELIABLE_WHISPER = {"nn", "nynorsk"}


def normalize_whisper_language(raw: str) -> str:
    """Whisper reports a language name ('english') or code ('en', 'zh-TW', 'yue'); return a lowercase code.

    Returns '' when absent, unparseable (digits, junk) or known to be unreliable ('nn'); the caller then falls back
    to the text heuristic.
    """
    name = re.sub(r"\s+", " ", (raw or "").strip().lower().replace("_", " "))
    for candidate in (name, re.split(r"[ \-(]", name)[0]):  # 'haitian creole', then 'chinese' from 'chinese (traditional)' / 'zh-tw'
        if not candidate or candidate in UNRELIABLE_WHISPER:
            return ""
        if candidate in WHISPER_LANGUAGES:
            return WHISPER_LANGUAGES[candidate]
        if candidate == "yue":
            return "zh"
        if candidate in WHISPER_CODES:
            return candidate
    return ""


def forced_language(arg_lang: str, environ=None) -> str:
    """--lang, or WATCH_WHISPER_LANGUAGE already set in the environment: both force Whisper's language."""
    return arg_lang or (environ if environ is not None else os.environ).get("WATCH_WHISPER_LANGUAGE", "")


def _has_content(text: str) -> bool:
    body = re.sub(r"\[\d{1,2}:\d{2}(?::\d{2})?\]|```|^#.*$|^_Source:.*$", "", text, flags=re.M)
    return bool(re.search(r"[A-Za-z\u3040-\u30ff\u4e00-\u9fff\uac00-\ud7af]", body))


def resolve_language(text: str, whisper_raw: str = "", forced: str = "") -> tuple[str, str]:
    """Pick the language label and say where it came from: (language, source).

    source is 'whisper', 'whisper (text: zh)' (Whisper and the text disagree: a human should check),
    'heuristic' or 'heuristic (forced --lang)'. Whisper's own language id wins when present (more reliable than
    character ratios for short or mixed text) unless the language was forced (Whisper then just echoes it) or the
    transcript has no content (silence/music: Whisper still reports a language). Platform captions carry no
    Whisper language, so those use detect_language().
    """
    if forced:
        return detect_language(text), "heuristic (forced --lang)"
    if not _has_content(text):
        return "unknown", "heuristic"
    code = normalize_whisper_language(whisper_raw)
    if not code:
        return detect_language(text), "heuristic"
    text_lang = detect_language(text)
    cjk = ("zh", "ja", "ko")
    conflict = (code in cjk and text_lang in cjk + ("en",) and text_lang != code) or (code not in cjk and text_lang in cjk)
    return code, f"whisper (text: {text_lang})" if conflict else "whisper"


def needs_zh_translation(detected: str) -> bool:
    """Any known non-Chinese language (en, ja, ko, es…) gets a Traditional Chinese translation; other / unknown are left to a human check."""
    return detected not in ("zh", "other", "unknown")


def convert_to_traditional(detected: str) -> bool:
    """OpenCC + full-width punctuation only for text that may be Chinese.

    Skipped for ja / ko (would corrupt kanji, e.g. 会議 -> 會議) and for 'other' (unclear: a human decides first).
    """
    return detected not in ("ja", "ko", "other")


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


def has_groq_key() -> bool:
    """GROQ_API_KEY from the environment, ~/.config/watch/.env or a project .env (same lookup as the watch skill)."""
    return watch_config.load_api_key("groq")[0] is not None


def resolve_fillers_mode(clean: bool, keep: bool, remembered: str) -> str:
    """'on'/'off' forced by --clean-fillers/--keep-fillers (remembered across reruns); otherwise 'auto'."""
    if clean:
        return "on"
    if keep:
        return "off"
    return remembered if remembered in ("on", "off") else "auto"


def fillers_enabled(mode: str, domains, video_type: str = "") -> bool:
    """auto = a spoken lecture (講座／講經): the pure-land glossary is loaded or meta.json.video_type is "lecture";
    its particles (呢、啊…) are then stripped from transcript.md."""
    return mode == "on" or (mode == "auto" and ("pure-land" in domains or video_type == "lecture"))


def apply_fillers(transcript: str, to_zh_tw: bool, mode: str, domains, video_type: str = ""):
    """Strip filler particles when enabled and the transcript is Chinese. Returns (text, lines changed, lines dropped)."""
    if to_zh_tw and fillers_enabled(mode, domains, video_type):
        return clean_fillers.clean_text(transcript)
    return transcript, 0, 0


def resolve_sop_mode(sop: bool, no_sop: bool, remembered: str) -> str:
    """'on'/'off' forced by --sop/--no-sop (remembered across reruns); otherwise 'auto' = Claude decides from the video."""
    if sop:
        return "on"
    if no_sop:
        return "off"
    return remembered if remembered in ("on", "off") else "auto"


def pick_whisper(explicit: str | None, local: bool, remembered: str, groq_key: bool) -> str | None:
    """Transcription backend for watch.py: --whisper > --local (WhisperX) > the choice remembered in meta.json >
    groq when a Groq key exists. None lets watch.py fall back to WATCH_WHISPER_BACKEND in ~/.config/watch/.env.
    """
    if explicit:
        return explicit
    if local:
        return "whisperx"
    if remembered:
        return remembered
    return "groq" if groq_key else None


def configured_backend() -> str:
    try:
        return watch_config.get_config()["whisper_backend"]
    except watch_config.ConfigError:
        return ""


def whisper_hints(backend: str, lang: str, prompt: str) -> tuple[dict, str, str, list]:
    """Env for watch.py plus the language / prompt that will really reach the backend, and warnings.

    Groq / OpenAI read WATCH_WHISPER_LANGUAGE / WATCH_WHISPER_PROMPT. WhisperX only reads WATCH_WHISPERX_LANGUAGE
    (two lowercase letters) and has no prompt, so glossary terms only apply as post-transcription replacements.
    """
    if backend != "whisperx":
        env = {k: v for k, v in (("WATCH_WHISPER_LANGUAGE", lang), ("WATCH_WHISPER_PROMPT", prompt)) if v}
        return env, lang, prompt, []
    warnings = []
    if prompt:
        warnings.append("WhisperX has no prompt support: glossary / --terms hints are not sent "
                        "(glossary replacements still apply after transcription).")
    if lang and not re.fullmatch(r"[a-z]{2}", lang):
        warnings.append(f"WhisperX needs a two-letter language code; --lang {lang} ignored, language auto-detected.")
        lang = ""
    return ({"WATCH_WHISPERX_LANGUAGE": lang} if lang else {}), lang, "", warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--question", default="請摘要影片內容並附時間戳")
    ap.add_argument("--category", default="", help="coarse category = subfolder under watch-output/ (e.g. AI, 佛學, 理財); default: remembered, else inferred from --glossary, else 未分類; changing it moves the folder")
    ap.add_argument("--title", help="override the display title/folder name (remembered in meta.json as title_override)")
    ap.add_argument("--glossary", default=None, help="comma-separated glossary domains, e.g. ai-chips,electronics (common is always loaded)")
    ap.add_argument("--lang", default="", help="force Whisper language, e.g. zh. Leave empty (default) so the language is auto-detected and reported; forcing a wrong language yields garbage")
    ap.add_argument("--terms", default="", help="extra comma-separated terms to hint Whisper (names, jargon)")
    wg = ap.add_mutually_exclusive_group()
    wg.add_argument("--whisper", choices=["groq", "openai", "whisperx"], default=None,
                    help="transcription backend; default groq when a Groq key exists, else WATCH_WHISPER_BACKEND from "
                         "setup.py; remembered in meta.json")
    wg.add_argument("--local", action="store_true",
                    help="transcribe with local WhisperX even when a Groq key exists; remembered in meta.json")
    ap.add_argument("--detail", default="balanced")
    ap.add_argument("--keep-media", action="store_true", help="also keep the full video in media/ (local only, gitignored)")
    ap.add_argument("--timestamps", default=None,
                    help="comma-separated cue times (MM:SS or H:MM:SS) to grab extra frames at, e.g. at topic changes in long "
                         "screen-recording / notebook sections that scene detection skips; remembered in meta.json")
    ap.add_argument("--resolution", type=int, default=None,
                    help="frame width in pixels (watch default 512); 1024 makes code and small slide text readable; remembered")
    sg = ap.add_mutually_exclusive_group()
    sg.add_argument("--sop", action="store_true", help="force the step-by-step SOP step (computer-tool tutorials); remembered")
    sg.add_argument("--no-sop", action="store_true", help="skip the SOP step even if sop.md exists; remembered")
    fg = ap.add_mutually_exclusive_group()
    fg.add_argument("--clean-fillers", action="store_true", help="strip filler particles (呢、啊…) from the Chinese transcript; default for lectures (講座／講經: --glossary pure-land or video_type lecture); remembered")
    fg.add_argument("--keep-fillers", action="store_true", help="keep filler particles even for lectures; remembered")
    args = ap.parse_args()

    platform, raw_id = platform_and_id(args.url)
    vid = safe_id(raw_id)

    early = find_dirs(vid)
    early_meta = json.loads((early[0] / "meta.json").read_text(encoding="utf-8")) if early and (early[0] / "meta.json").exists() else {}
    domains = [d.strip() for d in args.glossary.split(",") if d.strip()] if args.glossary is not None else early_meta.get("glossaries", [])
    gl_terms, gl_replace = load_glossary(domains)
    terms = [t.strip() for t in args.terms.split(",") if t.strip()] + gl_terms
    whisper_choice = args.whisper or ("whisperx" if args.local else early_meta.get("whisper_choice", ""))
    whisper = pick_whisper(args.whisper, args.local, early_meta.get("whisper_choice", ""), has_groq_key())
    hint_env, lang, prompt, hint_warnings = whisper_hints(
        whisper or configured_backend(), args.lang, whisper_prompt(terms, args.lang) if terms else "")
    for w in hint_warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    env = dict(os.environ, **hint_env)

    # Archiving needs frames + transcript, which only the local engine returns; with GEMINI_API_KEY set,
    # watch.py's "auto" would pick Gemini and the archive would come out empty. WATCH_ENGINE overrides.
    engine = os.environ.get("WATCH_ENGINE", "local")
    cue_timestamps = args.timestamps if args.timestamps is not None else early_meta.get("cue_timestamps", "")
    resolution = args.resolution or early_meta.get("resolution")
    extra = (["--timestamps", cue_timestamps] if cue_timestamps else []) + (["--resolution", str(resolution)] if resolution else [])
    extra += ["--whisper", whisper] if whisper else []
    # ~/.config/watch/.env may carry WATCH_SUB_LANG=en ("prefer English"), which would pick YouTube's English
    # auto-translation of a Chinese video; the archive wants the video's own language.
    extra += ["--sub-lang", "auto"]
    work = Path(tempfile.mkdtemp(prefix="watch-archive-"))
    proc = subprocess.run(
        [sys.executable, str(WATCH), args.url, "--engine", engine, "--question", args.question,
         "--detail", args.detail, "--out-dir", str(work)] + extra,
        capture_output=True, text=True, env=env,
    )
    if proc.returncode != 0:
        print(f"watch.py failed (exit {proc.returncode}):\n{proc.stderr[-2000:]}", file=sys.stderr)
        sys.exit(proc.returncode)
    report = proc.stdout
    if "## Transcript" not in report and "frame_" not in report:
        print("watch.py returned neither frames nor a transcript (download or engine problem); nothing archived.\n"
              + report[:1500], file=sys.stderr)
        sys.exit(1)

    title_raw = field(report, "Title") or "untitled"
    prev_dirs = find_dirs(vid)
    prev0 = json.loads((prev_dirs[0] / "meta.json").read_text(encoding="utf-8")) if prev_dirs and (prev_dirs[0] / "meta.json").exists() else {}
    title_override = args.title or prev0.get("title_override", "")
    title = title_override or tidy_title(title_raw, field(report, "Uploader"))
    tm = re.search(r"## Transcript\s*\n(.*?)(?:\n---\n_Work dir|\Z)", report, re.S)
    transcript_raw = tm.group(1).strip() if tm else ""
    detected_language, language_source = resolve_language(
        transcript_raw, field(report, "Whisper language"), forced_language(lang))
    if "(text:" in language_source:
        print(f"WARNING: Whisper reported '{detected_language}' but the transcript text looks different "
              f"({language_source}); check the language before relying on translation / conversion.", file=sys.stderr)
    to_zh_tw = convert_to_traditional(detected_language)
    if to_zh_tw:
        transcript, glossary_applied = apply_glossary(fullwidth_punct(to_traditional(transcript_raw)), gl_replace)
        title = to_traditional(title)
    else:  # keep ja / ko / unclear text untouched
        transcript, glossary_applied = apply_glossary(transcript_raw, gl_replace)
    fillers_mode = resolve_fillers_mode(args.clean_fillers, args.keep_fillers, early_meta.get("clean_fillers", ""))
    transcript, n_changed, n_dropped = apply_fillers(transcript, to_zh_tw, fillers_mode, domains, early_meta.get("video_type", ""))  # raw.md keeps the original
    if n_changed or n_dropped:
        print(f"[watch] filler particles removed: {n_changed} line(s) cleaned, {n_dropped} dropped")
    if _S2T is None:
        print("WARNING: opencc not installed; transcript left as-is (pip install opencc-python-reimplemented)", file=sys.stderr)
    src_m = re.search(r"_Source:\s*(.+?)\._", transcript)
    transcript_source = src_m.group(1) if src_m else "unknown"

    frames = []
    for m in re.finditer(r"^- `([^`]+)` \(t=([\d:]+), reason=([^)]*)\)", report, re.M):
        frames.append({"src": m.group(1), "t": m.group(2), "reason": m.group(3)})

    # Reuse an existing folder for the same video ID; otherwise create a new one.
    OUT_ROOT.mkdir(exist_ok=True)
    existing = find_dirs(vid)
    category = pick_category(args.category, prev0.get("category", ""), domains)
    cat_dir = OUT_ROOT / category
    cat_dir.mkdir(exist_ok=True)
    if existing:
        # keep the original date prefix but follow title changes (e.g. Simplified -> Traditional) and category changes
        dest = existing[0]
        renamed = cat_dir / f"{dest.name.split('_')[0]}_{platform}_{clean_title(title)}__{vid}"[:NAME_MAX]
        if renamed != dest and not renamed.exists():
            dest = dest.rename(renamed)
    else:
        name = f"{dt.date.today():%Y-%m-%d}_{platform}_{clean_title(title)}__{vid}"
        dest = cat_dir / name[:NAME_MAX]
    dest.mkdir(exist_ok=True)

    prev = json.loads((dest / "meta.json").read_text(encoding="utf-8")) if (dest / "meta.json").exists() else {}
    meta = {
        "url": args.url,
        "platform": platform,
        "video_id": vid,
        "title": title,
        "title_raw": title_raw,
        "title_override": title_override,
        "category": category,
        "whisper_hints": {"language": lang or "auto", "prompt": prompt},
        "whisper_choice": whisper_choice,
        "detected_language": detected_language,
        "language_source": language_source,
        "forced_lang": lang,
        "needs_zh_translation": needs_zh_translation(detected_language),
        "glossaries": domains,
        "glossary_applied": glossary_applied,
        "source_hashtags": hashtags(title_raw),
        "uploader": to_traditional(field(report, "Uploader")) if to_zh_tw else field(report, "Uploader"),
        "duration": field(report, "Duration"),
        "detail": args.detail,
        "cue_timestamps": cue_timestamps,
        "resolution": resolution,
        "transcript_source": transcript_source,
        "question": args.question,
        "first_archived": prev.get("first_archived", dt.date.today().isoformat()),
        "last_updated": dt.date.today().isoformat(),
        "known_asr_errors": prev.get("known_asr_errors", []),  # hand-curated: never overwrite
        "keywords": prev.get("keywords", []),  # hand-curated: never overwrite
        "section_keywords": prev.get("section_keywords", {}),  # keyed by frame start time
        "slides": prev.get("slides", []),  # hand-curated: one entry per slide, overrides per-frame sections
        "video_type": prev.get("video_type", ""),  # hand-curated: "tutorial" for a screen-operation tutorial
        "clean_fillers": fillers_mode,
        "sop_mode": resolve_sop_mode(args.sop, args.no_sop, prev.get("sop_mode", early_meta.get("sop_mode", ""))),
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
    old_frames = json.loads((dest / "frames.json").read_text(encoding="utf-8")) if (dest / "frames.json").exists() else []
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
    if meta["slides"] and saved:
        meta["slides"] = remap_slide_frames(meta["slides"], old_frames, saved)
        (dest / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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
    if forced_language(lang):
        print(f"WARNING: --lang {forced_language(lang)} was forced to Whisper, so a wrong language would NOT be caught; "
              "if the audio is another language the transcript will be garbage. Rerun without --lang if unsure.", file=sys.stderr)
    if detected_language == "zh":
        print(f"language: zh [{language_source}]（已轉繁體 zh-TW）")
    elif detected_language == "unknown":
        print("language: unknown（逐字稿太短或缺失，請自行判斷是否需要中譯）")
    elif detected_language == "other":
        print("language: other（混雜或無法判斷）：已跳過簡轉繁；請讀逐字稿確認，中文請手動轉繁體，非中文請依 SKILL 步驟 4b 寫 transcript.zh.md")
    else:
        print(f"language: {detected_language} [{language_source}] -> 非中文影片：請依 SKILL 步驟 4b 寫 transcript.zh.md（繁體中文中譯，時間戳沿用原文）")


def remap_slide_frames(slides: list, old_frames: list, new_frames: list) -> list:
    """Point each slide at the new frame closest in time to the frame it used before.

    frames/ is rebuilt on every run and its files are renumbered (frame_0013 may become another moment), so a slide's
    'frame' is resolved through the old frames.json time. Slides whose old frame time is unknown fall back to their
    own start time.
    """
    old_t = {f["file"]: build_report.to_sec(f["t"]) for f in old_frames if f.get("file") and f.get("t")}
    new = [(build_report.to_sec(f["t"]), f["file"]) for f in new_frames if f.get("file") and f.get("t")]
    if not new:
        return slides
    out = []
    for sl in slides:
        target = old_t.get(sl.get("frame"), build_report.to_sec(sl["start"]) if sl.get("start") else None)
        if target is None:
            out.append(sl)
            continue
        out.append({**sl, "frame": min(new, key=lambda tf: abs(tf[0] - target))[1]})
    return out


def update_index(dest: Path, meta: dict):
    idx = OUT_ROOT / "index.md"
    header = ("# watch-output 索引\n\n"
              "| 日期 | 領域 | 平台 | 標題 | 長度 | 轉錄來源 | 資料夾 |\n|---|---|---|---|---|---|---|\n")
    rows = []
    if idx.exists():
        rows = [l for l in idx.read_text(encoding="utf-8").splitlines()
                if l.startswith("| ") and not l.startswith("| 日期") and f"__{meta['video_id']}/" not in l]
    safe_title = meta["title"].replace("|", "｜")
    rel = dest.relative_to(OUT_ROOT).as_posix()
    rows.append(f"| {meta['last_updated']} | {meta.get('category', DEFAULT_CATEGORY)} | {meta['platform']} | {safe_title} | "
                f"{meta['duration']} | {meta['transcript_source']} | [開啟](./{rel}/) |")
    idx.write_text(header + "\n".join(sorted(rows, key=lambda r: (r.split(" | ")[1], r.split(" | ")[0]))) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
