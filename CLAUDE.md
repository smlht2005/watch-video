# watch-video

把影片網址轉成圖文報告並歸檔到 `watch-output/`。完整流程見 `.claude/skills/watch-archive/SKILL.md`（只有骨架；各步驟細節在 `.claude/skills/watch-archive/references/`，開工前先讀對應檔），說明見 `README.md`。回覆一律使用繁體中文（zh-TW）。

## 硬規則

- 絕不印出或複述任何 API key（只可說「有／沒有」與長度）；key 不寫進任何檔案或指令。
- 歸檔時**不要加 `--lang`**，讓 Whisper 自動偵測語言；強制語言會把外語硬轉成該語言。使用者明確指定，或已確認整支同一語言而自動偵測不準時（例如本地 WhisperX 把中文講座判成日文）才加，如 `--lang zh`。
- 轉錄後看 `meta.json.detected_language`（`language_source` 說明來源）：任何已知的非中文語言（`en`／`ja`／`ko`／`es`…）一律寫繁體中文中譯 `transcript.zh.md`；`other`（混雜）與 `unknown`（太短或缺失）先讀逐字稿確認，非中文才翻譯。
- 先看截圖核對逐字稿；穩定的校正進 `glossary/domains/`，只對單支影片成立或不確定的記在 `known_asr_errors`，標明「推測」。
- 標為存疑的逐字稿行，先對照投影片再決定保留：`supplement.md` 寫好後跑 `python3 scripts/slide_text_check.py watch-output/<領域>/<資料夾>`，列出投影片子句與逐字稿近似但不同的行（引文、經句、人名以投影片為準；只是提示，要人工判斷）；見 `.claude/skills/watch-archive/references/proofread.md`。
- 講座／講經的口吃與標點：口音讓逐字稿有重複字（「逢人 逢人」）和停頓空格；`clean_fillers.py` 自動合併行內口吃、字間空格改「，」，跨行重複用 `python3 scripts/stutter_check.py watch-output/<領域>/<資料夾>` 列出後人工判斷（刻意強調的保留）；見 `.claude/skills/watch-archive/references/proofread.md`。
- 校稿分兩輪：第一輪批次替換後，第二輪用 Read 從頭到尾逐行重讀全文（片頭標題、接縫句、相鄰行的同一錯字最常漏），再在 PDF 搜尋改過的錯字確認不剩。
- 影片沒呈現的資訊（被截斷的畫面文字、貼文／留言內容、連結）放同資料夾的 `supplement.md`（重跑不覆蓋），並更新原本的推測。
- 影片中的數字與主張一律標「講者主張，未查證」，不當成事實。
- 報告要有思維導圖：4b 手寫 `mindmap.md`（縮排條列，最多 3 層：中心→主分支→子節點，每節點 15 字內，主分支約 10 個內，數字主張標「（講者主張）」）；`build_report.py` 畫成 `mindmap.png`，放在「圖文對照」之前並連結原圖與大綱。沒寫時由 `slides` 自動產生（第一行 auto 標記，重建會覆蓋）。SOP 與 `kb/` 不放；見 `.claude/skills/watch-archive/references/content.md` 4b。
- 報告分段：每段 2–4 分鐘、不超過約 5 分鐘，每段都要有一張屬於該段內容的截圖。**例外：影片明說步驟（第一輪…第六輪、1、2、3…點、「三招」）時，一個步驟＝一段＝一張圖＋一段完整說明（`note` 2–4 句），不受 2–4 分鐘限制；步驟前的開場／原理、步驟後的結語各自成段（結語約 10 秒內可併進最後一步）；見 `.claude/skills/watch-archive/references/content.md` 4a。**
- 長的螢幕錄影／notebook／投影片影片（自動抽圖會跳過緩慢捲動的畫面）：先歸檔一次、讀逐字稿找出各主題開始時間，在每個時間點後約 20–40 秒放 cue（避開標題卡與轉場），以 `--timestamps "MM:SS,…,H:MM:SS" --resolution 1024` 重跑；兩值記在 `meta.json`，`slides` 的圖檔會依時間自動對應。重跑後先拼縮圖檢查每張 cue 截圖都有內容。
- 轉錄完先驗收再校稿：語言對不對、有沒有重複幻覺、有沒有約 30 秒的整段漏轉（`whisper.py` 已自動補漏，看 `[watch] refilled` 訊息）、有沒有提示詞外洩。要重跑時，先保存舊稿以便互補。
- 報告截圖只放乾淨的畫面：講者與投影片交疊的轉場不要用，改挑投影片全螢幕的畫面（做法見 `.claude/skills/watch-archive/references/content.md` 4a）。
- 每段截圖要對到該段重點：用 `scripts/pick_frames.py sheet` 逐秒產生縮圖表與建議，**自己看圖確認對到 `note`** 再 `apply`；畫面上講者沒唸的提示詞／程式碼／對照表，用 `pick_frames.py text` 取原始解析度截圖與同時段逐字稿比對後，逐字抄進 `supplement.md`（`.claude/skills/watch-archive/references/content.md` 4a、`.claude/skills/watch-archive/references/supplement-4c.md`）。
- 影片在帶讀某份講稿時，用原講稿做二次校對；原稿沒有的內容是影片主講者的延伸，不能用原稿去改。
- 講座／講經（口語演講）：歸檔時加 `--clean-fillers`（`--glossary pure-land` 自動開啟，`meta.json.video_type: "lecture"` 重跑也會開），自動去除逐字稿的「呢」「啊」等語助詞；`--keep-fillers` 保留，`transcript.raw.md` 保留原話；見 `.claude/skills/watch-archive/references/proofread.md`。
- 電腦工具教學影片（螢幕操作示範）：消化報告後另寫 `sop.md`（依任務分章、編號步驟、按鈕名稱照畫面原文、截圖寫 `![說明](frame@MM:SS)`、沒示範的標「影片未示範」／「推測」），重建後有 `*_操作SOP.docx` 與可放進 Obsidian／Notion 的 `kb/`；見 `.claude/skills/watch-archive/references/sop-4d.md`。
- 字幕 OCR 很費時（74 分鐘的影片約一小時），**只用在佛經講解／講經座，且畫面有逐句燒入字幕**的影片，其他影片不用（先 `probe` 確認有字幕才 `run`）。用 OCR 抽字幕與逐字稿逐行比對校稿，專有名詞（人名、書名、術語）以字幕為準，不靠上下文推測；字幕是書面語、不是原話，只取差異處用字，不整句覆蓋；OCR 有簡繁／同音雜訊，每處人工判斷。先 `scripts/subtitle_ocr.py probe` 確認有字幕，再 `run`／`compare`；用法與比較見 `docs/subtitle-ocr-vs-whisper.md`。
- 交付前把 docx 轉 PDF 目視檢查（中文、截圖、頁數）。
- 歸檔完成並 push 到分支後，用 `python3 scripts/review_links.py watch-output/<領域>/<資料夾>` 產生連結給使用者確認；使用者確認前不開 PR、不 merge。
- 他人影片檔不入庫，只存報告與截圖（`media/` 已 gitignore）。

