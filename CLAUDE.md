# watch-video

把影片網址轉成圖文報告並歸檔到 `watch-output/`。完整流程見 `.claude/skills/watch-archive/SKILL.md`，說明見 `README.md`。回覆一律使用繁體中文（zh-TW）。

## 硬規則

- 絕不印出或複述任何 API key（只可說「有／沒有」與長度）；key 不寫進任何檔案或指令。
- 歸檔時**不要加 `--lang`**，讓 Whisper 自動偵測語言；強制語言會把外語硬轉成該語言。使用者明確指定時才加。
- 轉錄後看 `meta.json.detected_language`（`language_source` 說明來源）：任何已知的非中文語言（`en`／`ja`／`ko`／`es`…）一律寫繁體中文中譯 `transcript.zh.md`；`other`（混雜）與 `unknown`（太短或缺失）先讀逐字稿確認，非中文才翻譯。
- 先看截圖核對逐字稿；穩定的校正進 `glossary/domains/`，只對單支影片成立或不確定的記在 `known_asr_errors`，標明「推測」。
- 校稿分兩輪：第一輪批次替換後，第二輪用 Read 從頭到尾逐行重讀全文（片頭標題、接縫句、相鄰行的同一錯字最常漏），再在 PDF 搜尋改過的錯字確認不剩。
- 影片沒呈現的資訊（被截斷的畫面文字、貼文／留言內容、連結）放同資料夾的 `supplement.md`（重跑不覆蓋），並更新原本的推測。
- 影片中的數字與主張一律標「講者主張，未查證」，不當成事實。
- 報告分段：每段 2–4 分鐘、不超過約 5 分鐘，每段都要有一張屬於該段內容的截圖。
- 長的螢幕錄影／notebook／投影片影片（自動抽圖會跳過緩慢捲動的畫面）：先歸檔一次、讀逐字稿找出各主題開始時間，在每個時間點後約 20–40 秒放 cue（避開標題卡與轉場），以 `--timestamps "MM:SS,…,H:MM:SS" --resolution 1024` 重跑；兩值記在 `meta.json`，`slides` 的圖檔會依時間自動對應。重跑後先拼縮圖檢查每張 cue 截圖都有內容。
- 轉錄完先驗收再校稿：語言對不對、有沒有重複幻覺、有沒有約 30 秒的整段漏轉（`whisper.py` 已自動補漏，看 `[watch] refilled` 訊息）、有沒有提示詞外洩。要重跑時，先保存舊稿以便互補。
- 報告截圖只放乾淨的畫面：講者與投影片交疊的轉場不要用，改挑投影片全螢幕的畫面（做法見 SKILL 4a）。
- 影片在帶讀某份講稿時，用原講稿做二次校對；原稿沒有的內容是影片主講者的延伸，不能用原稿去改。
- 交付前把 docx 轉 PDF 目視檢查（中文、截圖、頁數）。
- 他人影片檔不入庫，只存報告與截圖（`media/` 已 gitignore）。

## 已知限制（細節見 README「限制與風險」）

- YouTube 在雲端環境常被擋（429／要求登入）；Google Drive 影片須公開分享才抓得到，歸檔後提醒使用者改回私人。
- 語言優先採用 Whisper 回報的語言；平台字幕與強制 `--lang` 時才用字元比例啟發式（`en` 含其他拉丁字母語言）；`other`／`unknown` 要自己讀逐字稿確認；`ja`／`ko`／`other` 不做簡轉繁，確定是中文時手動轉；漢字為主的日文與太短的 `unknown` 仍可能被誤轉。
- `watch_archive.py` 預設以本機引擎執行（`WATCH_ENGINE` 未設時為 `local`），因為歸檔需要截圖與逐字稿，Gemini 引擎只回傳文字答案、會產生空報告。要改用 Gemini 才設 `WATCH_ENGINE=gemini`；Gemini 失敗（503／模型停用）不自動降級，先問使用者。
- 轉錄方式：有 Groq key（環境變數或 `~/.config/watch/.env`）預設用 Groq；`--local` 改用本地 WhisperX，並記在 `meta.json.whisper_choice`，重跑會沿用。雲端只能用 Groq：容器沒有 WhisperX，不要加 `--local`。WhisperX 收不到詞典提示詞，專有名詞要在校稿時多留意。
- 本地 WhisperX（`small`）自動偵測語言不可靠：曾把中文講座判成日文並翻成日文，還有大量重複幻覺。中文影片優先用 Groq，或加 `--lang zh`。
- Windows 本機：要設 `PYTHONUTF8=1`（否則 `watch_archive.py` 解碼中文輸出失敗）；YouTube 擋下載時只能用 Firefox cookies（Chrome／Edge 的 App-Bound 加密 yt-dlp 解不開）；使用者開著 Word 時 `build_report.py` 會 `PermissionError`，請使用者關掉。
- 重跑 `watch_archive.py` 會清空 `frames/`，手動加的 `slide_NN.jpg` 會消失，要重做。
- 詞典 `claude-code` 假設講者在談 Claude，講雲端的影片不要載入；佛學講座用 `pure-land`。
- Word 預覽缺字型會出現方框（僅預覽問題）；尚未在真正的 Word 逐份驗證。

## Git

- 在指定的 `claude/...` 分支開發，完成後 commit 並 push；不主動開 PR，合併後的分支不重用。
- Commit 訊息結尾加 Co-Authored-By 與 Claude-Session 兩行。

## 常用指令

```bash
python3 scripts/watch_archive.py "<URL>" [--glossary <領域>] [--title "..."] [--timestamps "MM:SS,..."] [--resolution 1024] [--local]   # 歸檔
python3 scripts/build_report.py watch-output/<資料夾>                           # 重建報告
```
