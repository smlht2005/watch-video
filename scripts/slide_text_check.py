#!/usr/bin/env python3
"""比對 supplement.md 的投影片原文與逐字稿，列出「近似但不相同」的片段（疑似聽錯字）。

用法：python3 scripts/slide_text_check.py watch-output/<領域>/<資料夾> [--min 0.6]
投影片文字是人眼讀到的原文，逐字稿是 ASR；兩者相近卻不相同時，多半是 ASR 聽錯，
以投影片為準（引文、經句、人名、術語）。結果只是提示，每一處仍要人工判斷。
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

CLAUSE_SPLIT = re.compile(r"[，。、；：？！,.;:?!（）()「」『』\s•\-]+")


def clauses(supplement: str, min_len: int = 5) -> list[str]:
    out = []
    for line in supplement.splitlines():
        if line.startswith(("#", ">")) or not line.strip():
            continue
        for c in CLAUSE_SPLIT.split(line):
            if len(c) >= min_len and c not in out:
                out.append(c)
    return out


def transcript_lines(text: str) -> list[tuple[str, str]]:
    out = []
    for line in text.splitlines():
        m = re.match(r"\[(\d+:\d{2}(?::\d{2})?)\]\s*(.*)", line)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def find_near_misses(clause_list, lines, min_ratio=0.5):
    """同長度視窗逐字比對：同位置相同字數達門檻、但不完全相同者，視為疑似聽錯。

    ASR 聽錯多是同音／近音的「代換」，長度不變，所以只比同長度視窗；
    投影片子句在別處出現過完全相同的說法也不放過（同一句可能一處對、一處錯）。
    """
    hits = []
    n = len(lines)
    for c in clause_list:
        need = max(2, -(-int(len(c) * min_ratio * 100) // 100))
        for i in range(n):
            txt = re.sub(r"[\s，。、！？：；,.]+", "", lines[i][1] + (lines[i + 1][1] if i + 1 < n else ""))
            best = None
            for st in range(0, len(txt) - len(c) + 1):
                seg = txt[st:st + len(c)]
                if seg == c:
                    continue
                same = sum(x == y for x, y in zip(c, seg))
                if same >= need and (best is None or same > best[0]):
                    best = (same, seg)
            # 排除該行本身已含完整子句的情況
            if best and c not in txt:
                hits.append((lines[i][0], c, best[1], best[0] / len(c)))
    seen, out = set(), []
    for h in hits:  # 同一子句與同一聽到的字串只列第一次
        if (h[1], h[2]) not in seen:
            seen.add((h[1], h[2]))
            out.append(h)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("folder")
    ap.add_argument("--min", type=float, default=0.5, dest="min_ratio")
    a = ap.parse_args(argv)
    d = Path(a.folder)
    sup = (d / "supplement.md").read_text(encoding="utf-8")
    lines = transcript_lines((d / "transcript.md").read_text(encoding="utf-8"))
    hits = find_near_misses(clauses(sup), lines, a.min_ratio)
    if not hits:
        print("沒有近似但不相同的片段")
        return 0
    for t, slide, heard, r in sorted(hits):
        print(f"[{t}] 投影片「{slide}」 ↔ 逐字稿「{heard}」（相似度 {r:.2f}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
