# watch-video

Claude Code 的 `/watch` skill：把影片網址或本機檔案轉成帶時間戳的畫面與逐字稿，讓 Claude 回答影片內容。

- Skill 來源：[bradautomates/claude-video](https://github.com/bradautomates/claude-video)（v0.3.2，MIT），位於 `.claude/skills/watch/`
- `.claude/hooks/session-start.sh`：雲端 session（`CLAUDE_CODE_REMOTE=true`）啟動時自動安裝 `yt-dlp`，並在缺少設定時寫入預設值（本機引擎、`balanced`、僅使用字幕）
- `.claude/settings.json`：註冊上述 SessionStart hook

## 使用

```text
/watch <影片網址或本機路徑> 請摘要內容並附時間戳
/watch video.mp4 --start 2:15 --end 2:45
/watch video.mp4 --detail transcript
```

需要 Python 3.10+、ffmpeg；yt-dlp 由 hook 自動安裝。網址影片能否下載取決於環境的網路政策。

## 影片 → 圖文報告流程（watch-archive）

把影片轉成「畫面 + 逐字稿」的圖文報告（Word / Markdown），並依影片 ID 歸檔，方便日後查找。

### 事前準備

- 環境變數 `GROQ_API_KEY`（無字幕時用 Groq Whisper 轉錄；不要把 key 寫進任何檔案）
- `python3 .claude/skills/watch/scripts/setup.py --backend groq --detail balanced`
- `pip install python-docx`（產生 Word 檔）；轉 PDF 目視檢查另需 LibreOffice

### 指令

```bash
python3 scripts/watch_archive.py "<影片網址>" [--question "..."] [--keep-media]
python3 scripts/build_report.py watch-output/<資料夾>   # 編輯 summary.md / meta.json 後重建報告
```

在 Claude Code 說「用 watch-archive 處理 <網址>」，會依 `.claude/skills/watch-archive/SKILL.md` 完成整套流程（含補寫摘要與關鍵字、傳送 Word 檔）。

### 輸出結構

```text
watch-output/
├── index.md                                   # 所有影片索引
└── <日期>_<平台>_<標題>__<影片ID>/              # 同一影片 ID 只會有一個資料夾，重跑為更新
    ├── <stem>_report.docx / <stem>_report.md  # 圖文報告（摘要、名詞說明、畫面+逐字稿、關鍵字標籤）
    ├── meta.json                              # 網址、標題、上傳者、轉錄來源、關鍵字、已知轉錄錯誤
    ├── transcript.md                          # 原始逐字稿（不修改）
    ├── summary.md                             # 摘要（時間戳重點 + 名詞/縮寫說明）
    ├── frames/、frames.json                   # 截圖與其時間戳（小檔，進 git）
    └── media/<stem>_video.<ext>               # 僅 --keep-media；只存本機（gitignore）
```

`<stem>` = `<日期>_<平台>_<標題前20字>__<影片ID>`，單看檔名即可辨識是哪支影片。

### `meta.json` 中重跑不會被覆蓋的欄位

| 欄位 | 用途 |
|---|---|
| `keywords` | 整份報告的關鍵字標籤 |
| `section_keywords` | 各畫面標籤，key 為畫面起始時間，如 `"00:12"` |
| `known_asr_errors` | 轉錄誤聽校正（時間、聽成、應為） |
| `first_archived` | 首次歸檔日期 |

### 注意事項

- `meta.json.transcript_source` 標示逐字稿來源：`whisper (groq)` 為語音轉錄，否則為平台字幕。
- 影片檔不進 git；報告內附來源網址的超連結。他人影片僅供個人參考，repo 改為 public 或分享前請勿附影片。
- 開發請在 `claude/...` 分支進行，合併後的分支不要重用。
