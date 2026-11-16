# 02: 影片筆記用文字版思維導圖取代摘要與 PNG

**What to build:** Obsidian 影片筆記不再有〈摘要〉與思維導圖 PNG；改在標題後放〈思維導圖〉，內容是資料夾 `mindmap.md` 的縮排條列（去掉第一行 auto 註解與檔內一級標題）。`_attachments/<video_id>/` 不再產生 `mindmap.png`，重匯時舊的自然消失。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 筆記有〈思維導圖〉且內容為 `mindmap.md` 的條列，不含 `<!-- auto` 註解
- [ ] 筆記沒有〈摘要〉，也沒有 `mindmap.png` 圖片連結
- [ ] 匯出後 `_attachments/<vid>/` 沒有 `mindmap.png`；先放一個舊 PNG 再重匯，它會被清掉
- [ ] 沒有 `mindmap.md` 的資料夾照常匯出，省略此區塊、不報錯
- [ ] 屬性、知識點、連結、SOP、索引、擁有權行為不變（既有測試通過；檢查摘要的斷言改寫為新行為）

## Comments
