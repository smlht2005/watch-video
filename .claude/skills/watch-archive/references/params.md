# 呼叫參數、領域判斷與步驟 1 選參數

> 領域判斷（`AI/claude-code`、新增領域門檻）與 `watch_archive.py` 旗標選擇。

- **第一個參數**：影片網址（必填）。
- **第二個參數（選填）**：先對照白名單 `glossary/categories.json`（目前 AI／AI/claude-code／佛學／商業理財／身心生活／電子／雲端／未分類；寫簡體會自動轉繁體，英文只差大小寫會校正）：
  - **對得上白名單 → 當成領域**：傳給 `watch_archive.py --category <領域>`，不必再推測。
  - **對不上 → 當成主題詞（例如「自律」）**：不報錯、不中斷。把它存進這支影片的 `meta.json.keywords`（步驟 4b 補內容時一起寫），領域則改由詞典或影片內容判斷（見下一點）。**回覆必須明講三件事**：這個詞沒有對應到任何領域；實際歸到哪個領域、依據是什麼；想指定領域時可用的值有哪些（這樣領域打錯字也不會悄悄歸錯，使用者看得出來）。
- **沒有指定領域時**：先看影片內容與所選詞典（`--glossary`）能否明確判斷（詞典檔的 `category` 欄位會自動推測）。能明確判斷就照該領域歸檔，並在回覆註明是推測；**沒把握就不要自行決定，建議使用者先跑 `/grill-me`** 釐清領域，不要悄悄放進「未分類」。
- **子領域 `AI/claude-code`（使用者的學習主題）**：只收以 Claude Code 為主角的影片（用法、額度／token、CLAUDE.md、MCP、Agent 工具）；只是提到 Claude 的影片（例：ComfyUI 接 Claude）仍歸 `AI`。載入 `--glossary claude-code` 會自動歸入，也可明講 `--category AI/claude-code`。巢狀領域只限一層，寫成「父/子」；`index.md` 小節顯示為「AI／claude-code」。
- **新增領域的規則**：同時符合 (a) 至少 5 支影片屬於同一個新主題、(b) 放在現有領域裡找不到合適位置，才新增；沒達標前，主題只用 `keywords` 標記，不開新資料夾（例：自律 → 歸 `身心生活`＋關鍵字「自律」；同一關鍵字累積到 5 支且有需要時再討論是否獨立）。要新增領域、或不確定新影片該歸哪個領域時，用 `/grill-me <要決定的事>`，結論寫進 `glossary/categories.json`（必要時再補詞典檔的 `category`）。
- **按關鍵字找影片**：目前不另建索引，搜尋各 `meta.json` 的 `keywords` 欄位即可。

## 步驟 1：選參數

**沒有把握就用預設**，以下各項只在條件符合時才加：

   - **語言：預設不加 `--lang`，讓 Whisper 自動偵測。** 強制 `--lang` 會讓任何語言都被硬轉成該語言（英文影片加 `--lang zh` 會得到不通順的中文，且無法事後偵測）。只有使用者明確指定、或已確認整支影片是同一種語言且自動偵測不準時才加；腳本會對強制語言印警告。
   - 語言優先採用 **Whisper 回報的語言**（報告表頭 `Whisper language`）；平台字幕來源與強制 `--lang` 時才從輸出文字判斷。寫入 `meta.json.detected_language`（`zh`／`ja`／`ko`／`en`／`es`…／`other`／`unknown`；每次重跑重新判斷）、`language_source`、`forced_lang` 與 `needs_zh_translation`（任何已知的非中文語言為 true；`other`／`unknown` 為 false），並在結尾印出 `language: …`。中文夾雜英文術語仍會判為 `zh`；`other`（混雜）與 `unknown`（逐字稿太短）要自己讀逐字稿確認：`other` 為避免改壞日韓文，**不會做簡轉繁**（`ja`／`ko` 同樣不轉），確定是中文時請手動轉繁體；`unknown` 仍照常轉換。平台有字幕時直接採用字幕，語言以字幕為準。
   - **轉錄方式**：預設不加。有 Groq key 時用 Groq；使用者要求本地轉錄（不上傳音訊）時加 `--local`（本地 WhisperX，雲端不可用）；要指定其他後端用 `--whisper groq|openai|whisperx`（不可與 `--local` 同時用）。選擇會記在 `meta.json.whisper_choice`，重跑自動沿用（用過 `--local` 的影片重跑不會改上傳 Groq；要改回加 `--whisper groq`）。影片有平台字幕時不轉錄，這個參數不影響結果。
   - **WhisperX 不支援提示詞**：`--glossary`／`--terms` 的術語提示不會送給 WhisperX（腳本會印警告），詞典只在轉錄後做固定替換，所以本地轉錄的專有名詞錯誤會比較多，步驟 3 校稿（`.claude/skills/watch-archive/references/proofread.md`）要多留意。`--lang` 只接受兩個小寫字母（例如 `zh`）。
   - **領域（`--category`）**：網址後第二個參數對得上白名單就照用；對不上則當主題關鍵字（見上方「呼叫參數」）；沒指定時依詞典推測，沒把握就建議 `/grill-me`。
   - 依主題 → `--glossary <領域>`，領域在 `glossary/domains/`（目前 `ai-chips`、`ai-video`、`electronics`、`kubernetes`、`claude-code`、`neo4j`、`pure-land`、`lengyan`；`common` 一律載入）。找不到合適領域就不加，並在 `.claude/skills/watch-archive/references/content.md` 的「校正去哪裡」考慮新增。
   - 標題只有 #標籤或很雜亂 → `--title "描述性標題"`（可用影片開頭標題卡文字）。
   - 人名、術語只在這支影片出現 → `--terms "詞1,詞2"`。
   - **講座／講經／演講（口語、有大量「呢」「啊」等語助詞）**：看標題或上傳者判斷是不是講座類影片，是的話歸檔時加 `--clean-fillers`（用 `--glossary pure-land` 的佛學講座會自動開啟，不必加）；之後可在 `meta.json` 寫 `"video_type": "lecture"`，重跑歸檔時 `auto` 模式也會去語助詞。不想去除加 `--keep-fillers`。選擇記在 `meta.json.clean_fillers`（`auto`／`on`／`off`），重跑沿用。
   - **電腦工具教學影片**（螢幕示範軟體／網頁／CLI／App 操作）→ 步驟 4d 會另寫操作 SOP；不想要時加 `--no-sop`，想強制時加 `--sop`（兩者擇一，記在 `meta.json.sop_mode`）。
   - **長的螢幕錄影／notebook／投影片影片** → 加 `--timestamps "MM:SS,…,H:MM:SS" --resolution 1024`。自動抽圖依畫面變化挑圖，緩慢捲動的 notebook 會被當成重複畫面丟掉，結果一段十幾分鐘只剩標題卡。做法：先跑一次讀逐字稿，找出各主題開始的時間，在每個時間點後約 20–40 秒放一個 cue（避開標題卡與轉場），再重跑；1024px 讓程式碼與小字可讀。兩個值會記在 `meta.json`（`cue_timestamps`、`resolution`），之後重跑自動沿用；重跑時 `slides` 的圖檔會依時間自動對到新截圖。
