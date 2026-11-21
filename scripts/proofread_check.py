#!/usr/bin/env python3
"""第二輪校稿的機械檢查（只列清單，不改檔；要人工判斷）。

檢查 <資料夾>/transcript.md 的逐字稿行：
  簡體殘留     轉成繁體後字會變的字（OpenCC s2tw；「台」等台灣通用字除外）
  用語         台灣不常用的詞（賬、平臺、軟件、信息…）
  誤轉         已知的 OpenCC 誤轉（范式→正規化 等）
  疑似錯字     隻+要／能／有…（應為只）、AI AI 這類口吃重複
  指稱混用     同一支影片「他／她」混用（人物指稱可能不一致）
  重複行       相鄰兩行完全相同

這支腳本只做機械部分。第二輪仍要用 Read 從頭到尾逐行重讀（見
.claude/skills/watch-archive/references/proofread.md），改完後標記完成：

Usage:
  python3 scripts/proofread_check.py watch-output/<領域>/<資料夾>
  python3 scripts/proofread_check.py watch-output/<領域>/<資料夾> --mark-done --fixes 16 [--note "說明"]

--mark-done 會在 meta.json 寫 second_pass: {done, date, fixes, note}；
review_links.py 會檢查這個欄位（2026-11-21 起歸檔的影片沒標記就不給確認連結）。
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

LINE_RE = re.compile(r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s?(.*)$")

# 台灣不常用的詞 → 建議（只是提示，人名／引文可保留）
TERMS = {
    "賬": "帳", "平臺": "平台", "軟件": "軟體", "信息": "資訊", "視頻": "影片",
    "默認": "預設", "質量": "品質（若指品質）", "網絡": "網路", "文檔": "文件",
    "程序": "程式", "內存": "記憶體", "硬盤": "硬碟", "鼠標": "滑鼠", "激活": "啟用",
}
# 已知 OpenCC s2twp 誤轉
MISCONVERT = {"正規化": "範式（若原意為 范式）", "連接符": "連接符號", "重新整理": "刷新（若指創新高／刷新紀錄）"}
# 台灣也通用、但 OpenCC 會當成簡體的字
TW_OK = set("台")
# 隻 後接這些字多半是「只」
ZHI_NEXT = "要能有是會需好用看想說可得放買賣做剩"


def load_lines(folder: Path):
    p = folder / "transcript.md"
    if not p.exists():
        sys.exit(f"找不到 {p}")
    rows = []
    for no, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        m = LINE_RE.match(raw.strip())
        if m:
            rows.append((no, m.group(1), m.group(2)))
    return rows


_CC = None


def simplified_residue(text: str):
    global _CC
    try:
        import opencc
    except ImportError:
        return []
    if _CC is None:  # 建一次就好（每字重建會慢幾十倍）
        _CC = opencc.OpenCC("s2tw")
    out = []
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff" and ch not in TW_OK:
            t = _CC.convert(ch)
            if t != ch:
                out.append((ch, t))
    return out


def check(folder: Path):
    rows = load_lines(folder)
    findings = []  # (line_no, time, kind, message)
    he = she = 0
    prev = None
    for no, t, text in rows:
        for ch, tr in simplified_residue(text):
            findings.append((no, t, "簡體殘留", f"「{ch}」→「{tr}」"))
        for w, s in TERMS.items():
            if w in text:
                findings.append((no, t, "用語", f"「{w}」→「{s}」"))
        for w, s in MISCONVERT.items():
            if w in text:
                findings.append((no, t, "誤轉", f"「{w}」→「{s}」"))
        for m in re.finditer(r"隻([%s])" % ZHI_NEXT, text):
            findings.append((no, t, "疑似錯字", f"「隻{m.group(1)}」應為「只{m.group(1)}」"))
        for m in re.finditer(r"\b([A-Za-z]{2,})\s+\1\b", text):
            findings.append((no, t, "口吃重複", f"「{m.group(0)}」"))
        for m in re.finditer(r"([一-鿿]{2,4})\1", text):
            findings.append((no, t, "口吃重複", f"「{m.group(0)}」（若非刻意強調）"))
        he += text.count("他")
        she += text.count("她")
        if prev is not None and text == prev and text:
            findings.append((no, t, "重複行", f"與上一行相同：{text[:20]}"))
        prev = text
    if she >= 1 and he >= 3:
        findings.append((0, "", "指稱混用", f"他×{he}／她×{she}：若同一人物被稱「他」又稱「她」，請統一（指 AI 的「他」可保留）"))
    return rows, findings


def mark_done(folder: Path, fixes: int, note: str):
    mp = folder / "meta.json"
    meta = json.loads(mp.read_text(encoding="utf-8"))
    meta["second_pass"] = {"done": True, "date": datetime.date.today().isoformat(), "fixes": fixes, "note": note}
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"second_pass: done（修正 {fixes} 處）已寫入 {mp}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--mark-done", action="store_true", help="第二輪逐行重讀完成後標記")
    ap.add_argument("--fixes", type=int, default=0, help="第二輪修正處數")
    ap.add_argument("--note", default="")
    args = ap.parse_args()
    folder = Path(args.folder)
    if args.mark_done:
        mark_done(folder, args.fixes, args.note)
        return
    rows, findings = check(folder)
    print(f"proofread_check: {folder.name} — {len(rows)} 行，{len(findings)} 項提示")
    for no, t, kind, msg in findings:
        loc = f"L{no} [{t}]" if no else "全片"
        print(f"  {loc} {kind}：{msg}")
    sp = {}
    try:
        sp = json.loads((folder / "meta.json").read_text(encoding="utf-8")).get("second_pass") or {}
    except Exception:
        pass
    if sp.get("done"):
        print(f"second_pass: 已完成（{sp.get('date', '')}，修正 {sp.get('fixes', 0)} 處）")
    else:
        print("second_pass: 尚未完成 → 用 Read 從頭到尾逐行重讀 transcript.md，改完再跑 --mark-done")


if __name__ == "__main__":
    main()
