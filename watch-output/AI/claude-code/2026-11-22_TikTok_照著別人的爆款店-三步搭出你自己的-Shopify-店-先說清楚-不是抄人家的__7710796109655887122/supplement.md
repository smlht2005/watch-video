# 補充資料

## S1｜整理者補充：Shopify CLI 是什麼與基本用法
- 來源：整理者（Claude）依自身知識撰寫，非影片內容、未對照官方文件查證；取得日期：2026-11-22；取得方式：使用者詢問「何謂 shopify cli, how to use」
- 為何需要補充：影片 00:46 只說「用 Shopify CLI 在本地預覽，不會動到線上的店」，沒有說明工具與指令。

### 內容（整理者補充，指令與版本請以官方文件為準）
Shopify CLI 是 Shopify 官方的命令列工具，用來在本機開發與管理主題（theme）、App 與 Function。影片用到的是主題開發。

```text
npm install -g @shopify/cli@latest                     # 安裝（需 Node.js 18 以上）
shopify theme pull --store 店名.myshopify.com          # 把線上主題拉到本機
shopify theme dev  --store 店名.myshopify.com          # 本地預覽（通常 http://127.0.0.1:9292），改檔即時更新
shopify theme push                                     # 上傳；建議先推成未發布的新主題，確認後再發布
shopify theme check                                    # 檢查主題程式碼
```

### Claude 的對照分析
- 與影片一致：影片說用 Shopify CLI 在本地預覽、不動線上的店，對應 `theme dev`（據此推定，影片未講指令）。
- 影片未示範：安裝、登入、`pull`／`push` 步驟。
- 備註：指令、連接埠與版本需求為整理者補充、未查證；建議 `pull` 後用 git 管理、不要直接覆蓋營業中的主題；參考他人店時不複製 logo、文案與圖片。

## S2｜整理者補充：Claude Design 在 Claude Code 的用法
- 來源：整理者（Claude）網路搜尋的二手與官方說明頁摘要，未逐頁查證；取得日期：2026-11-22；取得方式：使用者詢問「Claude Design 如何在 Claude Code 使用」後以 WebSearch 查詢
- 為何需要補充：影片 00:00 只說 Claude 把 Claude Design 放進每個對話、連 Claude Code 也能用，沒有說明怎麼用。

### 內容（整理者補充，未查證）
- 主要入口是 Claude Code 的 `/design` 指令（終端機或桌面版 session）：建立、編輯並同步設計專案，也可用自然語言描述需求。
- 匯入／匯出：用 `/design` 把設計匯入程式碼庫，或把現有程式碼匯出成可互動原型。
- 設計系統：用 `/design-sync` 從 GitHub repo、設計檔、上傳檔或本機程式碼庫匯入，讓產出符合品牌。
- 雙向同步：Claude Code 開始的原型可同步到 Claude Design 畫布；在 Claude Design 做好的可交給本機 Claude Code 或雲端 Claude Code Web。
- 方案與用量：beta，Pro／Max／Team／Enterprise 可用，用量與聊天、Claude Code、Cowork 共用。
- 時間點：有文章稱獨立版 claude.ai/design 建立的設計系統須在 2026-12-14 關閉前遷移（單一來源）。

### Claude 的對照分析
- 與影片一致：影片說 Claude Code 能用 Claude Design，對應 `/design`（據此推定，影片未講指令）。
- 影片未示範：是否使用 `/design`；丟截圖給 Claude Code 搭頁面不一定需要它。
- 「放進每個對話」一句未在官方來源證實（只見於二手報導），仍是講者主張。
- 備註：發布日期（2026-04-17）、加入 Claude Code（2026-06-17）、`/design` skill（2026-08-18）來自二手報導，未核對官方；指令與用法以官方文件為準：https://support.claude.com/en/articles/14604416-get-started-with-claude-design 、https://claude.com/blog/claude-design-stays-on-brand-for-daily-work 、https://support.claude.com/en/articles/12138966-release-notes
