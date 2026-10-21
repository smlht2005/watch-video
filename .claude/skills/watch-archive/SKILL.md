---
name: watch-archive
description: 看影片並歸檔成圖文報告。使用者給影片網址（Facebook/YouTube/TikTok 等），要求「看影片、摘要、逐字稿、轉 Word、歸檔」時使用。網址後可加第二個參數：白名單內的領域（如 `/watch-archive <網址> 身心生活`）當領域，其他詞當主題關鍵字；沒指定領域時依詞典推測，沒把握建議先 /grill-me。產出 watch-output/<領域>/<資料夾>/ 內的 report.docx、report.md、截圖與 meta.json；逐字稿預設繁體中文，並用詞典校正。
---

# watch-archive：影片 → 圖文報告（Word / Markdown）

回覆一律使用繁體中文（zh-TW）。**絕不印出或複述任何 API key**（只可說「有/沒有」與長度）。

## 呼叫參數：`/watch-archive <影片網址> [領域或主題]`

- **第一個參數**：影片網址（必填）。
- **第二個參數（選填）**：先對照白名單 `glossary/categories.json`（目前 AI／佛學／商業理財／身心生活／電子／雲端／未分類；寫簡體會自動轉繁體，英文只差大小寫會校正）：
  - **對得上白名單 → 當成領域**：傳給 `watch_archive.py --category <領域>`，不必再推測。
  - **對不上 → 當成主題詞（例如「自律」）**：不報錯、不中斷。把它存進這支影片的 `meta.json.keywords`（步驟 4b 補內容時一起寫），領域則改由詞典或影片內容判斷（見下一點）。**回覆必須明講三件事**：這個詞沒有對應到任何領域；實際歸到哪個領域、依據是什麼；想指定領域時可用的值有哪些（這樣領域打錯字也不會悄悄歸錯，使用者看得出來）。
- **沒有指定領域時**：先看影片內容與所選詞典（`--glossary`）能否明確判斷（詞典檔的 `category` 欄位會自動推測）。能明確判斷就照該領域歸檔，並在回覆註明是推測；**沒把握就不要自行決定，建議使用者先跑 `/grill-me`** 釐清領域，不要悄悄放進「未分類」。
- **新增領域的規則**：同時符合 (a) 至少 5 支影片屬於同一個新主題、(b) 放在現有領域裡找不到合適位置，才新增；沒達標前，主題只用 `keywords` 標記，不開新資料夾（例：自律 → 歸 `身心生活`＋關鍵字「自律」；同一關鍵字累積到 5 支且有需要時再討論是否獨立）。要新增領域、或不確定新影片該歸哪個領域時，用 `/grill-me <要決定的事>`，結論寫進 `glossary/categories.json`（必要時再補詞典檔的 `category`）。
- **按關鍵字找影片**：目前不另建索引，搜尋各 `meta.json` 的 `keywords` 欄位即可。

## 流程總覽

![watch-archive 流程鳥瞰圖](../../../docs/watch-archive-flow.png)

```text
網址 ─▶ 0 環境 ─▶ 1 選參數(不強制 --lang；長錄影加 --timestamps/--resolution；本地轉錄加 --local；講座／講經加 --clean-fillers) ─▶ 2 歸檔(下載→平台字幕或 Groq／WhisperX 轉錄→偵測語言→中文轉繁體→詞典校正→(講座／講經)去語助詞→截圖→報告)
     ─▶ 3 校稿(先驗收：語言錯／重複幻覺／30 秒漏轉（已自動補漏）／提示詞外洩→保存舊稿後回到 2 重跑、兩次互補；第一輪批次替換→第二輪逐行重讀全文) ─▶ 4a 看截圖分投影片或主題(slides，每段 2–4 分鐘；pick_frames.py 逐秒挑「對到重點」的截圖並人工確認；截圖不足→補 cue 回到 2 重跑；講者交疊→改挑乾淨投影片)
     ─▶ 4b 補內容(摘要/關鍵字/校正；非中文→transcript.zh.md) ─▶ 4c 補充資料(選用 supplement.md；畫面有講者沒唸的原文→逐字抄進補充；有原講稿→二次校對) ─▶ 4d 電腦工具教學→操作 SOP(選用 sop.md) ─▶ 5 重建報告 ─▶ 5b 目視檢查 ─▶ 6 交付 ─▶ 7 提交＋給確認連結 ─▶ 使用者確認 ─▶ 8 PR＋merge
```