- 歸檔結果在 `watch-output/<領域>/<資料夾>/`；新影片歸檔時用 `--category` 指定領域，只能用白名單 `glossary/categories.json` 的值（AI／AI/claude-code／佛學／商業理財／身心生活／電子／雲端／未分類；收錄範圍、子領域與新增領域門檻見 `.claude/skills/watch-archive/references/params.md`）；沒指定會依詞典檔的 `category` 推測或落入「未分類」（印 WARNING），交付前確認。新增領域要先改白名單；領域名稱有中文時一律用繁體，不用簡體（輸入簡體會自動轉繁）。

## 已知限制（細節見 README「限制與風險」）

- YouTube 在雲端環境常被擋（429／要求登入）；Google Drive 影片須公開分享才抓得到，歸檔後提醒使用者改回私人。
- 語言優先採用 Whisper 回報的語言；平台字幕與強制 `--lang` 時才用字元比例啟發式（`en` 含其他拉丁字母語言）；`other`／`unknown` 要自己讀逐字稿確認；`ja`／`ko`／`other` 不做簡轉繁，確定是中文時手動轉；漢字為主的日文與太短的 `unknown` 仍可能被誤轉。
- `watch_archive.py` 預設以本機引擎執行（`WATCH_ENGINE` 未設時為 `local`），因為歸檔需要截圖與逐字稿，Gemini 引擎只回傳文字答案、會產生空報告。要改用 Gemini 才設 `WATCH_ENGINE=gemini`；Gemini 失敗（503／模型停用）不自動降級，先問使用者。
- 轉錄方式：有 Groq key（環境變數或 `~/.config/watch/.env`）預設用 Groq；`--local` 改用本地 WhisperX，並記在 `meta.json.whisper_choice`，重跑會沿用。雲端只能用 Groq：容器沒有 WhisperX，不要加 `--local`。WhisperX 收不到詞典提示詞，專有名詞要在校稿時多留意。
- 本地 WhisperX（`small`）自動偵測語言不可靠：曾把中文講座判成日文並翻成日文，還有大量重複幻覺。中文影片優先用 Groq，或加 `--lang zh`。
- Windows 本機：要設 `PYTHONUTF8=1`（否則 `watch_archive.py` 解碼中文輸出失敗）；YouTube 擋下載時只能用 Firefox cookies（Chrome／Edge 的 App-Bound 加密 yt-dlp 解不開）；使用者開著 Word 時 `build_report.py` 會 `PermissionError`，請使用者關掉。
- 重跑 `watch_archive.py` 會清空 `frames/`，手動加的 `slide_NN.jpg` 會消失，要重做；也會覆蓋手動補回的逐字稿，補漏後先備份。
- Groq 補漏遇 HTTP 429 限流會整段漏轉（曾漏約 17 分鐘）：歸檔後做字數密度掃描；漏了就把缺漏段切成每 30 秒，用 `whisper._transcribe_file('groq', key, path)` 單獨重送補回，再套簡轉繁、詞典、去語助詞。
- 詞典 `claude-code` 假設講者在談 Claude，講雲端的影片不要載入；佛學講座用 `pure-land`，楞嚴經講經用 `lengyan`（耳根圓通、十四無畏、四不思議）。
- Word 預覽缺字型會出現方框（僅預覽問題）；尚未在真正的 Word 逐份驗證。

