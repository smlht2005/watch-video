Status: ready-for-agent

# 佛學／講經：推測詞自動剪音檔，放 waitConfirm 供點選重聽確認

## Problem Statement

歸檔佛學／講經影片時，校稿會遇到只能靠聽音或看投影片才能定案的**推測詞**（例如「螻蟻→螻螘」「覆援→互援」「難清→難侵」）。目前我要手動找時間點、剪音檔、貼路徑，來回很多輪，才能逐個聽音確認。

## Solution

校稿寫完 `known_asr_errors` 後，執行一個指令，就為每個**推測詞**自動剪出**待確認音檔**與截圖，放在該影片資料夾的 `waitConfirm/`，並產生 `index.md`。我在 `index.md` 點連結重聽、看圖，把結果告訴 Claude；Claude 把該筆改成**使用者聽音確認**並重建報告。

## User Stories

1. 身為校稿者，我想要一個指令為所有推測詞一次剪好音檔，這樣我不必手動找時間點。
2. 身為校稿者，我想要 `index.md` 每筆一列，列出時間點、逐字稿該行、`heard`、`expected`，這樣我一眼看出要確認什麼。
3. 身為校稿者，我想要點 `[▶ 重聽]` 就播放該片段，這樣不必貼路徑。
4. 身為校稿者，我想要音檔取該時間點前 5 秒、後 25 秒，這樣有足夠上下文。
5. 身為校稿者，我想要每筆附一張 720p 截圖，這樣投影片上的字（聽不出來的）也能核對。
6. 身為校稿者，我想要相距 30 秒內的時間點共用一個音檔，並標出該詞在片段內的偏移，這樣不會重複下載與重複聽。
7. 身為校稿者，我想要只處理 `status` 為 `suspected` 的項目，這樣已確認的不會再被剪。
8. 身為校稿者，我想要區間、多段、「全片」、補漏類的項目被跳過並印警告，這樣我知道哪些沒處理、為什麼。
9. 身為校稿者，我想要沒有 `status` 欄位的舊資料被視為不剪，這樣舊影片不會被誤動。
10. 身為校稿者，我想要非佛學／講經的影片不產生 `waitConfirm/`，這樣其他領域流程不受影響。
11. 身為校稿者，我想要聽完用對話回報，由 Claude 把 `status` 改成 `confirmed`、在 `expected` 加「使用者聽音確認」並重建報告，這樣我不必手改檔案。
12. 身為校稿者，我想要 YouTube 被擋或需要 cookies 時有清楚錯誤訊息（Windows 提示用 Firefox cookies），這樣我知道怎麼處理。
13. 身為校稿者，我想要 `waitConfirm/` 不入庫，這樣他人影片的音檔不會進 repo。
14. 身為交付者，我想要 `review_links.py` 有 `waitConfirm/` 時列出本機 `index.md` 路徑並註明 GitHub 上看不到音檔，這樣使用者知道要在本機點。
15. 身為維護者，我想要 `GLOSSARY.md` 定義推測詞、待確認音檔、使用者聽音確認，這樣之後的對話用語一致。
16. 身為維護者，我想要 skill、references、CLAUDE.md、README 與流程圖都更新，這樣下次歸檔會記得做這一步。
17. 身為維護者，我想要在時間點找不到對應逐字稿行時只警告不中斷，這樣一筆壞資料不會擋住其他項目。

## Implementation Decisions

- `known_asr_errors` 每筆新增 `status`：`suspected`（推測）或 `confirmed`（使用者聽音確認）。舊資料不回補。
- 只剪 `status == suspected` 且 `time` 為單一 `MM:SS`（或 `H:MM:SS`）的項目；其餘跳過並警告。
- 適用範圍：`meta.json.video_type == "lecture"` 或 `category == "佛學"`。
- 觸發方式：`clip_check.py` 加 `--wait-confirm <資料夾>`；`watch_archive.py` 不自動跑（`known_asr_errors` 是校稿時才人工寫）。skill 流程在校稿後加一步提醒。
- 輸出：`waitConfirm/NN_MM-SS_<詞>.mp3`、同名 `.jpg`、`index.md`。窗格前 5 秒、後 25 秒；相距 30 秒內的時間點合併為一個 mp3，`index.md` 仍每筆一列並標出片段內偏移。
- `index.md` 欄位：時間點、逐字稿該行、`heard`、`expected`（多個候選用「／」分隔，照樣列出）、`[▶ 重聽]`、截圖連結。
- 重複出現的詞只剪該筆 `time`；要聽別處用 `clip_check.py --at` 手動剪。
- 影片不在本機時，沿用 `clip_check.py` 以 yt-dlp 只下載該時段。
- 確認後寫回由 Claude 在對話中完成，不做勾選或互動腳本。
- `waitConfirm/` 加進 `.gitignore`（同 `media/`），確認後不自動刪。
- `review_links.py`：有 `waitConfirm/` 才列本機路徑。
- 新建根目錄 `GLOSSARY.md`，先放三個詞，只寫定義。
- 不寫 ADR。
- 硬規則不變：不印 API key；影片檔不入庫。
- 分支：從 `claude/clip-check` 接著做，同一個 PR；使用者確認前不開 PR、不合併。

## Testing Decisions

- 好的測試只驗外部行為：給定 `meta.json` 內容與逐字稿，產出哪些檔案與 `index.md` 內容；不測內部函式的呼叫順序。
- **測試接縫（一個）**：`clip_check.py` 的 `--wait-confirm` 入口函式。剪音檔與截圖的動作以可注入的替身取代（不連網、不呼叫 yt-dlp／ffmpeg），測試只看產出的檔名清單與 `index.md`。
- 要涵蓋：只取 `suspected`、略過區間／全片／無 `status`、合併 30 秒內時間點與偏移標示、時間點找不到逐字稿行時警告並跳過、非佛學／講經不產生目錄。
- 前例：`tests/test_clip_check.py`（同分支，已有 window／時間解析測試）與 `tests/test_slide_text_check.py` 的以檔案為輸入、檢查輸出文字的寫法。

## Out of Scope

- 自動判斷哪些詞該標推測（仍由校稿者人工寫 `known_asr_errors`）。
- 對逐字稿中同詞的其他出現處批次剪音。
- 互動式勾選確認、網頁介面。
- 非佛學／講經領域。
- 舊影片 `known_asr_errors` 的 `status` 回補。
- 自動刪除 `waitConfirm/`。

## Further Notes

- 實例：淨土安心法門(四)的「螻蟻→螻螘」「覆援→互援」「難清→難侵」，都是使用者聽音或看投影片才定案。
- 取代舊的 `issues/01-wait-confirm-voice-clips.md` 的範圍描述；實作 ticket 可由 `/to-tickets` 從本 spec 拆出。