藍＝腳本自動、橘＝Claude 判斷、綠＝交付；黃色虛線是兩條重跑回圈：「截圖不足時補 cue 重跑」（4a→2）與「語言錯／整段漏轉時重跑」（3→2）；圖源 `docs/watch-archive-flow.svg`。改圖後重新產生 PNG：
- 雲端（Linux）：`/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox --hide-scrollbars --window-size=1600,1100 --screenshot=docs/watch-archive-flow.png file://$PWD/docs/watch-archive-flow.svg`，再用 PIL 裁成 1600×900（視窗外框會吃掉底部，故先開大再裁）。
- Windows：`"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu --hide-scrollbars --window-size=1600,900 --screenshot=<絕對路徑>\docs\watch-archive-flow.png file:///<絕對路徑>/docs/watch-archive-flow.svg`（直接 1600×900，不必裁）。微軟正黑體比文泉驛寬，改字後要看圖確認沒有超出方框。

## 步驟

0. **環境**：確認 Groq key 是否存在（環境變數 `GROQ_API_KEY` 或 `~/.config/watch/.env`；只報有/沒有與長度）。有就預設用 Groq 轉錄；沒有則依 `setup.py --json` 的 `whisper_backend`（例如本地 WhisperX），兩者都沒有時，無字幕影片會拿不到逐字稿，要先告知使用者。**雲端 session（`CLAUDE_CODE_REMOTE=true`）只能用 Groq**：容器沒有 WhisperX，不要加 `--local`；沒有 key 就先告知使用者到環境 secret 設定 `GROQ_API_KEY`。確認 `pip install python-docx opencc-python-reimplemented`。
   若 `.claude/skills/watch` 尚未設定，先跑 `python3 .claude/skills/watch/scripts/setup.py --engine local --backend groq --detail balanced`（沒有 Groq key 時把 `groq` 換成 `whisperx`）（exit 0；一定要帶 `--engine local`，否則有 `GEMINI_API_KEY` 時會改走 Gemini，不產生截圖與逐字稿）。
   從最新的 `main` 開新分支 `claude/...`（不要重用已合併的分支）。
   **Windows 本機**：
   - 所有 `python` 指令都要在 `PYTHONUTF8=1` 下執行（使用者環境變數；設定前開的 session 要在指令前加）。否則 `watch_archive.py` 會用 cp950 解碼 `watch.py` 的中文輸出，直接以 `TypeError: 'NoneType'` 失敗。
   - YouTube 回「Sign in to confirm you're not a bot」時，以 `WATCH_COOKIES_FROM_BROWSER=firefox` 只傳給這次執行（不寫進設定檔）。Windows 的 Chrome／Edge 有 App-Bound 加密，yt-dlp 會出現 `Failed to decrypt with DPAPI`，關掉瀏覽器也沒用，不要再試；沒有 Firefox 就請使用者匯出 cookies.txt（存在 repo 外）改用 `WATCH_COOKIES_FILE`。讀瀏覽器 cookies 前先問使用者。
   - Groq key 可能設在系統層級（Machine）環境變數，session 讀不到時用 `[Environment]::GetEnvironmentVariable('GROQ_API_KEY','Machine')` 取值，只傳給該次執行，不印出。

