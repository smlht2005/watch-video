#!/usr/bin/env python3
"""List repeated phrases across adjacent transcript lines (the end of line i also starts line i+1).

clean_fillers.py merges in-line stutters automatically; a repeat across two lines may be a stutter (delete) or the
speaker's deliberate emphasis (keep), so this only prints candidates for a human to judge.

Usage: python3 scripts/stutter_check.py watch-output/<領域>/<資料夾> [--min 3]
"""
import re
import sys
from pathlib import Path

SEG_RE = re.compile(r"^\[(\d+:\d+(?::\d+)?)\]\s*(.*)$")
PUNCT = "，。、？！；：「」『』（） "


def load_lines(text: str):
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
        m = SEG_RE.match(line.strip()) if in_fence else None
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def find_overlaps(lines, min_len=3):
    """(ts_a, ts_b, phrase): the longest tail of line a equal to the head of line b, ignoring punctuation."""
    res = []
    for (ta, a), (tb, b) in zip(lines, lines[1:]):
        a2 = a.strip(PUNCT)
        b2 = b.strip(PUNCT)
        for n in range(min(len(a2), len(b2), 12), min_len - 1, -1):
            if a2[-n:] == b2[:n]:
                res.append((ta, tb, a2[-n:]))
                break
    return res


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    min_len = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 3
    args = [a for a in args if a != str(min_len)]
    for folder in args:
        lines = load_lines((Path(folder) / "transcript.md").read_text(encoding="utf-8"))
        hits = find_overlaps(lines, min_len)
        for ta, tb, ph in hits:
            print(f"[{ta}]→[{tb}] {ph}")
        print(f"{folder}: {len(hits)} cross-line repeat(s) to judge")
