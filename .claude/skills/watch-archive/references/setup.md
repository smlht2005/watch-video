# 步驟 0：環境

> 含 Windows 本機注意事項。

0. **環境**：確認 Groq key 是否存在（環境變數 `GROQ_API_KEY` 或 `~/.config/watch/.env`；只報有/沒有與長度）。有就預設用 Groq 轉錄；沒有則依 `setup.py --json` 的 `whisper_backend`（例如本地 WhisperX），兩者都沒有時，無字幕影片會拿不到逐字稿，要先告知使用者。**雲端 session（`CLAUDE_CODE_REMOTE=true`）只能用 Groq**：容器沒有 WhisperX，不要加 `--local`；沒有 key 就先告知使用者到環境 secret 設定 `GROQ_API_KEY`。確認 `pip install python-docx opencc-python-reimplemented`。
   若 `.claude/skills/watch` 尚未設定，先跑 `python3 .claude/skills/watch/scripts/setup.py --engine local --backend groq --detail balanced`（沒有 Groq key 時把 `groq` 換成 `whisperx`）（exit 0；一定要帶 `--engine local`，否則有 `GEMINI_API_KEY` 時會改走 Gemini，不產生截圖與逐字稿）。
   從最新的 `main` 開新分支 `claude/...`（不要重用已合併的分支）。
   **Windows 本機**：
   - 所有 `python` 指令都要在 `PYTHONUTF8=1` 下執行（使用者環境變數；設定前開的 session 要在指令前加）。否則 `watch_archive.py` 會用 cp950 解碼 `watch.py` 的中文輸出，直接以 `TypeError: 'NoneType'` 失敗。
   - YouTube 回「Sign in to confirm you're not a bot」時，以 `WATCH_COOKIES_FROM_BROWSER=firefox` 只傳給這次執行（不寫進設定檔）。Windows 的 Chrome／Edge 有 App-Bound 加密，yt-dlp 會出現 `Failed to decrypt with DPAPI`，關掉瀏覽器也沒用，不要再試；沒有 Firefox 就請使用者匯出 cookies.txt（存在 repo 外）改用 `WATCH_COOKIES_FILE`。讀瀏覽器 cookies 前先問使用者。
   - Groq key 可能設在系統層級（Machine）環境變數，session 讀不到時用 `[Environment]::GetEnvironmentVariable('GROQ_API_KEY','Machine')` 取值，只傳給該次執行，不印出。