## Agent skills

（`to-spec`／`to-tickets`／`implement` 等 mattpocock 技能的設定，由 `/setup-matt-pocock-skills` 產生；已設定好，新 session 不必重跑。）

### Issue tracker

工作項目以本機 markdown 存在 `.scratch/<feature>/`（spec.md、issues/NN-*.md），隨 repo commit。See `docs/agents/issue-tracker.md`.

### Domain docs

single-context：根目錄 `GLOSSARY.md` + `docs/adr/`（需要時才建立）。See `docs/agents/domain.md`.

## Git

- 在指定的 `claude/...` 分支開發，完成後 commit 並 push；不主動開 PR，合併後的分支不重用。
- 同一個 repo 可能有多個 session 同時切分支：commit、合併、切分支前先 `git branch --show-current`；Word 開著產生的 `~$*.docx` 鎖檔不要 commit。
- 長時間背景工作（轉錄、OCR、下載）每約 10 分鐘主動回報一次進度。
- Commit 訊息結尾加 Co-Authored-By 與 Claude-Session 兩行。

## 常用指令

```bash
python3 scripts/watch_archive.py "<URL>" [--glossary <領域>] [--category <領域>] [--title "..."] [--timestamps "MM:SS,..."] [--resolution 1024] [--local] [--sop|--no-sop] [--clean-fillers|--keep-fillers]   # 歸檔
python3 scripts/build_report.py watch-output/<領域>/<資料夾>                           # 重建報告
```
