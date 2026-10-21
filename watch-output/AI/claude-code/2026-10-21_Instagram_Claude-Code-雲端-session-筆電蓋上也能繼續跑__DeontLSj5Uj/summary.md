# 摘要：Claude Code 雲端 session：筆電蓋上也能繼續跑

**一句話重點**：講者介紹 Claude Code 的「雲端 session」——把專案從 GitHub 複製到雲端虛擬機器、用自己的 branch 在背景工作，筆電蓋上也不中斷，並可用手機審查、再 teleport 回本機（以下皆為講者主張，未查證）。

| 時間 | 重點 |
|---|---|
| 00:00 | 開場：筆電蓋起來 Claude 仍在寫，拿起手機它還會問問題 |
| 00:05 | 本機 Claude Code 電腦一睡就停，手機遙控（Remote Control）也要電腦一直開著 |
| 00:12 | 雲端 session：專案從 GitHub 複製到雲端虛擬機器，開自己的 branch；下班前丟大重構，隔天看結果 |
| 00:20 | 網頁、手機 App、桌面 App 都能開；終端機用 `claude --cloud`；第一次先接 GitHub |
| 00:29 | 在手機看 diff、在程式碼旁留言讓它修改，沒問題按 Create PR |
| 00:33 | 想回電腦接著做：終端機 `claude --teleport`，對話與 branch 一起拉回 |
| 00:38 | 可一次開多個 session，各有自己的 branch、互不干擾 |

## 名詞
- **雲端 session**：Claude Code 在雲端虛擬機器執行的工作階段，不依賴本機開機。
- **Remote Control**：用手機遙控本機上的 Claude Code，本機仍須開機。
- **teleport**：`claude --teleport` 把雲端 session 的對話與 branch 拉回本機。

## 轉錄校正備註
- 轉錄來源 Whisper（Groq），語言 zh（影片為中文）。
- 「中端機」→「終端機」（已加入 claude-code 詞典）；「DIF」→ diff；兩處指令依畫面字幕校正為 `claude --cloud`、`claude --teleport`（逐字稿原文聽成「CLAUDE、CLAUDE」「CLAUDE://teleport」）。
- 片尾 00:43–00:44 為頻道「AI 懶人報」宣傳。
