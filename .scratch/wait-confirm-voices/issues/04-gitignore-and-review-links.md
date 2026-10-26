# 04：.gitignore 與 review_links.py 附 index.md

**What to build:** `waitConfirm/`（他人影片的音檔與截圖）不會被 commit；交付連結時，使用者能看到本機 `waitConfirm/index.md` 的路徑，並知道 GitHub 上看不到音檔。

**Blocked by:** 01

**Status:** resolved

- [x] `.gitignore` 加 `watch-output/**/waitConfirm/`，寫法與 `media/` 一致並加註解（他人影片音檔，只留本機）
- [x] 有 `waitConfirm/` 的資料夾下，`git status` 不列出該目錄任何檔案
- [x] `review_links.py`：存在 `waitConfirm/index.md` 時，多印一行「待確認音檔（本機）」，內容為 `index.md` 的絕對路徑（純路徑，不用 `file://`），並註明 GitHub 上看不到音檔、要在本機打開
- [x] 沒有 `waitConfirm/` 時，輸出與改動前逐字相同
- [x] `waitConfirm/` 存在但缺 `index.md` 時，印警告，不印路徑
- [x] 本機路徑用獨立的純函式處理，不放進 `build_links`（它只產生 GitHub URL）
- [x] 測試涵蓋以上三種情況，不連網、不呼叫 git

## Comments

- 完成於 commit `7aac98d`（分支 claude/clip-check）。
