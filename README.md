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

```bash
python3 scripts/watch_archive.py "<影片網址>"          # 下載、Groq 轉錄、截圖、產生 report.docx / report.md
python3 scripts/build_report.py watch-output/<資料夾>   # 編輯 summary.md / meta.json 後重建報告
```

- 輸出在 `watch-output/<日期>_<平台>_<標題>__<影片ID>/`，同一影片 ID 只會有一個資料夾。
- 報告檔名：`<日期>_<平台>_<標題前20字>__<ID>_report.docx`；影片（`--keep-media`）只存本機。
- 完整步驟見 `.claude/skills/watch-archive/SKILL.md`，在 Claude Code 說「用 watch-archive 處理 <網址>」即可。
