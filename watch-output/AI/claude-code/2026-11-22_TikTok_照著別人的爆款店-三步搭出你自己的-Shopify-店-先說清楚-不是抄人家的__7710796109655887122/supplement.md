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
