---
name: watch-archive
description: 看影片並歸檔成圖文報告。使用者給影片網址（Facebook/YouTube/TikTok 等），要求「看影片、摘要、逐字稿、轉 Word、歸檔」時使用。產出 watch-output/<資料夾>/ 內的 report.docx、report.md、截圖與 meta.json；逐字稿預設繁體中文，並用詞典校正。
---

# watch-archive：影片 → 圖文報告（Word / Markdown）

回覆一律使用繁體中文（zh-TW）。**絕不印出或複述任何 API key**（只可說「有/沒有」與長度）。

## 流程總覽

![watch-archive 流程鳥瞰圖](../../../docs/watch-archive-flow.png)

```text
網址 ─▶ 0 環境 ─▶ 1 選參數(不強制 --lang；長錄影加 --timestamps/--resolution；本地轉錄加 --local) ─▶ 2 歸檔(下載→平台字幕或 Groq／WhisperX 轉錄→偵測語言→中文轉繁體→詞典校正→截圖→報告)
     ─▶ 3 校稿(先驗收：語言錯／重複幻覺／30 秒漏轉（已自動補漏）／提示詞外洩→保存舊稿後回到 2 重跑、兩次互補；第一輪批次替換→第二輪逐行重讀全文) ─▶ 4a 看截圖分投影片或主題(slides，每段 2–4 分鐘；截圖不足→補 cue 回到 2 重跑；講者交疊→改挑乾淨投影片)
     ─▶ 4b 補內容(摘要/關鍵字/校正；非中文→transcript.zh.md) ─▶ 4c 補充資料(選用 supplement.md；有原講稿→二次校對) ─▶ 5 重建報告 ─▶ 5b 目視檢查 ─▶ 6 交付 ─▶ 7 提交
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
   - 依主題 → `--glossary <領域>`，領域在 `glossary/domains/`（目前 `ai-chips`、`ai-video`、`electronics`、`kubernetes`、`claude-code`、`neo4j`、`pure-land`；`common` 一律載入）。找不到合適領域就不加，並在步驟 4 考慮新增。
   - 標題只有 #標籤或很雜亂 → `--title "描述性標題"`（可用影片開頭標題卡文字）。
   - 人名、術語只在這支影片出現 → `--terms "詞1,詞2"`。
   - **長的螢幕錄影／notebook／投影片影片** → 加 `--timestamps "MM:SS,…,H:MM:SS" --resolution 1024`。自動抽圖依畫面變化挑圖，緩慢捲動的 notebook 會被當成重複畫面丟掉，結果一段十幾分鐘只剩標題卡。做法：先跑一次讀逐字稿，找出各主題開始的時間，在每個時間點後約 20–40 秒放一個 cue（避開標題卡與轉場），再重跑；1024px 讓程式碼與小字可讀。兩個值會記在 `meta.json`（`cue_timestamps`、`resolution`），之後重跑自動沿用；重跑時 `slides` 的圖檔會依時間自動對到新截圖。

2. **歸檔**：
   `python3 scripts/watch_archive.py "<URL>" [--lang zh] [--glossary a,b] [--title "..."] [--terms "..."] [--question "..."] [--keep-media] [--local]`
   - 內部依序：解析平台與影片 ID（TikTok 短網址會先解析）→ 下載 → 平台字幕，或 Whisper 轉錄（Groq 帶語言與詞典提示詞；`--local` 時本地 WhisperX，只帶語言）→ 簡轉繁（OpenCC `s2twp`）→ 半形標點轉全形 → 詞典固定替換 → 截圖 → 寫檔 → 建報告。
   - 資料夾 `watch-output/<日期>_<平台>_<標題>__<影片ID>/`；同一影片 ID 只會有一個資料夾（重跑 = 更新；標題變動時資料夾會改名）。
   - 產出：`meta.json`、`transcript.md`（繁體）、`transcript.raw.md`（轉換前）、`frames/`、`frames.json`、`summary.md`（待補範本）、`transcript.zh.md`（外語影片才由 Claude 補寫）、`supplement.md`（選用：影片未呈現的補充資料）、`<stem>_report.md`、`<stem>_report.docx`。`<stem>` = `<日期>_<平台>_<標題前20字>__<ID>`。
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
   - **不要手改 `transcript.md` 以外的原始轉錄**；`transcript.raw.md` 是轉換前原文，保持不動。
   - **重跑會覆蓋 `transcript.md`**（重新轉錄，手改全部消失；`slides`、`keywords`、`known_asr_errors`、`summary.md` 會保留）。所以：穩定的校正先寫進詞典（見步驟 4）再重跑，讓它自動套用；只對這支影片成立的修正，重跑後要再手改一次 `transcript.md`，並用 `known_asr_errors` 記錄。

4. **補內容**（4a 先做投影片／主題分段，再做 4b）：
   - 改寫 `summary.md`：一句話重點、含時間戳的重點表、名詞與縮寫說明、轉錄校正備註。評論／立場性影片寫「講者主張…」，數字註明未經查證。
   - 編輯 `meta.json`（重跑時以下欄位會保留）：`keywords`（約 8–10 個）、`section_keywords`（key 為畫面起始時間，如 `"00:12"`）、`known_asr_errors`（`{"time","heard","expected"}`，推測的要標「推測」）、`slides`（見下）。
   - **投影片／主題分段**：看 `frames/` 後在 `meta.json` 寫 `slides`。簡報類影片一張投影片一段；沒有投影片的影片（訪談、實拍、操作畫面）則依講述主題或場景切段，每段的 `start` 取該主題開始的時間、`title` 寫主題名：`[{"start":"00:06","frame":"frame_0019.jpg","title":"…","note":"本張投影片重點","keywords":[…]}]`，報告就會「每段一張圖 + 說明文字 + 該段逐字稿」，不再逐畫面切碎。**每段以 2–4 分鐘為宜，不要超過約 5 分鐘**；超過就再切，並確認每段都有一張屬於該段內容的截圖（不夠就補 `--timestamps`）。`frame` 選字幕與游標最乾淨的一張；沒有 `slides` 時才退回逐畫面。
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

5. **重建與檢查**：`python3 scripts/build_report.py watch-output/<資料夾>`；docx 轉 PDF 後目視檢查（中文、截圖、頁數；直式影片圖片已限高）。
   - 出現 `PermissionError` 寫不進 `*_report.docx`，代表使用者正在 Word 開著它（資料夾裡會有 `~$` 開頭的鎖定檔）：請使用者關掉 Word 再重建，不要強制結束 Word。`~$` 鎖定檔不要 commit。
   - Windows 轉 PDF：`soffice` 不在 PATH 時用 `"C:/Program Files/LibreOffice/program/soffice.com" --headless --convert-to pdf --outdir <暫存區> <docx>`。

6. **交付**：用 SendUserFile 傳 `*_report.docx`；回覆寫摘要重點，並說明逐字稿是 Groq 轉錄、本地 WhisperX 轉錄還是平台字幕（`meta.json.transcript_source`）；外語影片註明已附中譯（`transcript.zh.md`）。

7. **提交**：在 `claude/...` 分支 commit 並 push。合併方式依使用者指示（PR + Squash and merge，或直接合併）；使用者沒說就先問，不強制 push、不重用已合併分支。

## 注意

- TikTok 短網址（vt.tiktok.com）自動解析成真正的影片 ID；Facebook 標題的「views · reactions |」前綴與作者後綴會自動去除，原始標題在 `meta.json.title_raw`。
- 簡轉繁採台灣用字，技術詞會被換成台灣詞（算子→運算元、優化→最佳化）；OpenCC 對「里／裡」等一對多字有漏轉，由 `glossary/common.json` 兜底。
- Groq 轉錄有誤聽很正常；提示詞只提高機率，詞典才是確定的修正。
- 宗教／佛學講座：有 `glossary/domains/pure-land.json`（淨土宗、台中蓮社、雪公講稿常見專名）。只對單支影片成立的誤聽（例如「欣、厭」被聽成「心、願」，「心」字到處都有，放進詞典會誤傷）記在 `known_asr_errors`，不要放進詞典。
- 失敗時回報錯誤類別與原因（網路／下載／轉錄／權限），不要印出 key。
- 版權：來源是他人影片；repo 設為 private 時僅供個人參考，改 public 或分享前不要附影片。