1. **選參數**（沒有把握就用預設）：
   - **語言：預設不加 `--lang`，讓 Whisper 自動偵測。** 強制 `--lang` 會讓任何語言都被硬轉成該語言（英文影片加 `--lang zh` 會得到不通順的中文，且無法事後偵測）。只有使用者明確指定、或已確認整支影片是同一種語言且自動偵測不準時才加；腳本會對強制語言印警告。
   - 語言優先採用 **Whisper 回報的語言**（報告表頭 `Whisper language`）；平台字幕來源與強制 `--lang` 時才從輸出文字判斷。寫入 `meta.json.detected_language`（`zh`／`ja`／`ko`／`en`／`es`…／`other`／`unknown`；每次重跑重新判斷）、`language_source`、`forced_lang` 與 `needs_zh_translation`（任何已知的非中文語言為 true；`other`／`unknown` 為 false），並在結尾印出 `language: …`。中文夾雜英文術語仍會判為 `zh`；`other`（混雜）與 `unknown`（逐字稿太短）要自己讀逐字稿確認：`other` 為避免改壞日韓文，**不會做簡轉繁**（`ja`／`ko` 同樣不轉），確定是中文時請手動轉繁體；`unknown` 仍照常轉換。平台有字幕時直接採用字幕，語言以字幕為準。
   - **轉錄方式**：預設不加。有 Groq key 時用 Groq；使用者要求本地轉錄（不上傳音訊）時加 `--local`（本地 WhisperX，雲端不可用）；要指定其他後端用 `--whisper groq|openai|whisperx`（不可與 `--local` 同時用）。選擇會記在 `meta.json.whisper_choice`，重跑自動沿用（用過 `--local` 的影片重跑不會改上傳 Groq；要改回加 `--whisper groq`）。影片有平台字幕時不轉錄，這個參數不影響結果。
   - **WhisperX 不支援提示詞**：`--glossary`／`--terms` 的術語提示不會送給 WhisperX（腳本會印警告），詞典只在轉錄後做固定替換，所以本地轉錄的專有名詞錯誤會比較多，步驟 4 校稿要多留意。`--lang` 只接受兩個小寫字母（例如 `zh`）。
   - **領域（`--category`）**：網址後第二個參數對得上白名單就照用；對不上則當主題關鍵字（見上方「呼叫參數」）；沒指定時依詞典推測，沒把握就建議 `/grill-me`。
   - 依主題 → `--glossary <領域>`，領域在 `glossary/domains/`（目前 `ai-chips`、`ai-video`、`electronics`、`kubernetes`、`claude-code`、`neo4j`、`pure-land`、`lengyan`；`common` 一律載入）。找不到合適領域就不加，並在步驟 4 考慮新增。
   - 標題只有 #標籤或很雜亂 → `--title "描述性標題"`（可用影片開頭標題卡文字）。
   - 人名、術語只在這支影片出現 → `--terms "詞1,詞2"`。
   - **講座／講經／演講（口語、有大量「呢」「啊」等語助詞）**：看標題或上傳者判斷是不是講座類影片，是的話歸檔時加 `--clean-fillers`（用 `--glossary pure-land` 的佛學講座會自動開啟，不必加）；之後可在 `meta.json` 寫 `"video_type": "lecture"`，重跑歸檔時 `auto` 模式也會去語助詞。不想去除加 `--keep-fillers`。選擇記在 `meta.json.clean_fillers`（`auto`／`on`／`off`），重跑沿用。
   - **電腦工具教學影片**（螢幕示範軟體／網頁／CLI／App 操作）→ 步驟 4d 會另寫操作 SOP；不想要時加 `--no-sop`，想強制時加 `--sop`（兩者擇一，記在 `meta.json.sop_mode`）。
   - **長的螢幕錄影／notebook／投影片影片** → 加 `--timestamps "MM:SS,…,H:MM:SS" --resolution 1024`。自動抽圖依畫面變化挑圖，緩慢捲動的 notebook 會被當成重複畫面丟掉，結果一段十幾分鐘只剩標題卡。做法：先跑一次讀逐字稿，找出各主題開始的時間，在每個時間點後約 20–40 秒放一個 cue（避開標題卡與轉場），再重跑；1024px 讓程式碼與小字可讀。兩個值會記在 `meta.json`（`cue_timestamps`、`resolution`），之後重跑自動沿用；重跑時 `slides` 的圖檔會依時間自動對到新截圖。

2. **歸檔**：
   `python3 scripts/watch_archive.py "<URL>" [--lang zh] [--glossary a,b] [--title "..."] [--terms "..."] [--question "..."] [--keep-media] [--local]`
   - 內部依序：解析平台與影片 ID（TikTok 短網址會先解析）→ 下載 → 平台字幕，或 Whisper 轉錄（Groq 帶語言與詞典提示詞；`--local` 時本地 WhisperX，只帶語言）→ 簡轉繁（OpenCC `s2twp`）→ 半形標點轉全形 → 詞典固定替換 → 截圖 → 寫檔 → 建報告。
   - 資料夾 `watch-output/<領域>/<日期>_<平台>_<標題>__<影片ID>/`（領域用 `--category` 指定，只接受 `glossary/categories.json` 白名單的值；未指定則取第一個詞典檔的 `category`，否則「未分類」並印 WARNING，歸檔後請確認分類合適；`index.md` 依領域分節）；同一影片 ID 只會有一個資料夾（重跑 = 更新；標題變動時資料夾會改名）。
   - 產出：`meta.json`、`transcript.md`（繁體）、`transcript.raw.md`（轉換前）、`frames/`、`frames.json`、`summary.md`（待補範本）、`transcript.zh.md`（外語影片才由 Claude 補寫）、`supplement.md`（選用：影片未呈現的補充資料）、`sop.md`（選用：教學影片的操作 SOP，見 4d）、`<stem>_report.md`、`<stem>_report.docx`，有 SOP 時另有 `<影片標題>_操作SOP.docx／.md` 與 `kb/`。`<stem>` = `<日期>_<平台>_<標題前20字>__<ID>`。
   - 語言判斷順序：Whisper 回報的語言（Whisper 轉錄時）→ 否則（平台字幕、強制 `--lang`）以字數／字元比例判斷（此時 `en` 代表拉丁字母的非中文，西班牙文等也會標成 `en`）→ 中文轉繁體（OpenCC）／非中文留給步驟 4b 中譯。
   - `--keep-media` 才保留 `media/<stem>_video.<ext>`；影片只存本機（gitignore）。

