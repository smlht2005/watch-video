# 補充資料

## S1｜畫面遺漏：CodeGraph README 實測表格（VS Code／Excalidraw／Tokio）
- 來源：影片畫面（畫面標「CodeGraph README」）；取得日期：2026-11-09；取得方式：從原始解析度截圖抄錄
- 為何需要補充：講者只唸重點數字，畫面表格有完整欄位；對應 `slide_05`～`slide_07`（00:27–00:39）
### 原文（逐字）
```
Codebase | Time                          | File reads
VS Code  | 2.2× faster (58s vs 2m 10s)   | 0 vs 12        （畫面以紅框標 0 vs 12）

Codebase    | WITH cg                   | WITHOUT cg
Excalidraw  | 45s / 2 / 156k / $0.54    | 2m 42s / 43 / 991k / $2.43

Codebase | Time
Tokio    | 2.6× faster (1m 3s vs 2m 43s)
```
### Claude 的對照分析
- 與影片一致：VS Code 2:10→0:58、0 個檔；Excalidraw $2.43→$0.54；Tokio 2:43→1:03。
- 畫面直接寫明（影片沒唸的）：Excalidraw 的耗時 45 秒對 2 分 42 秒、工具呼叫 2 對 43 次、token 156k 對 991k。
- 據此推定（非畫面直接寫明）：開場「43 趟→2 趟」與 Excalidraw 列的 2／43 次相同，可能是同一組實測；開場截圖另標出處 DevsKingdom，兩者是否同一題未確認。
### 備註
- 全部數據為 CodeGraph README 的主張，未查證；欄位「45s / 2 / 156k / $0.54」的順序解讀（時間／呼叫次數／token／花費）是 Claude 推測。

## S2｜畫面遺漏：`codegraph init` 終端機輸出
- 來源：影片畫面（標「CodeGraph 官方」）；取得日期：2026-11-09；取得方式：原始解析度截圖抄錄
- 為何需要補充：講者只說「3000 多個檔案，30 幾秒」；對應 `slide_04`（00:22）
### 原文（逐字）
```
colby@Colbys-MacBook-Air g（被圖釘遮住）va % codegraph init -i
  Initializing CodeGraph
  Initialized in /Users/colby/GitKraken/Personal/codeg（畫面截斷）
  ◆ Scanning files — 3,251 found
  ◆ Parsing code — done
  ◆ Resolving refs — done
  Indexed 3,251 files
  119,675 nodes, 116,424 edges in 33.2s      （畫面以紅圈標 33.2s）
  Done
```
### Claude 的對照分析
- 與影片一致：3,251 個檔、33.2 秒建好。
- 畫面直接寫明：指令實際帶 `-i` 參數；圖譜規模 119,675 個節點、116,424 條邊。`-i` 的作用影片未說明。
### 備註
- 示範專案與機器效能未說明，建圖時間僅供參考（講者主張，未查證）。

## S3｜畫面遺漏：CodeGraph 說明文字（100% 本機）
- 來源：影片畫面；取得日期：2026-11-09；取得方式：原始解析度截圖抄錄
- 為何需要補充：講者只列 4 個工具，畫面原文列了更多；對應 `slide_09`（00:44–00:49）
### 原文（逐字）
```
Pre-indexed code knowledge graph,
auto syncs on code changes, for
Claude Code, Codex, Gemini, Cursor,
OpenCode, AntiGravity, Kiro, CoPilot,
and Hermes Agent — fewer tokens,
fewer tool calls, 100% local          （畫面以紅圈標 100% local）
```
### Claude 的對照分析
- 與影片一致：本機執行；支援 Claude Code、Codex、Cursor、Gemini。
- 畫面直接寫明（影片沒唸的）：程式碼變動時自動同步；另支援 OpenCode、AntiGravity、Kiro、CoPilot、Hermes Agent。
### 備註
- 支援清單與功能為工具自述，未查證；GitHub 截圖倉庫名 `colbymchenry/codegraph`、Star 76k（00:14），開場終端機出自 DevsKingdom，皆未查證。

## S4｜畫面遺漏：開場的 Claude Code 對話（43 趟的示範）
- 來源：影片畫面（標「DevsKingdom」）；取得日期：2026-11-09；取得方式：原始解析度截圖抄錄（下半截斷）
- 為何需要補充：說明「43 趟」是在問什麼樣的問題；對應 `slide_01`（00:00–00:02）
### 原文（逐字）
```
> this code base is openhuman project front end code, can you tell me how to skip the login ?
● I will begin by exploring the frontend routing and provider chain to understand how authentica（截斷）
  handled and where the "login" or "boot" check is enforced.
  First, I'll list the files in app/src/ to confirm the project structure.
  Listed 1 directory (ctrl+o to expand)
● Bash(pwd)
  └ /home/web/projects/openhuman/app
  Listed 1 directory (ctrl+o to expand)
● I'll examine the App.tsx provider chain and the BootCheckGate to understand the authentication（截斷）
  identify where the login check is enforced.
  Read 5 files (ctrl+o to expand)
● To skip the login (authentication check) in the OpenHuman frontend, you need to bypass the Pro（截斷）
  component, as it is the primary gatekeeper for the application's internal routes.
  How it works currently:
  1. ProtectedRoute.tsx: This component checks if a sessionToken exists in the CoreStateProvide（截斷）
     requireAuth is true and the token is missing, it redirects the user back to the welcome page（截斷）
  2. App.tsx (Onboarding Gate): …（看不清）
```
### Claude 的對照分析
- 據此推定：後面「地圖」畫面上的 App.tsx、BootCheckGate、ProtectedRoute、CoreState 節點，即取自這段對話涉及的檔案／元件，是示意圖，不是 CodeGraph 實際輸出。
### 備註
- 這段畫面看起來是 Claude Code 的終端介面（`ctrl+o to expand`），但未標示是否為裝 CodeGraph 前的版本；「43 趟」的計數方式未說明（講者主張，未查證）。
