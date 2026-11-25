# 摘要：CodeGraph：讓 Claude Code 查程式碼地圖，找程式碼從 43 趟降到 2 趟

**一句話重點**：開源工具 CodeGraph 先在本機把整個專案的「誰呼叫誰」建成程式碼知識圖譜，Claude Code 等 AI 寫程式工具查詢時直接查圖，不必反覆搜尋、開檔，講者主張可大幅減少工具呼叫次數、token 與花費（講者主張，未查證）。

- 來源：Instagram Reel，頻道「AI懶人報」（ai.lanrenbao），約 53 秒。
- 逐字稿：Groq Whisper 轉錄（自動偵測為中文），已依畫面字幕校稿。

## 重點表

| 時間 | 重點 |
|---|---|
| 00:00 | 同一題，Claude 找程式碼要呼叫工具 43 趟；裝 CodeGraph 後 2 趟（講者主張，未查證） |
| 00:03 | 問題：AI 在大專案裡「搜尋→開檔→再搜尋」，一直燒 token，使用者只能乾等 |
| 00:08 | 原理：CodeGraph 先把專案的呼叫關係畫成一張地圖，AI 直接查地圖；開源不到 10 個月破 7.5 萬顆星（講者主張，未查證） |
| 00:15 | 用法：`codegraph install` 接上 AI 工具 → 專案資料夾 `codegraph init` 建索引；示範 3,251 個檔約 33 秒建好；之後照常跟 Claude 對話即可 |
| 00:24 | 官方 7 個開源專案實測之一：VS Code 架構問題 2 分 10 秒、讀 12 個檔 → 58 秒、0 個檔（講者主張，未查證） |
| 00:31 | Excalidraw：同一題花費 2.43 美元 → 0.54 美元（講者主張，未查證） |
| 00:36 | Rust 的 Tokio：2 分 43 秒 → 1 分 3 秒（講者主張，未查證） |
| 00:40 | 7 個專案平均：token 少 62%、花費少 44%（講者主張，未查證） |
| 00:43 | 100% 本機執行、不需另申請 API key；Claude Code、Codex、Cursor、Gemini 都能接 |
| 00:49 | 片尾：追蹤 AI 懶人報 |

## 名詞與縮寫

- **CodeGraph**：預先建立程式碼知識圖譜（code knowledge graph）的開源工具，程式碼變動時自動同步；畫面 GitHub 為 `colbymchenry/codegraph`（倉庫名依畫面，未查證）。
- **工具呼叫（tool call）**：AI 代理每次執行搜尋、讀檔等動作；呼叫越多，耗時與 token 越多。
- **Excalidraw**：開源白板繪圖工具；**Tokio**：Rust 的非同步執行環境。兩者都是實測用的開源專案。
- **with cg／without cg**：畫面表格欄名，cg＝CodeGraph。

## 轉錄校正備註

- 依畫面字幕修正：CLAUDE→Claude、Cograph／cograph→CodeGraph／codegraph、「每一樁要翻」→「沒裝要翻」、Excaladra→Excalidraw、「RUS的Tokyo」→「Rust的Tokio」；半形逗號改全形。明細見 `meta.json.known_asr_errors`。
- 未去除語助詞（非講座類影片）。

## 備註

- 影片中所有倍數、時間、金額、星數都是講者／CodeGraph README 的主張，未經查證；畫面表格原文見補充資料 S1–S3。
- 這支以「讓 Claude Code 更省 token」的第三方 MCP 類工具為主角，但工具本身也支援其他 AI 寫程式工具。
