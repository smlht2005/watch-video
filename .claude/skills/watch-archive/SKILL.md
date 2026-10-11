---
name: watch-archive
description: 看影片並歸檔成圖文報告。使用者給影片網址（Facebook/YouTube/TikTok 等），要求「看影片、摘要、逐字稿、轉 Word、歸檔」時使用。產出 watch-output/<資料夾>/ 內的 report.docx、report.md、截圖與 meta.json；逐字稿預設繁體中文，並用詞典校正。
---

# watch-archive：影片 → 圖文報告（Word / Markdown）

回覆一律使用繁體中文（zh-TW）。**絕不印出或複述任何 API key**（只可說「有/沒有」與長度）。

## 流程總覽

![watch-archive 流程鳥瞰圖](../../../docs/watch-archive-flow.png)

```text
網址 ─▶ 0 環境 ─▶ 1 選參數(不強制 --lang) ─▶ 2 歸檔(下載→平台字幕或 Groq 轉錄→偵測語言→中文轉繁體→詞典校正→截圖→報告)
     ─▶ 3 校稿 ─▶ 4a 看截圖分投影片或主題(slides) ─▶ 4b 補內容(摘要/關鍵字/校正；非中文→transcript.zh.md)
     ─▶ 4c 補充資料(選用 supplement.md) ─▶ 5 重建報告 ─▶ 5b 目視檢查 ─▶ 6 交付 ─▶ 7 提交
```

藍＝腳本自動、橘＝Claude 判斷、綠＝交付；新增「偵測語言」（步驟 2）與「補充資料」（步驟 4c）；圖源 `docs/watch-archive-flow.svg`。改圖後重新產生 PNG：
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox --hide-scrollbars --window-size=1600,1100 --screenshot=docs/watch-archive-flow.png file://$PWD/docs/watch-archive-flow.svg`，再用 PIL 裁成 1600×900（視窗外框會吃掉底部，故先開大再裁）。

## 步驟

0. **環境**：確認 `GROQ_API_KEY` 存在（只報有/沒有與長度）；確認 `pip install python-docx opencc-python-reimplemented`。
   若 `.claude/skills/watch` 尚未設定，先跑 `python3 .claude/skills/watch/scripts/setup.py --backend groq --detail balanced`（exit 0）。
   從最新的 `main` 開新分支 `claude/...`（不要重用已合併的分支）。

1. **選參數**（沒有把握就用預設）：
   - **語言：預設不加 `--lang`，讓 Whisper 自動偵測。** 強制 `--lang` 會讓任何語言都被硬轉成該語言（英文影片加 `--lang zh` 會得到不通順的中文，且無法事後偵測）。只有使用者明確指定、或已確認整支影片是同一種語言且自動偵測不準時才加；腳本會對強制語言印警告。
   - 腳本轉錄後會從輸出文字判斷語言，寫入 `meta.json.detected_language`（`zh`／`ja`／`ko`／`en`／`other`／`unknown`；每次重跑重新判斷）、`forced_lang` 與 `needs_zh_translation`（非 `zh`／`unknown` 時為 true），並在結尾印出 `language: …`。中文夾雜英文術語仍會判為 `zh`；`other`（混雜）與 `unknown`（逐字稿太短）要自己讀逐字稿確認。平台有字幕時直接採用字幕，語言以字幕為準。
   - 依主題 → `--glossary <領域>`，領域在 `glossary/domains/`（目前 `ai-chips`、`electronics`、`kubernetes`、`claude-code`；`common` 一律載入）。找不到合適領域就不加，並在步驟 4 考慮新增。
   - 標題只有 #標籤或很雜亂 → `--title "描述性標題"`（可用影片開頭標題卡文字）。
   - 人名、術語只在這支影片出現 → `--terms "詞1,詞2"`。

2. **歸檔**：
   `python3 scripts/watch_archive.py "<URL>" [--lang zh] [--glossary a,b] [--title "..."] [--terms "..."] [--question "..."] [--keep-media]`
   - 內部依序：解析平台與影片 ID（TikTok 短網址會先解析）→ 下載 → Groq Whisper 轉錄（帶語言與詞典提示詞）→ 簡轉繁（OpenCC `s2twp`）→ 半形標點轉全形 → 詞典固定替換 → 截圖 → 寫檔 → 建報告。
   - 資料夾 `watch-output/<日期>_<平台>_<標題>__<影片ID>/`；同一影片 ID 只會有一個資料夾（重跑 = 更新；標題變動時資料夾會改名）。
   - 產出：`meta.json`、`transcript.md`（繁體）、`transcript.raw.md`（轉換前）、`frames/`、`frames.json`、`summary.md`（待補範本）、`transcript.zh.md`（外語影片才由 Claude 補寫）、`supplement.md`（選用：影片未呈現的補充資料）、`<stem>_report.md`、`<stem>_report.docx`。`<stem>` = `<日期>_<平台>_<標題前20字>__<ID>`。
   - 語言判斷順序：平台字幕語言 → Whisper 自動偵測結果（腳本以字數／字元比例判斷 `detected_language`；`en` 代表拉丁字母的非中文，西班牙文等也會標成 `en`）→ 中文轉繁體（OpenCC）／非中文留給步驟 4b 中譯。
   - `--keep-media` 才保留 `media/<stem>_video.<ext>`；影片只存本機（gitignore）。

