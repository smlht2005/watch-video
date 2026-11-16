# 01: 報告建置提供共用的「圖文對照段落」函式（prefactor）

**What to build:** 把報告〈圖文對照〉的段落產生（slides 分段／無 slides 逐畫面、逐字稿切段、中譯對齊、圖文貼文「第 N 頁」）抽成報告建置模組的公開函式，回傳段落 Markdown 與用到的圖片清單，讓報告與 Obsidian 匯出器共用。報告輸出完全不變。

**Blocked by:** None (can start immediately)

**Status:** done

- [x] 報告建置有一個公開函式，輸入歸檔資料夾（與已讀入的 meta／逐字稿段落），回傳〈圖文對照〉段落文字與其引用的圖片相對路徑清單
- [x] 報告 md 由此函式組成，既有資料夾重建後 `*_report.md` 與改動前逐字相同（至少用一支 slides 影片、一支無 slides 影片、一支圖文貼文驗證）
- [x] 新增測試：函式回傳的圖片清單與段落中的圖片連結一致
- [x] 全套測試通過

## Comments

- 2026-11-16：完成。新增 `build_report.gallery(meta, segs, frames) -> (lines, images)`，`build_md` 改用它；6 個資料夾（slides、無 slides、中譯、圖文貼文、投資理財）的報告 md 與改動前逐字相同；全套 304 測試通過。
