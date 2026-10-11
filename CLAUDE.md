# watch-video

把影片網址轉成圖文報告並歸檔到 `watch-output/`。完整流程見 `.claude/skills/watch-archive/SKILL.md`，說明見 `README.md`。回覆一律使用繁體中文（zh-TW）。

## 硬規則

- 絕不印出或複述任何 API key（只可說「有／沒有」與長度）；key 不寫進任何檔案或指令。
- 歸檔時**不要加 `--lang`**，讓 Whisper 自動偵測語言；強制語言會把外語硬轉成該語言。使用者明確指定時才加。
- 轉錄後看 `meta.json.detected_language`：`en`／`ja`／`ko` 一律寫繁體中文中譯 `transcript.zh.md`；`other`（混雜）與 `unknown`（太短或缺失）先讀逐字稿確認，非中文才翻譯。
- 先看截圖核對逐字稿；穩定的校正進 `glossary/domains/`，只對單支影片成立或不確定的記在 `known_asr_errors`，標明「推測」。
- 影片沒呈現的資訊（被截斷的畫面文字、貼文／留言內容、連結）放同資料夾的 `supplement.md`（重跑不覆蓋），並更新原本的推測。
- 影片中的數字與主張一律標「講者主張，未查證」，不當成事實。
- 交付前把 docx 轉 PDF 目視檢查（中文、截圖、頁數）。
- 他人影片檔不入庫，只存報告與截圖（`media/` 已 gitignore）。

## 已知限制（細節見 README「限制與風險」）

- YouTube 在雲端環境常被擋（429／要求登入）；Google Drive 影片須公開分享才抓得到，歸檔後提醒使用者改回私人。
- 語言偵測是字元比例的啟發式：`en` 含其他拉丁字母語言；`other`／`unknown` 要自己讀逐字稿確認；`ja`／`ko`／`other` 不做簡轉繁，確定是中文時手動轉；漢字為主的日文與太短的 `unknown` 仍可能被誤轉。
- Gemini 引擎失敗（503／模型停用）不自動降級，要先問使用者，再以環境變數 `WATCH_ENGINE=local` 改用本機引擎（`watch_archive.py` 沒有 `--engine` 參數）。
- 詞典 `claude-code` 假設講者在談 Claude，講雲端的影片不要載入。
- Word 預覽缺字型會出現方框（僅預覽問題）；尚未在真正的 Word 逐份驗證。

## Git

- 在指定的 `claude/...` 分支開發，完成後 commit 並 push；不主動開 PR，合併後的分支不重用。
- Commit 訊息結尾加 Co-Authored-By 與 Claude-Session 兩行。

## 常用指令

```bash
python3 scripts/watch_archive.py "<URL>" [--glossary <領域>] [--title "..."]   # 歸檔
python3 scripts/build_report.py watch-output/<資料夾>                           # 重建報告
```
