# 步驟 2：歸檔

2. **歸檔**：
   `python3 scripts/watch_archive.py "<URL>" [--category <領域>] [--glossary a,b] [--title "..."] [--terms "..."] [--clean-fillers|--keep-fillers] [--timestamps "MM:SS,…"] [--resolution 1024] [--keep-media] [--sop|--no-sop] [--local] [--question "..."]`
   - **不要加 `--lang`**（讓 Whisper 自動偵測）；只有使用者明確指定，或已確認整支同一語言且自動偵測不準時才加，見 `.claude/skills/watch-archive/references/params.md`。`--local`（本地 WhisperX）在雲端不可用。
   - 內部依序：解析平台與影片 ID（TikTok 短網址會先解析）→ 下載 → 平台字幕，或 Whisper 轉錄（Groq 帶語言與詞典提示詞；`--local` 時本地 WhisperX，只帶語言）→ 簡轉繁（OpenCC `s2twp`）→ 半形標點轉全形 → 詞典固定替換 → 截圖 → 寫檔 → 建報告。
   - 資料夾 `watch-output/<領域>/<日期>_<平台>_<標題>__<影片ID>/`（領域用 `--category` 指定，只接受 `glossary/categories.json` 白名單的值；未指定則取第一個詞典檔的 `category`，否則「未分類」並印 WARNING，歸檔後請確認分類合適；`index.md` 依領域分節）；同一影片 ID 只會有一個資料夾（重跑 = 更新；標題變動時資料夾會改名）。
   - 產出：`meta.json`、`transcript.md`（繁體）、`transcript.raw.md`（轉換前）、`frames/`、`frames.json`、`summary.md`（待補範本）、`transcript.zh.md`（外語影片才由 Claude 補寫）、`supplement.md`（選用：影片未呈現的補充資料）、`sop.md`（選用：教學影片的操作 SOP，見 4d）、`<stem>_report.md`、`<stem>_report.docx`，有 SOP 時另有 `<影片標題>_操作SOP.docx／.md` 與 `kb/`。`<stem>` = `<日期>_<平台>_<標題前20字>__<ID>`。
   - 語言判斷順序：Whisper 回報的語言（Whisper 轉錄時）→ 否則（平台字幕、強制 `--lang`）以字數／字元比例判斷（此時 `en` 代表拉丁字母的非中文，西班牙文等也會標成 `en`）→ 中文轉繁體（OpenCC）／非中文留給步驟 4b 中譯。
   - `--keep-media` 才保留 `media/<stem>_video.<ext>`；影片只存本機（gitignore）。
