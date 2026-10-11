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
