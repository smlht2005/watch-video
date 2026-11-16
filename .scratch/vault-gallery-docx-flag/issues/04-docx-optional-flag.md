# 04: docx 改為選用（--docx）

**What to build:** 歸檔與重建報告預設只產 Markdown（報告 md、SOP md、`kb/`）；`build_report.py` 與 `watch_archive.py` 加 `--docx` 才同時產出 `*_report.docx` 與 `*_操作SOP.docx`。`watch_archive` 不把旗標記進 `meta.json`，每次執行自己決定並轉傳給重建。不加 `--docx` 重建時刪掉資料夾裡舊的 docx。文件同步改為新行為。

**Blocked by:** None (can start immediately)

**Status:** done

- [x] 預設重建只有 md，資料夾沒有任何 `.docx`
- [x] `--docx`（建置函式的對應參數）時報告與 SOP 的 docx 都產出
- [x] 先加 `--docx` 建、再不加重建，舊 docx 消失
- [x] `watch_archive` 的參數解析接受 `--docx` 並傳到重建（以參數解析層測，不跑下載）
- [x] `review_links` 在沒有 docx 時正常列出 md 連結
- [x] `CLAUDE.md`（交付前檢查改看 md／思維導圖，要版面才加 `--docx` 轉 PDF）、`deliver.md`（步驟 5、步驟 6 SendUserFile 只在有 docx 時傳）、`archive.md`、`params.md`、`README.md` 同步
- [x] 全套測試通過

## Comments

- 2026-11-16：完成。`build(dest, docx=False)`；`build_report.py`、`watch_archive.py` 加 `--docx`（含 Threads 圖文貼文路徑），抽出 `watch_archive.parser()` 供測試；`review_links.py` 另補列 `_操作SOP.md`（docx 選用後 SOP 仍有連結）。新增 5 項測試、改寫 5 項寫死輸出數量的舊測試；文件 CLAUDE.md、SKILL.md、archive／deliver／params／sop-4d、README 同步。全套 321 測試通過。
