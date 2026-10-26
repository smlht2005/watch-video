---
name: watch-archive
description: 看影片並歸檔成圖文報告。使用者給影片網址（Facebook/YouTube/TikTok 等），要求「看影片、摘要、逐字稿、轉 Word、歸檔」時使用。網址後可加第二個參數：白名單內的領域（如 `/watch-archive <網址> 身心生活`）當領域，其他詞當主題關鍵字；沒指定領域時依詞典推測，沒把握建議先 /grill-me。產出 watch-output/<領域>/<資料夾>/ 內的 report.docx、report.md、截圖與 meta.json；逐字稿預設繁體中文，並用詞典校正。
---

# watch-archive：影片 → 圖文報告（Word / Markdown）

回覆一律使用繁體中文（zh-TW）。**絕不印出或複述任何 API key**（只可說「有/沒有」與長度）。

**這份檔案只放骨架。每個步驟開工前，先用 Read 讀下表對應的參考檔**：長 session 壓縮後 skill 本文會被截斷，參考檔不會，不要憑記憶做。步驟編號（0–8、4a–4d）在骨架與參考檔一致。

| 步驟 | 參考檔（`.claude/skills/watch-archive/references/`） |
|---|---|
| 呼叫參數、領域判斷、1 選參數 | `params.md` |
| 0 環境（含 Windows） | `setup.md` |
| 2 歸檔 | `archive.md` |
| 3 校稿 | `proofread.md` |
| 4a／4b 分段、截圖、補內容、中譯 | `content.md` |
| 4c 補充資料 | `supplement-4c.md` |
| 4d 操作 SOP | `sop-4d.md` |
| 5–8 重建、交付、確認連結、PR | `deliver.md` |
| 注意事項、流程圖維護 | `notes.md` |

## 呼叫參數：`/watch-archive <影片網址> [領域或主題]`

第二個參數對得上白名單 `glossary/categories.json` 就當領域（`--category`），對不上就當主題關鍵字；沒把握的領域不要自行決定，建議先 `/grill-me`。完整規則（回覆要講明的三件事、子領域 `AI/claude-code`、新增領域門檻）見 `.claude/skills/watch-archive/references/params.md`。

## 流程總覽

![watch-archive 流程鳥瞰圖](../../../docs/watch-archive-flow.png)

藍＝腳本自動、橘＝Claude 判斷、綠＝交付；兩條重跑回圈：截圖不足補 cue（4a→2）、語言錯／整段漏轉（3→2）。文字版見 `.claude/skills/watch-archive/references/notes.md`。

## 步驟要點

0. **環境**：確認 Groq key 有／沒有（只報長度）；**雲端 session 只能用 Groq，不加 `--local`**；從最新 `main` 開新 `claude/...` 分支，不重用已合併的分支；`pip install -r requirements.txt pymupdf`（`pymupdf` 供步驟 5 把 PDF 轉圖目視檢查、在 PDF 搜尋校稿錯字）。
1. **選參數**：**預設不加 `--lang`**（讓 Whisper 自動偵測）；有 Groq key 預設 Groq；`--category`、`--glossary`、`--title`、`--terms`；講座／講經加 `--clean-fillers`；教學影片的 SOP 用 `--sop`／`--no-sop`；長螢幕錄影加 `--timestamps "MM:SS,…" --resolution 1024`。
2. **歸檔**：`python3 scripts/watch_archive.py "<URL>" [旗標]`；重跑會清空 `frames/` 與覆蓋 `transcript.md`。
3. **校稿**：先驗收（語言錯、重複幻覺、整段漏轉、提示詞外洩、片頭尾幻覺；Groq／OpenAI 轉錄由 `whisper.py` 自動補漏並做字數密度掃描，看 `[watch] refilled` 訊息與 `meta.json` 缺漏清單；**`--local` 沒有自動補漏，要自己檢查約 30 秒的整段漏轉**，可用 `whisper._transcribe_file` 每 30 秒重送音訊比對），要重跑先保存舊稿；再兩輪校稿，**第二輪必做：用 Read 從頭到尾逐行重讀**；講座／講經另做口吃與標點整理（`scripts/stutter_check.py`）與投影片文字交叉比對（`scripts/slide_text_check.py`）。**佛經講解／講經座且畫面有燒入字幕**才加做字幕 OCR 比對（費時，其他影片不用；`scripts/subtitle_ocr.py`，見 `.claude/skills/watch-archive/references/proofread.md`）。**佛學／講經**的推測詞（`known_asr_errors` 的 `status: "suspected"`）另跑 `scripts/clip_check.py <資料夾> --wait-confirm` 剪音檔給使用者聽音確認（同一份 proofread.md）。
4. **補內容**：
   - 4a／4b：寫 `slides`（每段 2–4 分鐘、不超過約 5 分鐘，每段一張對到重點的截圖；**影片明說步驟時改為一步驟一段一張圖一段說明**，見 `.claude/skills/watch-archive/references/content.md` 4a）、`summary.md`、`meta.json`；截圖用 `pick_frames.py sheet` 逐秒挑、**自己看圖確認**再 `apply`；外語影片寫 `transcript.zh.md`；手寫 `mindmap.md`（思維導圖，放在圖文對照之前）。
   - 4c：畫面有、講者沒唸的原文，逐字抄進 `supplement.md`；影片數字與主張一律標「講者主張，未查證」。
   - 4d：電腦工具教學影片另寫 `sop.md`。
5. **重建與檢查**：`python3 scripts/build_report.py watch-output/<領域>/<資料夾>`；docx 轉 PDF 目視檢查（中文、截圖、頁數）。
6. **交付**：SendUserFile 傳 `*_report.docx`；回覆說明逐字稿來源（`meta.json.transcript_source`）與外語中譯。
7. **提交並給確認連結**：commit、push 到 `claude/...` 分支，跑 `python3 scripts/review_links.py watch-output/<領域>/<資料夾>` 貼連結（有 `waitConfirm/` 時會多印本機 `index.md` 路徑），並列出需使用者確認的判斷。**使用者確認前不開 PR、不 merge。**
8. **確認後才開 PR 並 merge**：合併方式依使用者指示；沒說就先問。

失敗時回報錯誤類別與原因（網路／下載／轉錄／權限），不要印出 key。
