# watch-video

把影片網址轉成圖文報告並歸檔到 `watch-output/`。完整流程見 `.claude/skills/watch-archive/SKILL.md`，說明見 `README.md`。回覆一律使用繁體中文（zh-TW）。

## 硬規則

- 絕不印出或複述任何 API key（只可說「有／沒有」與長度）；key 不寫進任何檔案或指令。
- 歸檔時**不要加 `--lang`**，讓 Whisper 自動偵測語言；強制語言會把外語硬轉成該語言。使用者明確指定時才加。
- 轉錄後看 `meta.json.detected_language`；非中文（`needs_zh_translation`）一律寫繁體中文中譯 `transcript.zh.md`。
- 先看截圖核對逐字稿；穩定的校正進 `glossary/domains/`，只對單支影片成立或不確定的記在 `known_asr_errors`，標明「推測」。
- 影片沒呈現的資訊（被截斷的畫面文字、貼文／留言內容、連結）放同資料夾的 `supplement.md`（重跑不覆蓋），並更新原本的推測。
- 影片中的數字與主張一律標「講者主張，未查證」，不當成事實。
- 交付前把 docx 轉 PDF 目視檢查（中文、截圖、頁數）。
- 他人影片檔不入庫，只存報告與截圖（`media/` 已 gitignore）。

## Git

- 在指定的 `claude/...` 分支開發，完成後 commit 並 push；不主動開 PR，合併後的分支不重用。
- Commit 訊息結尾加 Co-Authored-By 與 Claude-Session 兩行。

## 常用指令

```bash
python3 scripts/watch_archive.py "<URL>" [--glossary <領域>] [--title "..."]   # 歸檔
python3 scripts/build_report.py watch-output/<資料夾>                           # 重建報告
```
