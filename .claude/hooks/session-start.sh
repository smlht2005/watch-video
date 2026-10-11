#!/usr/bin/env bash
# 雲端 session 啟動時安裝 /watch skill 所需的 yt-dlp、watch-archive 所需的 Python 套件（python-docx、opencc），並在缺少設定時寫入預設設定
set -u

# 僅在 Claude Code on the web（雲端容器）執行；本機環境由使用者自行管理
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
SETUP="$PROJECT_DIR/.claude/skills/watch/scripts/setup.py"

if ! command -v yt-dlp >/dev/null 2>&1; then
  python3 -m pip install -q -U "yt-dlp[default,curl-cffi]" >/dev/null 2>&1 \
    || echo "/watch: yt-dlp 安裝失敗，請手動執行 pip install -U \"yt-dlp[default,curl-cffi]\""
fi

# watch-archive：python-docx（產生 Word）、opencc（簡轉繁）。缺任何一個才安裝，已有則不動。
if ! python3 -c "import docx, opencc" >/dev/null 2>&1; then
  python3 -m pip install -q -r "$PROJECT_DIR/requirements.txt" >/dev/null 2>&1 \
    || echo "watch-archive: Python 套件安裝失敗，請手動執行 pip install -r requirements.txt"
fi

# 首次執行時套用預設：本機引擎、balanced 抽幀。
# 環境有 GROQ_API_KEY（建議設為環境 secret）時以 Groq 作為語音轉錄備援，否則僅使用字幕。
if [ ! -f "$HOME/.config/watch/.env" ] && [ -f "$SETUP" ]; then
  BACKEND=none
  [ -n "${GROQ_API_KEY:-}" ] && BACKEND=groq
  python3 "$SETUP" --engine local --backend "$BACKEND" --detail balanced >/dev/null 2>&1 || true
fi

exit 0
