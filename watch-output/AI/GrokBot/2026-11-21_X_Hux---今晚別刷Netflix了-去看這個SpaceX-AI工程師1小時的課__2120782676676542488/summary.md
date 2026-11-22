# 摘要：Lauren 談如何信任 agent——驗證、skill 與嚴格約束（Cursor／Grokbot）

**一句話重點**：講者 Lauren（任職 Cursor／SpaceX AI，Grokbot 團隊）分享她如何從「高度介入」爬上「信任曲線」，到讓 agent 自動合併 PR：先建立「驗證」能力與 skill（含 eval 測試 skill），再把架構改成嚴格、慣例化、由 CI 硬性強制的 Dune 架構；並談 token 的 ROI 與 Grokbot 如何讓非工程人員也能交付（以下成績與主張皆講者所述，未查證）。標題稱「SpaceX AI 工程師」，內容主要談 Cursor 與 Grokbot。

| 時間 | 重點 |
|---|---|
| 00:00 | AI 是配對夥伴，不是取代思考 |
| 01:25 | 核心：如何信任 agent；信任曲線；自動合併 PR |
| 04:18 | 一個月 1000 個 PR；投影片「5 個月 3000+ PR」 |
| 06:03 | 最重要的技能：驗證（讓 agent 能真的執行並測自己） |
| 07:02 | 實例：control glass skill 與功能地圖 |
| 13:46 | PStack（Potato Stack）的來歷與 skill 的概念 |
| 17:26 | 維護 skill：eval＝agent 的單元測試 |
| 21:36 | 評審 agent、hill climbing；工程師像主廚 |
| 23:50 | 先本機、再雲端 agent；Benny 重現 bug |
| 27:32 | 回顧：驗證→雲端→自動合併，沒有捷徑 |
| 29:56 | 重寫與護欄：Greenfield 原型的風險 |
| 36:05 | PR 大小與 CI：Dune、禁用 useEffect 與註解 |
| 42:42 | 多層約束：硬強制優先、軟規則輔助 |
| 48:25 | Q&A：token ROI、Grok 4.6 |
| 53:26 | Grokbot 讓 PM 與設計師也能交付 |

## 領域判斷

- 使用者指定 `AI/GrokBot`（講者在 Grokbot 團隊，內容涵蓋 Grokbot 的架構與 Cursor 的實務）。

## 名詞與縮寫

- **verification skill／control glass**：讓 agent 能操作並驗證應用的 skill；glass 是 agent 視窗的內部代號。
- **PStack**：講者做的外掛（Potato Stack，調侃 Garry Tan 的 GStack）。
- **eval**：agent／skill 的單元測試。
- **Dune**：Grokbot 的嚴格架構代號（「給 Electron 應用的 Next.js」）。
- **BugBot**：Cursor 在 CI 上跑的程式碼審查工具。

## 轉錄與校正備註

- 逐字稿為 X 平台人工英文字幕；另寫繁體中文中譯 `transcript.zh.md`（碎片句已合併）。
- 校正：Rockbot／GraphBot／in Robot→Grokbot、email playbook→eval playbook、PSAT／P stack→PStack、bugba→BugBot、Gary→Garry。
- 保留待確認：「DSAC」（21:11）、「fable size」（51:23）。
- 影片畫面有燒入中英雙語字幕與投影片（如「how do I trust my agents more?」）。
- 「土豆女神」＝ Lauren Tan：影片中 PStack 的 P 是 potato，且講者自稱 Lauren，與先前影片的稱呼吻合。
- 第二輪：1561 行英文字幕以機械檢查加上全文通讀（修 20 處）。