3. **校稿**（腳本不會自動做）：
   - **先驗收轉錄品質，再開始校稿**。看到下面任何一項，先處理再往下：
     - **語言錯**：逐字稿語言和影片不符。WhisperX 自動偵測曾把中文講座判成日文，而且直接**翻成日文**輸出（內容還看得出「雪公」「民國」等中文痕跡）。已確認是中文的影片，改用 Groq，或加 `--lang zh` 重跑（這是「確認整支同一語言」的合理強制）。
     - **重複幻覺**：同一詞連續重複幾十次（`small` 模型常見）→ 改用 Groq 重跑。
     - **整段漏轉**：時間戳跳了約 30 秒、中間只有一兩個字。根本原因是 Groq 處理長音訊時，有些 30 秒窗格在講者念完標題、停頓後就提早結束，剩下的人聲沒被轉錄（同一段單獨重送就正常）。`whisper.py` 現在會**自動補漏**：段落間空白 ≥15 秒就把那段音訊單獨重送再插回（執行輸出會印 `[watch] refilled N gap(s)`，每支影片最多 40 段）。仍有空白時多半是真的音樂或靜音；若是人聲，才需要用另一次轉錄互補。
     - **提示詞外洩**：逐字稿出現一串詞典 `terms`（例如「阿賴耶識、散善義、敦倫盡分」），是 Whisper 把提示詞當成內容吐出，要刪除。
     - **片頭片尾幻覺**：音樂段落出現不相干的句子（「明星大跟班」「明天見」），改成「（片頭音樂）」。
   - **重跑前先保存舊稿**：重跑會覆蓋 `transcript.md` 和 `transcript.raw.md`。先把舊的複製到暫存區，兩次轉錄的缺漏位置不同，可以互補；從另一次轉錄補入的段落要標「依第二次轉錄補入」，補不到的標「轉錄缺漏」，並記在 `known_asr_errors`。
   - **第一輪校稿**：通讀 `transcript.md`，挑出可疑處：專有名詞、英文縮寫、同音字、斷句異常。用 `frames/`（Read 看圖）上的畫面字幕、投影片交叉核對，以畫面文字為準；整理成替換表批次套用（詞典＋只限這支影片的校正）。
   - **第二輪校稿（必做）**：批次替換完，**用 Read 從第一行讀到最後一行**，逐行再看一次，不要只用 grep 抽查。批次替換一定會漏，常見的幾種：
     - 第一行或片頭的標題卡（例如「致成心」→ 至誠心），讀第一輪時容易跳過。
     - 替換表的 key 太長或只涵蓋一種寫法，同一個錯在相鄰行換了個樣子就沒套到（「清淨心作」改了，下一行開頭的「坐以後」沒改）。
     - 補漏、接縫處插入的句子；Groq 重複兩次的整句；片尾幻覺（「多謝您的觀看，下次見！」）。
     - 一字之差的同音字（悔／毀、鑽／專、意念／憶念）與異體字不一致（唸／念，統一成一種）。
     第二輪改完，在 PDF 用 `get_text()` 搜尋第一、二輪改過的錯字，確認一個都不剩。使用者回報漏網的錯字時，修好後再做一次完整的第二輪，不要只改被指出的那一處。
   - **去語助詞（講座／講經預設自動）**：`meta.json.clean_fillers` 為 `auto` 時，只要是講座類——載入 `pure-land` 詞典，或 `meta.json.video_type` 為 `lecture`——腳本在詞典替換後、寫入 `transcript.md` 前，自動去掉沒意義的「呢」「啊」與句尾的「啦／嘛／喔／哦／囉」（`scripts/clean_fillers.py`；只動逐字稿行，`transcript.raw.md` 保留原話；「嘛呢叭咪吽」「呢喃」「啊彌」等保留，句中的「嘛」不動；只處理偵測為中文的逐字稿）。`--clean-fillers` 對任何中文影片強制去除、`--keep-fillers` 保留（記在 `meta.json.clean_fillers`，重跑沿用）。重跑歸檔會自動再做，不必手動；已歸檔的舊稿可手動跑 `python3 scripts/clean_fillers.py watch-output/<領域>/<資料夾>`（可重複執行）。語助詞是影片原話，在 `summary.md` 註明有沒有去除。
   - **不要手改 `transcript.md` 以外的原始轉錄**；`transcript.raw.md` 是轉換前原文，保持不動。
   - **重跑會覆蓋 `transcript.md`**（重新轉錄，手改全部消失；`slides`、`keywords`、`known_asr_errors`、`summary.md` 會保留）。所以：穩定的校正先寫進詞典（見步驟 4）再重跑，讓它自動套用；只對這支影片成立的修正，重跑後要再手改一次 `transcript.md`，並用 `known_asr_errors` 記錄。

