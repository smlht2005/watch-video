# 04：--low-priority 與 --background

**What to build:** `--low-priority`：Windows 設 Idle 優先權類別，其他平台用 `os.nice`，子程序繼承，預設不開。`--background`：以相同參數另起一個脫離 session 的程序（Windows `DETACHED_PROCESS`＋`CREATE_NEW_PROCESS_GROUP`，其他平台 `start_new_session`），隱含 `--low-priority`，寫 `<seg-dir>/progress.log`，本程序印出 log 路徑後立即結束。

**Blocked by:** 01、02

**Status:** ready-for-agent

- [x] 旗標傳遞：`--background` 組出的子程序指令不含 `--background`、含 `--low-priority`，其餘參數照傳
- [x] 啟動後立即返回，印出 log 與 `status` 的用法
- [x] progress.log 在背景程序內持續寫入每段進度
- [x] 以替身驗證，不真的起程序；實機在 Windows 手動驗證一次並記錄
- [x] 文件註明：關掉 Claude 不會終止背景程序，但關機會

## Comments
