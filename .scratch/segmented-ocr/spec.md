Status: ready-for-agent

# 字幕 OCR 分段執行：每 10 分鐘一段、可續跑、低負載

## Problem Statement

`scripts/subtitle_ocr.py run` 一次跑完整支影片。74 分鐘的影片 v4 約一小時、改 v5 還要慢約 3 倍，期間筆電被拖慢（使用者同時開別的 Claude 做別的專案），session 一結束或被關掉，辨識階段又不輸出進度、沒有存檔，整段白跑（第 104 集就發生過）。

第 104 集靠我臨時寫在暫存區的 `drive.py`／`drive2.py` 才跑完：每 10 分鐘一段各存 `seg_NNNNN.json`、已完成的跳過、`.lock` 檔避免兩個驅動撞同一段、`Start-Process` 脫離 session、優先權 Idle，最後手動合併成 `ocr.json`。這些沒進 repo，下一支影片要重寫。

## Solution

把這套做法收進 `subtitle_ocr.py run`：加 `--segment-min 10`，整支切成固定長度的段落，每段辨識完立刻存檔；中斷後重跑自動跳過已完成的段落；全部完成後合併成 `--out`。每段結束印進度（符合「長時間背景工作每約 10 分鐘回報」）。另有 `status` 看進度、`--low-priority` 降低優先權、`--background` 脫離 session 執行。輸出格式不變（`{秒數: 文字}`），`compare` 不用改。

## User Stories

1. 身為校稿者，我想要 `run --segment-min 10` 把影片切成每 10 分鐘一段，這樣一段跑完就有結果，不會整支白跑。
2. 身為校稿者，我想要每段存成 `seg_NNNNN.json`，這樣中斷後不必重來。
3. 身為校稿者，我想要重跑同一個指令時跳過已完成的段落，這樣續跑就是再下一次同樣的指令。
4. 身為校稿者，我想要全部段落完成後自動合併成 `--out`（格式與現在相同），這樣 `compare` 照舊使用。
5. 身為校稿者，我想要每段結束印「第 N／共 M 段、時間範圍、辨識張數、耗時」，這樣看得到進度。
6. 身為校稿者，我想要 `status` 指令列出完成幾段、剩幾段、哪段正在跑，這樣不必猜它有沒有卡住。
7. 身為校稿者，我想要段落寫檔是原子的（先寫暫存檔再改名），這樣被砍掉時不會留下半個壞檔。
8. 身為校稿者，我想要兩個程序可以同時跑同一支影片而不撞到同一段，這樣能用 2 個程序加快。
9. 身為校稿者，我想要過期的鎖（程序已死）自動被忽略，這樣被砍掉後重跑不會永遠卡住。
10. 身為校稿者，我想要 `--low-priority` 降低辨識程序的優先權，這樣筆電不會被拖慢。
11. 身為校稿者，我想要 `--background` 讓辨識脫離目前 session 在背景跑並寫 log，這樣關掉 Claude 也不會被砍。
12. 身為校稿者，我想要段落邊界不遺失或重複字幕列（每段的取樣點對齊 `--every`），這樣合併後與一次跑完等價。
13. 身為校稿者，我想要 `--start`／`--end` 仍可限制範圍，這樣只想補某一段時可用。
14. 身為維護者，我想要不加 `--segment-min` 時行為與現在完全相同，這樣舊指令與既有測試不受影響。
15. 身為維護者，我想要 skill、references、docs 與記憶都更新成「預設用分段跑」，這樣下次歸檔不會再手寫驅動腳本。

## Implementation Decisions

- 介面：`run` 加 `--segment-min N`（0／未指定＝現行一次跑完）、`--seg-dir DIR`（預設 `<out>.segs/`）、`--low-priority`、`--background`；新增 `status <out>` 子命令。
- 段落檔名 `seg_<起始秒 5 位數>.json`，內容同現行輸出 `{秒數: 文字}`，秒數為整支影片的絕對秒數。段落長度為 `--segment-min` 分鐘，最後一段到 `--end` 或影片結尾。
- 取樣點：每段起點為 `--every` 的整數倍（段長取 `--every` 的倍數），確保合併後與一次跑完取樣點相同。
- 續跑：段落檔存在即視為完成；**不比對內容**。要重做某段就刪該檔。
- 原子寫入：先寫 `seg_NNNNN.json.tmp`，完成後 `os.replace`。
- 鎖：`seg_NNNNN.lock` 以獨佔建立（`O_EXCL`）搶占，內容為 pid 與時間；鎖超過 `--lock-ttl`（預設 30 分鐘）或同機 pid 已不存在視為過期，可接手。段落完成後刪鎖。
- 合併：所有段落都存在才寫 `--out`；缺段時 `run` 結束印「還差哪幾段」並以非 0 結束，不寫不完整的 `--out`。
- 進度：每段結束印一行並 `flush`；`--background` 時同時寫 `<seg-dir>/progress.log`。
- `--low-priority`：Windows 設 Idle 優先權類別，其他平台 `os.nice`；子程序繼承。預設不開。
- `--background`：以同樣參數另起一個脫離 session 的程序（Windows `DETACHED_PROCESS`＋`CREATE_NEW_PROCESS_GROUP`），本程序印 log 路徑後立即結束；隱含 `--low-priority`。
- 辨識模型沿用 `--model`（預設 v5）；v5 建議 `--workers 1～2`、`--every 3`，寫進文件，不改預設值。
- 影片下載、`probe`、`compare` 不變。
- 硬規則不變：不印 API key；影片檔不入庫，段落檔放暫存區或 `--seg-dir` 指定處，不進 repo。
- 分支：從最新 main 開 `claude/segmented-ocr`；使用者確認前不開 PR、不合併。

## Testing Decisions

- 好的測試只驗外部行為：給定影片長度與一個替身的「單段辨識」函式，產出哪些段落檔與合併後的 `--out`；不測內部呼叫順序。
- **測試接縫（一個）**：分段執行的入口函式，注入「取得影片長度」與「辨識一段」兩個替身（不連 ffmpeg／RapidOCR）。
- 要涵蓋：分段邊界（含最後不足一段、`--start`／`--end`）、續跑跳過已完成、缺段不寫 `--out`、合併結果與一次跑完等價、鎖搶占與過期鎖接手、原子寫入（暫存檔不被當成完成）、不加 `--segment-min` 時走舊路徑。
- `status` 與 `--background`／`--low-priority` 的外部行為（輸出文字、log 檔建立、優先權旗標傳遞）用替身驗證，不真的起程序。
- 前例：`tests/test_subtitle_ocr.py`（以資料為輸入、檢查輸出）與 `tests/test_clip_check.py` 的可注入替身寫法。
- 開 PR 前跑全套 `python3 -m unittest discover -s tests`。

## Out of Scope

- 自動判斷何時該用 OCR（仍限佛經講解／講經座且有燒入字幕）。
- GPU 加速、換用更快的模型。
- 多影片排程、佇列。
- 段落結果的雲端備份（記憶已提醒備份到專案外，仍由人工做）。
- `watch_archive.py` 歸檔時自動 `probe`／自動跑 OCR。

## Further Notes

- 實例：第 104 集（72 分鐘）用 2 個程序、`--every 3`、v4，約 40 分鐘完成；v5 約慢 3 倍，所以分段更重要。
- 臨時驅動腳本曾在兩端對跑時撞到同一段（40–50 分），鎖機制就是為此。
- 相關記憶：`ocr-lessons.md`（跑法與教訓）、`watch-104-in-progress.md`。