4. **補內容**（4a 先做投影片／主題分段，再做 4b）：
   - 改寫 `summary.md`：一句話重點、含時間戳的重點表、名詞與縮寫說明、轉錄校正備註。評論／立場性影片寫「講者主張…」，數字註明未經查證。
   - 編輯 `meta.json`（重跑時以下欄位會保留）：`video_type`（`tutorial`＝電腦工具教學→4d SOP；`lecture`＝講座／講經→去語助詞）、`keywords`（約 8–10 個）、`section_keywords`（key 為畫面起始時間，如 `"00:12"`）、`known_asr_errors`（`{"time","heard","expected"}`，推測的要標「推測」）、`slides`（見下）。
   - **投影片／主題分段**：看 `frames/` 後在 `meta.json` 寫 `slides`。簡報類影片一張投影片一段；沒有投影片的影片（訪談、實拍、操作畫面）則依講述主題或場景切段，每段的 `start` 取該主題開始的時間、`title` 寫主題名：`[{"start":"00:06","frame":"frame_0019.jpg","title":"…","note":"本張投影片重點","keywords":[…]}]`，報告就會「每段一張圖 + 說明文字 + 該段逐字稿」，不再逐畫面切碎。**每段以 2–4 分鐘為宜，不要超過約 5 分鐘**；超過就再切，並確認每段都有一張屬於該段內容的截圖（不夠就補 `--timestamps`）。`frame` 選字幕與游標最乾淨的一張；沒有 `slides` 時才退回逐畫面。
   - **截圖要對到重點（每段一張「講到這裡的那一張」）**：自動抽圖依畫面變化挑圖，逐頁動畫、轉場、標題卡很常被抓到，截圖就看不出這段在講什麼（例：提示詞 7 招影片，原本的截圖停在翻頁中間或只有大數字）。做法：
     1. 先寫好 `slides`（每段的 `start`、`title`、`note`），段落以逐字稿的主題轉換點切。
     2. 取得影片：歸檔時加 `--keep-media`（存在 `media/`，不入庫），或用 yt-dlp 下載到暫存區。
     3. `python3 scripts/pick_frames.py sheet watch-output/<領域>/<資料夾> --video <影片> --out <暫存區>`：每秒取一張縮圖，替每段產生標了秒數的縮圖表，並建議一個秒數（綠框；依「畫面內容多」×「前後一秒沒在變化（動畫已跑完）」評分，略過段落開頭 2 秒與最後 1 秒的轉場）。
     4. **用 Read 看每段縮圖表，確認建議的畫面真的對到這段的 `note`**：選畫面上的字和這段說明一致、資訊最完整的那一秒（條列跑完、引用句出現、對照表完整）。建議只看畫面豐富度，不懂內容，常會挑到同一段裡的次要畫面（例：第 2 招挑到 Eric 的引言，而不是「舊提醒句」主圖），這時改用自己挑的秒數。
     5. `python3 scripts/pick_frames.py apply <資料夾> --video <影片> --at "MM:SS,…"`（一段一個時間）：以 1024px 截成 `frames/slide_NN.jpg`、寫進 `frames.json`（`reason: clean-slide`）並更新 `slides[].frame`。
     6. 重建報告，轉 PDF 逐段確認截圖與說明對得上。
     7. 畫面上有說明欄放不下的重點文字（提示詞、程式碼、對照表、引用原文）時，從高解析度截圖逐字抄進 `supplement.md`（類型「畫面遺漏」），報告會自動多一節。
     - 重跑 `watch_archive.py` 會清空 `frames/`，`slide_NN.jpg` 要重新 apply（秒數記在 `frames.json` 的 `t`）。
   - **講者與投影片交疊的影片**（直播講座常見：投影片全螢幕＋左下角講者小視窗，換頁時有講者與投影片半透明交疊的轉場）：自動抽圖常抓到交疊畫面，使用者不要。做法：
     1. 用 yt-dlp 把影片下載到暫存區（不入庫，用完刪除），以 `ffmpeg -vf fps=1/2,scale=192:-1` 每 2 秒抽一張縮圖。
     2. 判斷乾淨投影片：投影片主體區（避開左下角小視窗）淡色像素比例高、背景色（例如講堂的藍色）比例低，而且前後各 2 秒也是乾淨的（避開轉場）。門檻依影片配色調整。
     3. 每段只在**內容對應的時間窗**裡挑「文字最多」的一張（條列動畫已跑完）。投影片換頁常比講者換話題慢，不限時間窗會挑到上一段的投影片。
     4. 用 `ffmpeg -ss <秒> -frames:v 1 -vf scale=1024:-2` 截高解析度圖，存成 `frames/slide_NN.jpg`，在 `frames.json` 加一筆（`reason: clean-slide`），再把 `slides[].frame` 指過去。
     5. 拼縮圖逐張確認，再重建報告。
     - **注意**：重跑 `watch_archive.py` 會清空 `frames/`，`slide_NN.jpg` 也會被刪掉。`slides` 會依時間對到新的自動截圖，所以重跑後要重做這一步。
   - **校正去哪裡**：穩定、不會誤傷的專有名詞錯誤 → 對應領域詞典 `glossary/domains/<領域>.json` 的 `replace`（key 用繁體、至少 3 字或帶上下文）或 `terms`；任何主題都成立的 → `glossary/common.json`；只這支影片成立或不確定的 → `known_asr_errors`。
   - 詞典新增後，對目前逐字稿直接替換並寫入 `meta.json.glossary_applied`，不必為此重跑 Whisper。
   - **外語影片加中譯**：執行輸出出現 `language: en`／`ja`／`ko` 等非中文語言，或 `meta.json.needs_zh_translation` 為 true（含英文平台字幕）時，一律寫 `transcript.zh.md`：翻成**繁體中文（台灣用字）**，專有名詞與指令保留英文原文；與 `transcript.md` 同格式 `[mm:ss] 譯文`，時間戳沿用原文；碎片句合併成完整句，掛在句首時間戳（其餘行省略）。不要讓一句譯文跨越 `slides` 的 `start` 邊界。報告每段會在原文下方加「**中譯：**」；重跑不會覆蓋此檔。

   - **4c 補充資料（`supplement.md`，選用）**：影片沒呈現、或畫面一閃而過而遺漏的資訊（被截斷的畫面文字、貼文說明欄／留言回傳的完整內容、連結、講者後續補充、更正），由使用者提供或我查到後，另存成同資料夾的 `supplement.md`（獨立檔，重跑不會覆蓋）。`build_report.py` 會自動把它放在報告「摘要」之後，並在報告最後加「補充資料連結」。寫法：
     - **一筆補充一節**，編號 S1、S2…，標類型（畫面遺漏／貼文／留言／連結／更正；來源位置不確定時寫「留言（推測）」這類帶註記的類型）；檔案以 `# 補充資料` 開頭（報告會丟掉這行，不用重複寫）。
     - **原文與分析分開**：「原文（逐字）」只放來源提供的文字，用 ``` 區塊保留、不改寫；「Claude 的對照分析」才是我的推論。
     - **三種說法要分清**：「補充直接寫明」、「與影片一致」、「據此推定（非補充直接寫明）」。只有補充直接寫明才能說「確認」。
     - **來源要完整**：誰提供、原始位置（說明欄／留言…）、取得日期、取得方式；並標對應的畫面檔名與時間。
     - **未查證的一律進備註**：主張、數字、模型名稱與版本號。
     - 補充若解決了 `known_asr_errors` 或摘要裡的推測，一併更新，用語依上面分級。
     - **畫面／投影片 → 補充資料（先判斷有沒有意義）**：投影片、螢幕錄影、字卡上常有講者沒唸出來的內容；逐字稿只有聲音，這些資訊會整個漏掉。
       1. **取得可讀的畫面與同時段講的話**：`python3 scripts/pick_frames.py text <資料夾> --video <影片> --out <暫存區>`，每段輸出一張原始解析度截圖（報告裡的 1024px 縮圖讀不清程式碼與小字），並列出這段時間的逐字稿。小字再用 ffmpeg `crop` 放大局部。截圖只放暫存區，不入庫。
       2. **判斷有沒有意義**：用 Read 看圖，把畫面上的字和同時段逐字稿比對，符合下列任一項才值得寫進補充：
          - 畫面有、講者沒唸的**原文**：提示詞、程式碼、指令、設定值、對照表、清單、引用的英文原句、網址、人名／出處、數字。
          - 畫面用**視覺標記**傳達意思：劃線刪除、前後對照（Before／After、Bad／Good）、計數（2/8、4/4）、箭頭流程、紅綠兩欄。
          - 講者口述是摘要，畫面是完整版（例：講者說「Anthropic 說全部做完才停」，畫面是整句英文原文）。
          不寫：只是把講者的話打成字幕、標題卡、Logo、裝飾、與逐字稿重複的條列。
       3. **逐字抄錄**：以原始解析度截圖為準，一字不改放進 ``` 區塊，保留行號與原有換行；劃線、紅框、箭頭等視覺標記用「← 劃掉」「（畫面標：…）」這類註記寫在行尾，並在備註說明註記是 Claude 加的。看不清的字寫「（看不清）」，不要猜。
       4. **分節**：同一份東西的演變放一節（例：範例 SYSTEM_PROMPT.md 改寫前 8 行／改寫後 4 行），各段零散的示範句合成一節並標時間（例：第 1、2、3、6、7 招的示範句）。每節標類型「畫面遺漏」，來源寫「影片畫面」與截圖檔名、時間；講者自製的示意範例要註明「不是官方文字」。
       5. **對照分析**：說明每段畫面文字對應影片哪個說法（例：劃掉的 4 行各對應第 1、2、4、5 招），分清「與影片一致」「畫面直接寫明」「據此推定」。畫面上的出處、模型名稱、版本號一律進備註標未查證。
       6. 畫面若**證實或推翻**逐字稿裡的推測（例：預設 effort 原標推測，00:30 畫面直接寫明），回頭更新 `known_asr_errors` 與摘要。
     - **原講稿／講義二次校對**：影片是在帶讀某份講稿時（例如明倫月刊的雪公講稿），用 curl 抓原始網頁全文（WebFetch 只給摘要，不能逐字比對），依講稿校正用字（例如「游魂為變」）並寫成一節補充（類型「連結」）。要分清「原稿有、影片一致」和「原稿沒有、是影片主講者自己的延伸」：後者不能用原稿去改，只能依上下文或投影片判斷。
     - 範本（`###` 小節在報告中會顯示為粗體行）：

       ```text
       ## S1｜<類型>：<一句話標題>
       - 來源：<誰提供／原始位置>；取得日期：<YYYY-MM-DD>；取得方式：<使用者貼上／查詢>
       - 為何需要補充：<影片缺了什麼；對應畫面檔名與時間>
       ### 原文（逐字）
       <``` 區塊>
       ### Claude 的對照分析
       - 與影片一致：…
       - 補充直接寫明（影片沒有的）：…
       - 據此推定（非補充直接寫明）：…
       ### 備註
       - 未查證的主張、版本號、可能過時之處
       ```

   - **4d 操作 SOP（`sop.md`，電腦工具教學影片）**：影片是在螢幕上示範軟體、網頁服務、CLI、程式碼、手機 App 或系統設定的操作時（實體硬體教學不算），消化完報告後，把它重新整理成可照著做的 SOP，並在 `meta.json` 寫 `"video_type": "tutorial"`。`--sop`／`--no-sop` 可強制開啟或關閉（記在 `meta.json.sop_mode`，重跑沿用）；`sop.md` 與 `supplement.md` 一樣是手寫檔，重跑不覆蓋。
     - **依任務分章**（安裝、生成圖片…），每章：`### 前置條件`（硬體、帳號、費用、要先完成的章節）、編號步驟、`### 注意事項`。
     - **每個步驟**：動作＋畫面上的按鈕或欄位**原文**（以截圖為準，不憑逐字稿）＋預期結果＋影片時間（括號）。關鍵步驟（設定畫面、錯誤提示、參數欄位）附 `![說明](frame@MM:SS)`：建報告時會換成最接近該時間的截圖，所以重跑後 `frames/` 重新編號也對得上；缺圖時補 `--timestamps` cue 重跑。
     - **只收可重現的操作**，講者的觀點與評價不收。影片沒示範的標「影片未示範」，Claude 補的標「推測」；價格、硬體需求、版本、效果一律標「講者主張，未查證」。
     - 影片有示範錯誤時，最後加「錯誤排解」表（現象／原因／做法／影片時間）。
     - **產出**（`build_report.py`）：主報告在「摘要」之後多一節「操作 SOP」；另輸出 `<影片標題>_操作SOP.docx／.md`（只有 SOP 與截圖）；以及 `kb/`（`<影片標題>_操作SOP.md`＋`attachments/`）：檔頭有 YAML frontmatter（title／type／source／date／tags），圖片依影片時間命名 `step-MMSS.jpg`、用相對路徑，整個資料夾可直接放進 Obsidian vault 或用 Notion 匯入（Markdown zip），當 AI 知識庫素材。
     - 規模參考：ComfyUI 影片（15 分鐘、7 章）約 14 頁、19 張圖，這個規模可以接受。

