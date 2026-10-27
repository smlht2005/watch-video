# 注意事項與流程圖維護

> 含流程圖的文字版與重新產生 PNG 的指令。

- TikTok 短網址（vt.tiktok.com）自動解析成真正的影片 ID；Facebook 標題的「views · reactions |」前綴與作者後綴會自動去除，原始標題在 `meta.json.title_raw`。
- 簡轉繁採台灣用字，技術詞會被換成台灣詞（算子→運算元、優化→最佳化）；OpenCC 對「里／裡」等一對多字有漏轉，由 `glossary/common.json` 兜底。
- Groq 轉錄有誤聽很正常；提示詞只提高機率，詞典才是確定的修正。
- 宗教／佛學講座：有 `glossary/domains/pure-land.json`（淨土宗、台中蓮社、雪公講稿常見專名）。只對單支影片成立的誤聽（例如「欣、厭」被聽成「心、願」，「心」字到處都有，放進詞典會誤傷）記在 `known_asr_errors`，不要放進詞典。
- YouTube 在雲端常回 403／429「Sign in to confirm you're not a bot」：提供 cookies.txt，`WATCH_COOKIES_FILE=<檔>`，或把 cookies.txt 全文放進環境 secret `WATCH_COOKIES_CONTENT`（下載時寫成 0600 暫存檔、結束即刪）；本機可用 `WATCH_COOKIES_FROM_BROWSER=firefox`。建議用專用小帳號匯出，絕不 commit 或印出 cookies。沒有 deno 但有 node 時，下載自動加 `--js-runtimes node`。
- 失敗時回報錯誤類別與原因（網路／下載／轉錄／權限），不要印出 key。
- 版權：來源是他人影片；repo 設為 private 時僅供個人參考，改 public 或分享前不要附影片。

## 流程圖文字版

```text
網址 ─▶ 0 環境 ─▶ 1 選參數(不強制 --lang；長錄影加 --timestamps/--resolution；本地轉錄加 --local；講座／講經加 --clean-fillers) ─▶ 2 歸檔(下載→平台字幕或 Groq／WhisperX 轉錄→偵測語言→中文轉繁體→詞典校正→(講座／講經)去語助詞→截圖→報告)
     ─▶ 3 校稿(先驗收：語言錯／重複幻覺／30 秒漏轉（已自動補漏）／提示詞外洩→保存舊稿後回到 2 重跑、兩次互補；第一輪批次替換（佛經講解座且有燒入字幕才加做字幕 OCR 比對，超過 30 分鐘自動分段、可續跑、--background 低負載）→第二輪逐行重讀全文；佛學／講經：推測詞用 clip_check.py --wait-confirm 剪音檔給使用者聽音確認) ─▶ 4a 看截圖分投影片或主題(slides；明說步驟的影片一步驟一段一張圖，否則每段 2–4 分鐘；pick_frames.py 逐秒挑「對到重點」的截圖並人工確認；截圖不足→補 cue 回到 2 重跑；講者交疊→改挑乾淨投影片)
     ─▶ 4b 補內容(摘要/關鍵字/校正/思維導圖 mindmap.md；非中文→transcript.zh.md) ─▶ 4c 補充資料(選用 supplement.md；畫面有講者沒唸的原文→逐字抄進補充；有原講稿→二次校對) ─▶ 4d 電腦工具教學→操作 SOP(選用 sop.md) ─▶ 5 重建報告 ─▶ 5b 目視檢查 ─▶ 6 交付 ─▶ 7 提交＋給確認連結 ─▶ 使用者確認 ─▶ 8 PR＋merge
```

## 重新產生流程圖 PNG

藍＝腳本自動、橘＝Claude 判斷、綠＝交付；黃色虛線是兩條重跑回圈：「截圖不足時補 cue 重跑」（4a→2）與「語言錯／整段漏轉時重跑」（3→2）；圖源 `docs/watch-archive-flow.svg`。改圖後重新產生 PNG：
- 雲端（Linux）：`/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox --hide-scrollbars --window-size=1600,1100 --screenshot=docs/watch-archive-flow.png file://$PWD/docs/watch-archive-flow.svg`，再用 PIL 裁成 1600×900（視窗外框會吃掉底部，故先開大再裁）。
- Windows：`"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu --hide-scrollbars --window-size=1600,900 --screenshot=<絕對路徑>\docs\watch-archive-flow.png file:///<絕對路徑>/docs/watch-archive-flow.svg`（直接 1600×900，不必裁）。微軟正黑體比文泉驛寬，改字後要看圖確認沒有超出方框。
