# watch-video

Claude Code 的 `/watch` skill：把影片網址或本機檔案轉成帶時間戳的畫面與逐字稿，讓 Claude 回答影片內容。

- Skill 來源：[bradautomates/claude-video](https://github.com/bradautomates/claude-video)（v0.3.2，MIT），位於 `.claude/skills/watch/`
- `.claude/hooks/session-start.sh`：雲端 session（`CLAUDE_CODE_REMOTE=true`）啟動時自動安裝 `yt-dlp` 與 `requirements.txt` 的 Python 套件（`python-docx`、`opencc-python-reimplemented`），並在缺少設定時寫入預設值（本機引擎、`balanced`、僅使用字幕）
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
- `pip install -r requirements.txt`（雲端 session 由 hook 自動安裝；產生 Word 檔；簡體逐字稿自動轉繁體）；轉 PDF 目視檢查另需 LibreOffice

### 流程

```mermaid
flowchart LR
    A[影片網址] --> B[watch_archive.py]
    B --> B1[解析平台 / 影片 ID<br/>TikTok 短網址先解析]
    B1 --> B2[下載 + 截圖]
    B2 --> B3[Groq Whisper 轉錄<br/>--lang / 詞典提示詞]
    B3 --> B4[簡轉繁 OpenCC<br/>全形標點 + 詞典替換]
    B4 --> C[(watch-output/資料夾)]
    C --> D[Claude 校稿與補內容<br/>summary / keywords / 校正]
    D --> E[build_report.py]
    E --> F[report.docx / report.md]
    D -. 穩定錯誤 .-> G[glossary/ 詞典]
    G -. 下次轉錄 .-> B3
```

### 指令

```bash
python3 scripts/watch_archive.py "<影片網址>" [--lang zh] [--glossary ai-chips,electronics] [--title "自訂標題"] [--terms "詞1,詞2"] [--question "..."] [--keep-media]
python3 scripts/build_report.py watch-output/<資料夾>   # 編輯 summary.md / meta.json 後重建報告
```

在 Claude Code 說「用 watch-archive 處理 <網址>」，會依 `.claude/skills/watch-archive/SKILL.md` 完成整套流程（選參數 → 歸檔 → 校稿 → 補摘要與關鍵字 → 重建報告 → 傳送 Word 檔 → 提交）。

### 提高轉錄準確度

- `--lang zh`：指定 Whisper 語言（預設自動偵測；中文影片建議加上）。
- `--glossary ai-chips,electronics`：載入詞典領域（`common` 一律載入；重跑會記住，存在 `meta.json.glossaries`）。詞典放在 `glossary/`：
  - `glossary/common.json`：任何主題都不會出錯的修正（例如簡轉繁後的「里／裡」）。
  - `glossary/domains/<領域>.json`：領域詞典，目前有 `ai-chips`、`electronics`。新增領域只要新增一個檔案。
  - 每個檔案有 `terms`（Whisper 提示詞，只放整個詞，總長約 200 字內；選中的領域優先）與 `replace`（轉錄後固定替換，key 用繁體、至少 3 字或帶上下文）。
  - 單支影片才成立的修正，不要放進詞典，改用 `--terms` 或 `meta.json.known_asr_errors`。
  - `WATCH_GLOSSARY_DIR` 可指向別處（例如獨立的詞典 repo），方便跨專案共用。
- `--terms "詞1,詞2"`：只對這一支影片額外提示的詞（人名、術語）。
- Whisper 的語言與提示詞由 `.claude/skills/watch/scripts/whisper.py` 的環境變數 `WATCH_WHISPER_LANGUAGE` / `WATCH_WHISPER_PROMPT` 傳入（本專案對上游 skill 的小幅修改，更新上游時需重新套用）。

### 輸出結構

```text
watch-output/
├── index.md                                   # 所有影片索引
└── <日期>_<平台>_<標題>__<影片ID>/              # 同一影片 ID 只會有一個資料夾，重跑為更新
    ├── <stem>_report.docx / <stem>_report.md  # 圖文報告（摘要、名詞說明、畫面+逐字稿、關鍵字標籤）
    ├── meta.json                              # 網址、標題、上傳者、轉錄來源、關鍵字、已知轉錄錯誤
    ├── transcript.md                          # 逐字稿（預設轉為繁體中文，時間戳不變）
    ├── transcript.raw.md                      # 轉繁體前的原始轉錄（僅在內容有變動時產生）
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
| `slides` | 投影片分段（`start`、`frame`、`title`、`note`、`keywords`）；有設定時每張投影片只放一張圖，說明文字與逐字稿接在下方 |
| `known_asr_errors` | 轉錄誤聽校正（時間、聽成、應為） |
| `first_archived` | 首次歸檔日期 |
| `title_override` | `--title` 指定的標題（重跑沿用） |
| `glossaries` | `--glossary` 選用的詞典領域（重跑沿用） |

### 注意事項

- 支援 Facebook、YouTube、TikTok（含 `vt.tiktok.com` 短網址，會先解析出真正的影片 ID）。標題只有 #標籤 或太雜亂時，用 `--title` 指定；之後重跑會記住（`meta.json.title_override`）。
- `meta.json.transcript_source` 標示逐字稿來源：`whisper (groq)` 為語音轉錄，否則為平台字幕。
- 影片檔不進 git；報告內附來源網址的超連結。他人影片僅供個人參考，repo 改為 public 或分享前請勿附影片。
- 開發請在 `claude/...` 分支進行，合併後的分支不要重用。