5. **重建與檢查**：`python3 scripts/build_report.py watch-output/<領域>/<資料夾>`；docx 轉 PDF 後目視檢查（中文、截圖、頁數；直式影片圖片已限高）。
   - 出現 `PermissionError` 寫不進 `*_report.docx`，代表使用者正在 Word 開著它（資料夾裡會有 `~$` 開頭的鎖定檔）：請使用者關掉 Word 再重建，不要強制結束 Word。`~$` 鎖定檔不要 commit。
   - Windows 轉 PDF：`soffice` 不在 PATH 時用 `"C:/Program Files/LibreOffice/program/soffice.com" --headless --convert-to pdf --outdir <暫存區> <docx>`。

6. **交付**：用 SendUserFile 傳 `*_report.docx`（有 SOP 時一併傳 `*_操作SOP.docx`，並提醒 `kb/` 可放進 Obsidian／Notion）；回覆寫摘要重點，並說明逐字稿是 Groq 轉錄、本地 WhisperX 轉錄還是平台字幕（`meta.json.transcript_source`）；外語影片註明已附中譯（`transcript.zh.md`）。

7. **提交並給確認連結**：在 `claude/...` 分支 commit 並 push（不強制 push、不重用已合併分支），然後跑 `python3 scripts/review_links.py watch-output/<領域>/<資料夾>`，把輸出的連結（資料夾、報告 md／docx、摘要、中譯、與 `main` 的差異）貼給使用者確認。**使用者確認前不開 PR、不 merge**；連結指向分支，未合併也打得開。回覆同時列出需要使用者確認的判斷（領域是否合適、標題、標「推測」的校正）。

