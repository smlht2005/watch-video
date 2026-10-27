---
title: "為什麼整個 GitHub 都在瘋傳 REA？別人的程式碼，現在是你的了?"
type: video-note
source: "https://youtu.be/nmzKH9t4Zos?si=MVFw0Spj1_CwBGcK"
platform: "YouTube"
video_id: "nmzKH9t4Zos"
uploader: "P & H"
category: "AI"
date: "2026-10-14"
status: unreviewed
origin_folder: "watch-output/AI/2026-10-14_YouTube_為什麼整個-GitHub-都在瘋傳-REA-別人的程式碼-現在是你的了__nmzKH9t4Zos"
generated_by: watch-archive
aliases:
  - "為什麼整個 GitHub 都在瘋傳 REA？別人的程式碼，現在是你的了?"
tags:
  - "watch-archive"
  - "AI"
  - "REA"
  - "逆向工程"
  - "MCP"
  - "Claude-Code"
  - "Ghidra"
  - "Detect-It-Easy"
  - "Three-js"
  - "DX-Ball"
  - "JADX"
  - "Binwalk"
---

# 為什麼整個 GitHub 都在瘋傳 REA？別人的程式碼，現在是你的了?

## 摘要

**一句話重點**：REA 是一組 MCP server + skill，讓 Claude Code 等 AI 程式能操作逆向工程工具，直接回答「這個 exe／網站是怎麼做的」，每個結論附證據與限制。

| 時間 | 重點 |
|---|---|
| 00:04 | REA 在 GitHub 衝破 8 萬星、登上熱門榜第一（講者主張，未查證）；以蛋糕比喻說明逆向工程 |
| 01:13 | REA 四步驟：直接問 → REA 接手檢查追蹤 → 回傳證據與未知處 → Claude Code 解釋；不同目標需不同工具 |
| 03:02 | 實測一：用 Ghidra 逆向 Windows exe「尾牙抽獎」，約 1.5 分鐘找出密碼 7461（55,666,521 的平方根） |
| 05:56 | 實測二：用 Chrome 連上網站，約 1 分鐘還原背景粒子特效（Three.js、3,000 顆粒子、每幀補 5%） |
| 07:28 | 準確度（DX-Ball 重寫版通過 3,205 個測試案例、63 位元組一致）與限制（遠端伺服器看不到） |

### 名詞與縮寫
- **逆向工程**：從成品倒推設計、結構與做法。
- **MCP server / skill**：讓 AI 程式呼叫外部工具的協定與技能包。
- **Ghidra**：NSA 研究部門開發、2019 年開源的逆向工程工具（講者主張，未查證）。
- **Hopper／IDA Pro／JADX／Binwalk／Detect It Easy**：分別用於原生程式、Android APK、韌體、辨識語言與編譯器。
- **javascript-obfuscator**：JS 混淆工具；**Three.js**：網頁 3D 函式庫。

### 工具對照（影片 02:00–02:26）
| 目標 | 工具 |
|---|---|
| Windows exe／Mac App | Ghidra、Hopper 或 IDA Pro |
| 網頁技術的桌面 App（VS Code、Discord） | Node.js |
| 網站 | Chrome 等瀏覽器 |
| C# Windows 程式 | 不需另外安裝 |
| Android APK | JADX |
| 路由器等韌體 | Binwalk（僅 Linux） |

### 轉錄校正備註
- 逐字稿來源：YouTube 創作者上傳的中文字幕（manual），非語音辨識；畫面硬字幕與之相符。
- 校正：「國家安全域性」→「國家安全局」、「尾牙抽獎。exe」→「.exe」（已進 `glossary/common.json`）。
- 「55,666,521」以字幕為準，驗算 7461² = 55,666,521 成立；此為講者示範數值。
- 影片中的星數、測試案例數、耗時等數字皆為講者主張，未查證。
- 資料處理：此前版本誤用 YouTube 英文自動字幕（見 commit 說明的 bug 修正）。

## 來源

- 原始資料夾：`watch-output/AI/2026-10-14_YouTube_為什麼整個-GitHub-都在瘋傳-REA-別人的程式碼-現在是你的了__nmzKH9t4Zos`
- 逐字稿來源：captions (zh, manual, original)
