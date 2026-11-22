# 步驟 5–8：重建、交付、確認連結、PR

> 使用者確認前不開 PR、不 merge。

5. **重建與檢查**：`python3 scripts/build_report.py watch-output/<領域>/<資料夾>`；預設只產 md（`--docx` 才產 Word；資料夾已有 docx 時會沿用並更新，`--no-docx` 移除）。檢查報告 md 與 `mindmap.png`；有 `--docx` 時再把 docx 轉 PDF 目視檢查（中文、截圖、頁數；直式影片圖片已限高）。
   - 出現 `PermissionError` 寫不進 `*_report.docx`，代表使用者正在 Word 開著它（資料夾裡會有 `~$` 開頭的鎖定檔）：請使用者關掉 Word 再重建，不要強制結束 Word。`~$` 鎖定檔不要 commit。
   - Windows 轉 PDF：`soffice` 不在 PATH 時用 `"C:/Program Files/LibreOffice/program/soffice.com" --headless --convert-to pdf --outdir <暫存區> <docx>`。

   - **每次歸檔都要跑 5b**（不論有沒有 `links.md`／`knowledge.md`；沒有時影片筆記 `status` 為 `unreviewed`，仍會產生）：`python3 scripts/obsidian_export.py watch-output/<領域>/<資料夾>`，把 `obsidian-vault/` 的變更一併 commit（見 `.claude/skills/watch-archive/references/obsidian-4e.md`）。2026-11-15 曾因只在有 `links.md` 時才跑而漏匯兩支影片。

6. **交付**：預設貼報告 md 的連結（步驟 7 的 `review_links.py`）；使用者要 Word 檔時才用 `--docx` 重建，並用 SendUserFile 傳 `*_report.docx`（有 SOP 時一併傳 `*_操作SOP.docx`）；有 SOP 時提醒 `kb/` 可放進 Obsidian／Notion；回覆寫摘要重點，並說明逐字稿是 Groq 轉錄、本地 WhisperX 轉錄還是平台字幕（`meta.json.transcript_source`）；外語影片註明已附中譯（`transcript.zh.md`）。

7. **提交並給確認連結**（先確認 `meta.json.second_pass.done`；2026-11-21 起歸檔的影片沒標記時 `review_links.py` 會拒絕輸出，見 proofread.md）：在 `claude/...` 分支 commit 並 push（不強制 push、不重用已合併分支），然後跑 `python3 scripts/review_links.py watch-output/<領域>/<資料夾>`，把輸出的連結（資料夾、報告 md／docx、摘要、中譯、與 `main` 的差異）貼給使用者確認。**使用者確認前不開 PR、不 merge**；連結指向分支，未合併也打得開。`review_links.py` 也會印 `knowledge.md`／`links.md` 連結與編號的知識點候選清單：**回覆必須貼這份連結與清單**，請使用者用編號回答「確認 1,3,5／刪 2／改 4」。回覆同時列出需要使用者確認的判斷（領域是否合適、標題、標「推測」的校正）。有 `waitConfirm/` 時，`review_links.py` 會多印本機 `index.md` 路徑（GitHub 上看不到音檔，請使用者在本機點 ▶ 重聽）。

8. **確認後開 PR 並 merge**：使用者確認（或指出要修改的地方，改完再重給連結）後，才開 PR；合併方式依使用者指示（PR + Squash and merge，或直接合併），使用者沒說就先問。
