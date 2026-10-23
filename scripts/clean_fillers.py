#!/usr/bin/env python3
"""Remove meaningless Chinese filler particles (呢、啊、clause-final 啦／嘛／喔／哦／囉) from transcript.md.
Also merges in-line stutters ("逢人 逢人"、"那個那個") and turns the pause spaces Whisper leaves between Chinese
characters into "，" so the written transcript has clear punctuation. Repeats across lines are only listed by
scripts/stutter_check.py (they may be deliberate emphasis).

Speech-style lectures are full of "你看啊"、"這個呢" which only make the written transcript harder to read. The ASR
output is not touched (transcript.raw.md stays as is); only the "[mm:ss] text" lines inside the fenced block of
transcript.md are cleaned, so headings, notes and everything else are left alone. The step is idempotent.

A rerun of watch_archive.py rewrites transcript.md, so run this again after proofreading (.claude/skills/watch-archive/references/proofread.md).

Usage: python3 scripts/clean_fillers.py watch-output/<folder> [<folder> ...]
"""
import re
import sys
from pathlib import Path

SEG_RE = re.compile(r"^\[(\d+:\d+(?::\d+)?)\]\s*(.*)$")
# words that contain a filler character but are not fillers (mantra, mumbling, wool cloth)
PROTECT = ["嘛呢叭咪吽", "嘛呢", "呢喃", "毛呢", "呢絨"]
CLAUSE_END = "，。、？！；：…）」』"
CJK = r"[㐀-鿿]"
# a repeat joined only by a pause space is a stutter; "一個一個"、"每個每個" style distributive repeats are kept
DISTRIB = "一二三四五六七八九十每各第"
# stutter with no separator, only for words that are never meant doubled
ADJ_WORDS = ["那個", "這個", "所以", "就是", "然後", "因為", "如果", "但是", "可是", "我們", "你們", "他們"]


def merge_stutters(text: str) -> str:
    def sep_repeat(m):
        return m.group(0) if m.group(1)[0] in DISTRIB else m.group(1)
    prev = None
    while prev != text:  # repeat until stable: "A A A" -> "A A" -> "A"
        prev = text
        text = re.sub(rf"({CJK}{{2,12}}?)[ 　]+\1", sep_repeat, text)  # comma repeats ("忽，忽就是忽視") may be definitions: stutter_check.py lists them
    for w in ADJ_WORDS:
        text = re.sub(rf"(?:{w}){{2,}}", w, text)
    return text


def pause_spaces_to_commas(text: str) -> str:
    return re.sub(rf"(?<={CJK})[ 　]+(?={CJK})", "，", text)


def strip_fillers(text: str) -> str:
    for i, word in enumerate(PROTECT):
        text = text.replace(word, f"\x00{i}\x00")
    text = text.replace("呢", "")
    text = re.sub(r"啊(?![彌難羅賴含])", "", text)  # 啊彌陀／啊難／啊賴耶 are mis-heard 阿…: keep for the proofreader
    text = re.sub(rf"[啦嘛喔哦囉]+(?=[{CLAUSE_END}]|$)", "", text)  # only when clause-final: 囉嗦／啦啦隊 stay
    for i, word in enumerate(PROTECT):
        text = text.replace(f"\x00{i}\x00", word)
    text = merge_stutters(text)
    text = pause_spaces_to_commas(text)
    text = re.sub(r"[，、]{2,}", "，", text)
    text = re.sub(r"，(?=[。？！；])", "", text)
    text = re.sub(r"^[，、。；：]+", "", text)
    return text.strip()


def clean_text(raw: str):
    """Clean the "[mm:ss] text" lines inside the fenced block of a transcript. Returns (text, changed, dropped)."""
    out, in_fence, changed, dropped = [], False, 0, 0
    for line in raw.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        m = SEG_RE.match(line.strip()) if in_fence else None
        if not m:
            out.append(line)
            continue
        new = strip_fillers(m.group(2))
        if new == m.group(2):
            out.append(line)
        elif new:
            out.append(f"[{m.group(1)}] {new}")
            changed += 1
        else:
            dropped += 1
    return "\n".join(out), changed, dropped


def clean_file(path: Path):
    """Clean a transcript.md in place. Returns (lines changed, lines dropped)."""
    text, changed, dropped = clean_text(path.read_text(encoding="utf-8"))
    if changed or dropped:
        path.write_text(text, encoding="utf-8")
    return changed, dropped


if __name__ == "__main__":
    for folder in sys.argv[1:]:
        changed, dropped = clean_file(Path(folder) / "transcript.md")
        print(f"{folder}: {changed} line(s) cleaned, {dropped} dropped")
