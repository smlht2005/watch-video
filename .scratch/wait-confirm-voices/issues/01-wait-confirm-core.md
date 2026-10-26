# 01：核心流程：推測詞剪成待確認音檔與 index.md

**What to build:** 對佛學／講經影片資料夾執行 `clip_check.py --wait-confirm <資料夾>`，為每個**推測詞**（`known_asr_errors` 中 `status == suspected` 且 `time` 為單一時間點）剪出**待確認音檔**（前 5 秒、後 25 秒）與 720p 截圖，放進 `waitConfirm/`，並產生 `index.md`。使用者點 `[▶ 重聽]` 就能聽、看圖。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 新增 `known_asr_errors` 的 `status` 欄位（`suspected`／`confirmed`）；沒有此欄位的舊資料視為不剪
- [ ] 只處理 `suspected` 且 `time` 為 `MM:SS`／`H:MM:SS` 的項目；區間、多段、「全片」、補漏類跳過並印警告
- [ ] 輸出 `waitConfirm/NN_MM-SS_<詞>.mp3`、同名 `.jpg`、`index.md`
- [ ] `index.md` 每筆一列：時間點、逐字稿該行、`heard`、`expected`（多候選以「／」分隔照列）、`[▶ 重聽]`、截圖連結
- [ ] 時間點找不到對應逐字稿行時只警告並跳過，不中斷其他項目
- [ ] 只在 `video_type == "lecture"` 或 `category == "佛學"` 時產生；其他影片不建立目錄
- [ ] 同一個詞在逐字稿出現多次時，只剪該筆的 `time`
- [ ] 測試在單一接縫（`--wait-confirm` 入口），剪音檔與截圖用替身，不連網、不呼叫 yt-dlp／ffmpeg；涵蓋上述各項

## Comments
