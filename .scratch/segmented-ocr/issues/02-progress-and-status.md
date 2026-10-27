# 02：每段進度輸出與 status 子命令

**What to build:** 每段結束印一行（第 N／共 M 段、時間範圍、辨識張數、耗時）並 flush。新增 `status <out>`：讀 `<seg-dir>`，列出已完成段數、剩餘段數、哪些段有鎖（正在跑）與最近一次進度時間。

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] 每段結束輸出一行進度，格式固定、可被測試比對
- [ ] `status` 顯示完成／剩餘／進行中的段落，沒有 seg-dir 時給清楚訊息
- [ ] 全部完成時 `status` 提示可執行合併（或已合併）
- [ ] 測試涵蓋進度行內容與 `status` 輸出

## Comments
