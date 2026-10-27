# 05：文件、skill、記憶與全套測試

**What to build:** 更新 `.claude/skills/watch-archive/references/proofread.md`、`CLAUDE.md` 硬規則、`docs/subtitle-ocr-vs-whisper.md`（用法改成：佛學／講經、有燒入字幕、超過 30 分鐘自動分段，建議 `--segment-min 10 --workers 1 --every 3 --low-priority`、`status`、續跑、兩程序並行）、`docs/watch-archive-flow.png` 與 `references/notes.md` 文字版（如有 OCR 步驟）、`README.md`；更新記憶 `ocr-lessons.md`（改成指向內建功能、刪除手寫驅動腳本的說明）。PR 前跑全套 `python3 -m unittest discover -s tests`（含 test_watch_archive 對文件完整路徑引用的檢查）。

**Blocked by:** 01、02、03、04

**Status:** ready-for-agent

- [x] 文件與 skill 都改成分段為預設做法，並說明 v5 的建議參數
- [x] 流程圖與文字版同步
- [x] 記憶更新
- [x] 全套測試通過

## Comments
