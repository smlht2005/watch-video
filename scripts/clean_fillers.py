#!/usr/bin/env python3
"""Remove meaningless Chinese filler particles (呢、啊、clause-final 啦／嘛／喔／哦／囉) from transcript.md.

Speech-style lectures are full of "你看啊"、"這個呢" which only make the written transcript harder to read. The ASR
output is not touched (transcript.raw.md stays as is); only the "[mm:ss] text" lines inside the fenced block of
transcript.md are cleaned, so headings, notes and everything else are left alone. The step is idempotent.

A rerun of watch_archive.py rewrites transcript.md, so run this again after proofreading (SKILL step 3).

Usage: python3 scripts/clean_fillers.py watch-output/<folder> [<folder> ...]
"""
import re
import sys
from pathlib import Path

SEG_RE = re.compile(r"^\[(\d+:\d+(?::\d+)?)\]\s*(.*)$")
# words that contain a filler character but are not fillers (mantra, mumbling, wool cloth)
PROTECT = ["嘛呢叭咪吽", "嘛呢", "呢喃", "毛呢", "呢絨"]
CLAUSE_END = "，。、？！；：…）」』"


def strip_fillers(text: str) -> str:
    for i, word in enumerate(PROTECT):
        text = text.replace(word, f"\x00{i}\x00")
    text = text.replace("呢", "")
    text = re.sub(r"啊(?![彌難羅賴含])", "", text)  # 啊彌陀／啊難／啊賴耶 are mis-heard 阿…: keep for the proofreader
    text = re.sub(rf"[啦嘛喔哦囉]+(?=[{CLAUSE_END}]|$)", "", text)  # only when clause-final: 囉嗦／啦啦隊 stay
    for i, word in enumerate(PROTECT):
        text = text.replace(f"\x00{i}\x00", word)
    text = re.sub(r"[，、]{2,}", "，", text)
    text = re.sub(r"，(?=[。？！；])", "", text)
    text = re.sub(r"^[，、。；：]+", "", text)
    return text.strip()


def clean_file(path: Path):
    """Clean the segment lines of a transcript.md in place. Returns (lines changed, lines dropped)."""
    raw = path.read_text(encoding="utf-8")
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
    if changed or dropped:
        path.write_text("\n".join(out), encoding="utf-8")
    return changed, dropped


if __name__ == "__main__":
    for folder in sys.argv[1:]:
        changed, dropped = clean_file(Path(folder) / "transcript.md")
        print(f"{folder}: {changed} line(s) cleaned, {dropped} dropped")
