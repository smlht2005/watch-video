# 知識點

## 已確認
### 信任是使用 agent 的核心問題：不信任就只能微觀管理
- 出處：01:34
- 引文：「how do you trust it?」
- 說明：講者說她用 agent 寫程式時最大的主題是「如何信任它」：當 agent 憑空猜測、第一百次信心滿滿地宣稱找到真正原因卻不是時，你就失去信任；信任不足就像不信任團隊的主管，只能微觀管理、無法平行化，也無法充分發揮 agent 的價值（講者主張）。
- 標示：講者主張，未查證

### 驗證不保證程式碼好，但能保證「正確」
- 出處：06:48
- 引文：「it doesn't guarantee your agent writes good code」
- 說明：講者說與 agent 合作最重要的技能是驗證：讓 agent 能真的執行程式碼、取得 CPU 追蹤、heap snapshot、開模擬器，實際測試並驗證自己的工作；它不保證 agent 寫出好的程式碼，但能讓它至少寫出「正確」的程式碼，是信任 agent 的一大步（講者主張）。
- 標示：講者主張，未查證

### 沒有驗證 skill 時，你自己就是瓶頸
- 出處：09:02
- 引文：「you are the verifier」
- 說明：講者說用 agent 開發卻沒有驗證 skill 時，你自己就是驗證者、就是瓶頸：你要打開本機 build 看結果、複製截圖與錯誤給 agent，無法平行化；所以她替 Cursor 做的第一批 skill 之一就是讓 agent 能自己操作並驗證應用（講者主張）。
- 標示：講者主張，未查證

### 功能地圖：教 agent 如何走到應用的每個功能
- 出處：11:43
- 引文：「it teaches the agent how to get」
- 說明：講者說驗證 skill 裡有個「功能地圖」，教 agent 怎麼走到應用的所有功能（含 UI 路徑、快捷鍵、DOM 屬性），讓 agent 能把模糊的使用者回報甚至只有一張截圖的回報，對應到具體功能；PStack 的 create verification skill 會探索程式碼並建立初版功能地圖（講者所述）。
- 標示：講者主張，未查證

### eval 是 agent 的單元測試
- 出處：18:16
- 引文：「it's like a unit test for an agent」
- 說明：講者說維護 skill 要靠 eval，她的心智模型是「agent 的單元測試」，不需要特別框架、視嚴謹程度自行建立；PStack 的 eval playbook 讓主協調 agent 訂評分標準、產生多個子 agent 去跑，並可跨多個模型比較（講者主張）。
- 標示：講者主張，未查證

### 最短路徑就是最好路徑：讓捷徑成為正解
- 出處：44:28
- 引文：「the shortest path is the best path」
- 說明：講者說 Dune 框架的一個關鍵原則是「最短的路徑就是最好的路徑」：agent 愛走捷徑、找最快的方式解題，所以就讓最快的方式也是最好的方式；為此她把每個 feature 的程式碼共置在單一目錄、讓開發方式高度慣例化，連最笨的 agent 也能做對（講者主張）。
- 標示：講者主張，未查證

### 靠人在審查時糾正，就該把它變成硬規則
- 出處：47:46
- 引文：「how do I turn this into a hard rule」
- 說明：講者說如果你的程式碼庫靠真人在 code review 時反覆糾正來維持不變量，是最糟的處境，每次都該視為 code smell，問自己：與其在 PR 留言，怎麼把它變成硬規則、lint 規則、CI 失敗，甚至從根本消除這個問題？她強調硬性強制（CI、靜態分析、編譯器）優先，BugBot 規則與 skill 只是較軟的輔助層（講者主張）。
- 標示：講者主張，未查證

### 評估時別讓子 agent 知道自己在被評估
- 出處：19:40
- 引文：「let the sub-agent know that it's being evaluated」
- 說明：講者說做 eval 時她為子 agent 建立的目錄名稱經過巧妙設計，不讓子 agent 知道自己正被評估，因為 agent 其實看得出來，一旦看出來就會改變行為，使評估失真（講者主張，未查證）。
- 標示：講者主張，未查證

## 候選