3. **校稿**（腳本不會自動做）：
   - 通讀 `transcript.md`，挑出可疑處：專有名詞、英文縮寫、同音字、斷句異常。
   - 用 `frames/`（Read 看圖）上的畫面字幕交叉核對；以畫面文字為準。
   - **不要手改 `transcript.md` 以外的原始轉錄**；`transcript.raw.md` 是轉換前原文，保持不動。
   - **重跑會覆蓋 `transcript.md`**（重新轉錄，手改全部消失；`slides`、`keywords`、`known_asr_errors`、`summary.md` 會保留）。所以：穩定的校正先寫進詞典（見步驟 4）再重跑，讓它自動套用；只對這支影片成立的修正，重跑後要再手改一次 `transcript.md`，並用 `known_asr_errors` 記錄。

4. **補內容**（4a 先做投影片／主題分段，再做 4b）：
   - 改寫 `summary.md`：一句話重點、含時間戳的重點表、名詞與縮寫說明、轉錄校正備註。評論／立場性影片寫「講者主張…」，數字註明未經查證。
   - 編輯 `meta.json`（重跑時以下欄位會保留）：`keywords`（約 8–10 個）、`section_keywords`（key 為畫面起始時間，如 `"00:12"`）、`known_asr_errors`（`{"time","heard","expected"}`，推測的要標「推測」）、`slides`（見下）。
   - **投影片／主題分段**：看 `frames/` 後在 `meta.json` 寫 `slides`。簡報類影片一張投影片一段；沒有投影片的影片（訪談、實拍、操作畫面）則依講述主題或場景切段，每段的 `start` 取該主題開始的時間、`title` 寫主題名：`[{"start":"00:06","frame":"frame_0019.jpg","title":"…","note":"本張投影片重點","keywords":[…]}]`，報告就會「每段一張圖 + 說明文字 + 該段逐字稿」，不再逐畫面切碎。`frame` 選字幕與游標最乾淨的一張；沒有 `slides` 時才退回逐畫面。
   - **校正去哪裡**：穩定、不會誤傷的專有名詞錯誤 → 對應領域詞典 `glossary/domains/<領域>.json` 的 `replace`（key 用繁體、至少 3 字或帶上下文）或 `terms`；任何主題都成立的 → `glossary/common.json`；只這支影片成立或不確定的 → `known_asr_errors`。
   - 詞典新增後，對目前逐字稿直接替換並寫入 `meta.json.glossary_applied`，不必為此重跑 Whisper。
   - **外語影片加中譯**：執行輸出出現 `language: en`／`ja`／`ko`，或 `meta.json.needs_zh_translation` 為 true（含英文平台字幕）時，一律寫 `transcript.zh.md`：翻成**繁體中文（台灣用字）**，專有名詞與指令保留英文原文；與 `transcript.md` 同格式 `[mm:ss] 譯文`，時間戳沿用原文；碎片句合併成完整句，掛在句首時間戳（其餘行省略）。不要讓一句譯文跨越 `slides` 的 `start` 邊界。報告每段會在原文下方加「**中譯：**」；重跑不會覆蓋此檔。

   - **4c 補充資料（`supplement.md`，選用）**：影片沒呈現、或畫面一閃而過而遺漏的資訊（被截斷的畫面文字、貼文說明欄／留言回傳的完整內容、連結、講者後續補充、更正），由使用者提供或我查到後，另存成同資料夾的 `supplement.md`（獨立檔，重跑不會覆蓋）。`build_report.py` 會自動把它放在報告「摘要」之後，並在報告最後加「補充資料連結」。寫法：
     - **一筆補充一節**，編號 S1、S2…，標類型（畫面遺漏／貼文／留言／連結／更正；來源位置不確定時寫「留言（推測）」這類帶註記的類型）；檔案以 `# 補充資料` 開頭（報告會丟掉這行，不用重複寫）。
     - **原文與分析分開**：「原文（逐字）」只放來源提供的文字，用 ``` 區塊保留、不改寫；「Claude 的對照分析」才是我的推論。
     - **三種說法要分清**：「補充直接寫明」、「與影片一致」、「據此推定（非補充直接寫明）」。只有補充直接寫明才能說「確認」。
     - **來源要完整**：誰提供、原始位置（說明欄／留言…）、取得日期、取得方式；並標對應的畫面檔名與時間。
     - **未查證的一律進備註**：主張、數字、模型名稱與版本號。
     - 補充若解決了 `known_asr_errors` 或摘要裡的推測，一併更新，用語依上面分級。
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

6. **交付**：用 SendUserFile 傳 `*_report.docx`；回覆寫摘要重點，並說明逐字稿是 Groq 轉錄還是平台字幕（`meta.json.transcript_source`）；外語影片註明已附中譯（`transcript.zh.md`）。

7. **提交**：在 `claude/...` 分支 commit 並 push。合併方式依使用者指示（PR + Squash and merge，或直接合併）；使用者沒說就先問，不強制 push、不重用已合併分支。

## 注意

- TikTok 短網址（vt.tiktok.com）自動解析成真正的影片 ID；Facebook 標題的「views · reactions |」前綴與作者後綴會自動去除，原始標題在 `meta.json.title_raw`。
- 簡轉繁採台灣用字，技術詞會被換成台灣詞（算子→運算元、優化→最佳化）；OpenCC 對「里／裡」等一對多字有漏轉，由 `glossary/common.json` 兜底。
- Groq 轉錄有誤聽很正常；提示詞只提高機率，詞典才是確定的修正。
- 失敗時回報錯誤類別與原因（網路／下載／轉錄／權限），不要印出 key。
- 版權：來源是他人影片；repo 設為 private 時僅供個人參考，改 public 或分享前不要附影片。
