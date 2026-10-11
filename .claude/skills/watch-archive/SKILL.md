---
name: watch-archive
description: 看影片並歸檔成圖文報告。使用者給影片網址（Facebook/YouTube 等），要求「看影片、摘要、逐字稿、轉 Word、歸檔」時使用。產出 watch-output/<資料夾>/ 內的 report.docx、report.md、截圖與 meta.json。
---

# watch-archive：影片 → 圖文報告（Word / Markdown）

回覆一律使用繁體中文（zh-TW）。**絕不印出或複述任何 API key**（只可說「有/沒有」與長度）。

## 流程

1. **環境**：確認 `GROQ_API_KEY` 存在（只報有/沒有）。若 `.claude/skills/watch` 尚未設定，先跑
   `python3 .claude/skills/watch/scripts/setup.py --backend groq --detail balanced`（exit 0）。
2. **歸檔**：`python3 scripts/watch_archive.py "<URL>" [--question "..."] [--keep-media]`
   - 資料夾：`watch-output/<日期>_<平台>_<標題>__<影片ID>/`；同一影片 ID 只會有一個資料夾（重跑 = 更新）。
   - 自動產生：`meta.json`、`transcript.md`、`frames/`、`frames.json`、`summary.md`（待補範本）、
     `<stem>_report.md`、`<stem>_report.docx`。`<stem>` = `<日期>_<平台>_<標題前20字>__<ID>`。
   - `--keep-media` 才保留 `media/<stem>_video.mp4`；影片只存本機（已 gitignore），報告內附來源網址超連結。
3. **人工/Claude 補充內容**（腳本不會自動做）：
   - 讀 `transcript.md` 與 `frames/`（用 Read 看圖），改寫 `summary.md`：含時間戳重點表、名詞與縮寫說明。
   - 編輯 `meta.json`（重跑時這些欄位會保留，不會被覆蓋）：
     - `keywords`：整份關鍵字（約 8–10 個）。
     - `section_keywords`：以畫面起始時間為 key，如 `{"00:12": ["上下文限制"]}`。
     - `known_asr_errors`：`[{"time","heard","expected"}]`，書名/人名可用畫面文字核對。
4. **重建報告**：`python3 scripts/build_report.py watch-output/<資料夾>`
5. **目視檢查**：docx 轉 PDF 後看頁面（中文、截圖是否正常）。
6. **交付**：用 SendUserFile 傳 `*_report.docx`；摘要重點與「是否為 Groq 轉錄（非字幕）」寫在回覆裡。
7. **提交**：在 `claude/...` 分支 commit（不要直接動 main）；除非使用者要求，不建立 PR、不強制 push。

## 注意

- 逐字稿來源在 `meta.json.transcript_source`（`whisper (groq)` = 語音轉錄；否則為平台字幕）。
- **逐字稿預設繁體中文（zh-TW）**：腳本用 OpenCC（s2twp）把簡體轉繁體；轉換前的原文存成 `transcript.raw.md`。需先 `pip install opencc-python-reimplemented`，缺少時腳本會警告並保留原文。
- Groq 轉錄可能有誤聽（同音字、英文縮寫）；校正寫進 `known_asr_errors`，**不要手改 `transcript.md`**（原始轉錄在 `transcript.raw.md`）。
- 失敗時回報錯誤類別與原因（網路/下載/轉錄/權限），不要印出 key。
- 版權：來源是他人影片；repo 設為 private 時僅供個人參考，改 public 或分享前不要附影片。