8. **確認後開 PR 並 merge**：使用者確認（或指出要修改的地方，改完再重給連結）後，才開 PR；合併方式依使用者指示（PR + Squash and merge，或直接合併），使用者沒說就先問。

## 注意

- TikTok 短網址（vt.tiktok.com）自動解析成真正的影片 ID；Facebook 標題的「views · reactions |」前綴與作者後綴會自動去除，原始標題在 `meta.json.title_raw`。
- 簡轉繁採台灣用字，技術詞會被換成台灣詞（算子→運算元、優化→最佳化）；OpenCC 對「里／裡」等一對多字有漏轉，由 `glossary/common.json` 兜底。
- Groq 轉錄有誤聽很正常；提示詞只提高機率，詞典才是確定的修正。
- 宗教／佛學講座：有 `glossary/domains/pure-land.json`（淨土宗、台中蓮社、雪公講稿常見專名）。只對單支影片成立的誤聽（例如「欣、厭」被聽成「心、願」，「心」字到處都有，放進詞典會誤傷）記在 `known_asr_errors`，不要放進詞典。
- 失敗時回報錯誤類別與原因（網路／下載／轉錄／權限），不要印出 key。
- 版權：來源是他人影片；repo 設為 private 時僅供個人參考，改 public 或分享前不要附影片。
