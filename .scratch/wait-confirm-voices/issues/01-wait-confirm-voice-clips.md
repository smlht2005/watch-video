# 佛學／講經：推測詞自動剪音檔，放 waitConfirm 資料夾，連結點選重聽確認

Status: ready-for-agent
Branch: 從最新 main 開新 `claude/...`；`scripts/clip_check.py` 已存在於 `claude/clip-check`（`880ff7b`，未開 PR），先合併或沿用它

## 背景

第 104 集與淨土安心法門(四)校稿時，使用者要逐個聽音確認推測詞（「一介螻螘，萬聖互援」「學員長」「難侵」）。每次都要手動找時間點、剪音檔、貼路徑，來回很多輪。
實例：(四)的「螻蟻→螻螘」「覆援→互援」「難清→難侵」，三處都是使用者聽音或看投影片才定案；我看不到講者拿的投影片，所以只靠逐字稿推不出來。

## 要做的事

1. 領域是佛學／講經（`meta.json.video_type == "lecture"` 或 `category == "佛學"`）時，歸檔流程在寫完 `known_asr_errors` 後，對每一筆標「推測」的詞自動剪音檔。
2. 每筆存成 `watch-output/<領域>/<資料夾>/waitConfirm/NN_MM-SS_<詞>.mp3`（前 5 秒、後 25 秒；用 `scripts/clip_check.py` 的 `window`／`download`），同一時段的多筆合併成一個音檔。
3. 產生 `waitConfirm/index.md`：每筆一列，內容是「時間點、逐字稿該行、目前寫法、候選寫法、音檔連結 `[▶ 重聽](./01_….mp3)`、截圖連結」；使用者點連結就能重聽。
4. 使用者確認後的結果寫回 `known_asr_errors`（把「推測」改成「使用者聽音確認」）並重建報告；確認完 `waitConfirm/` 不入庫（他人影片音檔，加進 `.gitignore`，同 `media/`）。
5. `review_links.py` 交付連結時，附上 `waitConfirm/index.md`（連結用本機路徑；GitHub 上看不到音檔，需說明）。
6. 更新流程與文件：`.claude/skills/watch-archive/SKILL.md` 與 references（`proofread.md`、`deliver.md`）、`CLAUDE.md` 硬規則、`docs/watch-archive-flow.png` 流程圖與 `references/notes.md` 文字版、`README.md`。
7. 測試：`known_asr_errors` 取出推測項、時間點解析（逐字稿找不到時間點時跳過並警告）、index.md 產生。

## 注意

- 逐字稿的時間點要從 `known_asr_errors` 的 `time`（若有）或在逐字稿找 `heard` 字串；先確認 `meta.json` 現有欄位再設計，不夠就在 `known_asr_errors` 加 `time`。
- 影片不在本機時 `clip_check.py` 會用 yt-dlp 下載該時段；YouTube 被擋或需 cookies 時要有清楚錯誤訊息（Windows 只能用 Firefox cookies）。
- 投影片上的字（例如「難侵」）靠聽音聽不出，要同時附該時間附近的截圖：`--frame`。
- 硬規則不變：絕不印出 API key；影片檔不入庫。

## Comments
