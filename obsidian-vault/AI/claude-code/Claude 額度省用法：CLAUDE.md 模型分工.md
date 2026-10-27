---
title: "Claude 額度省用法：CLAUDE.md 模型分工"
type: video-note
source: "https://www.instagram.com/reel/DeUPXT1s44U/?dlrf=N3lvc2d2cHVvYjFx"
platform: "Instagram"
video_id: "DeUPXT1s44U"
uploader: "S的 AI 研究所"
category: "AI/claude-code"
date: "2026-10-11"
status: unreviewed
origin_folder: "watch-output/AI/claude-code/2026-10-11_Instagram_Claude-額度省用法-CLAUDE-md-模型分工__DeUPXT1s44U"
generated_by: watch-archive
aliases:
  - "Claude 額度省用法：CLAUDE.md 模型分工"
tags:
  - "watch-archive"
  - "AI/claude-code"
  - "Claude-額度"
  - "CLAUDE-md"
  - "Claude-Code"
  - "Opus-5-5"
  - "Sub-Agent"
  - "模型分工"
  - "省成本"
---

# Claude 額度省用法：CLAUDE.md 模型分工

## 摘要

**一句話重點：** 講者（S 的 AI 研究所）主張：在 CLAUDE.md 規定「複雜任務才用最強模型、簡單工作用 Opus 5.5、可拆分的任務交給 Sub Agent」，就能更省 Claude 額度。

| 時間 | 重點 |
|---|---|
| 00:00 | 問題：Claude 額度常常不到一天就用完；Opus 5.5 之後有個隱藏用法 |
| 00:07 | 作法：建立 CLAUDE.md（Claude Code 每次工作前都會讀的說明書） |
| 00:12 | 在裡面寫分工規則：複雜任務才交給最強模型，簡單工作用 Opus 5.5；適合拆開的任務交給不同 Sub Agent |
| 00:23 | 好處：不必每個任務都用最高成本模型，Claude 依工作選模型與 Agent |
| 00:29 | 講者稱 Opus 5.5 成本比 Opus 5 便宜近一半、輸出快超過 30% |
| 00:35 | 行動呼籲：常把額度用爆者一定要加；留言「省錢」索取完整指令 |

### 名詞與縮寫
- **CLAUDE.md**：Claude Code 啟動工作前讀取的專案說明檔，可放長期規則。
- **Sub Agent**：由主 agent 派出、處理拆分子任務的代理。
- **Opus 5.5**：影片中提到的模型；講者將其定位為「處理簡單工作、較便宜」的選項。

### 轉錄校正備註
- 語言：自動偵測為中文（`detected_language: zh`），Whisper（Groq）轉錄，已簡轉繁並以 `glossary/domains/claude-code.json` 修正 Claude／CLAUDE.md 等寫法。
- 「最強的模型」講者未點名；據〈補充資料〉S1（貼文提供的完整 CLAUDE.md）推定指 Fable 5.1（非補充直接寫明）。
- 數字（便宜近一半、快 30%）皆為講者主張，**未經查證**；且口述「快一半」與畫面圖示 -40% 略有出入。
- 影片為口播＋圖示，內容短（42 秒）；完整 CLAUDE.md 影片中未揭露，已由使用者提供並收錄於〈補充資料〉（`supplement.md`）。

## 補充資料

### S1｜留言（推測）：影片提到的完整 CLAUDE.md
- 來源：使用者貼上的文字，使用者表示為講者回覆「省錢」留言後傳送的內容（開頭為「這是影片提到的CLAUDE.md👇」；原始位置未經確認）；取得日期：2026-10-11；取得方式：使用者貼上。
- 為何需要補充：影片只在 `frame_0007.jpg`（00:14）短暫露出 CLAUDE.md 的前兩行；完整內容講者要求觀眾留言索取（00:38–00:40），影片本身沒有揭露。

### 原文（逐字）

```
永遠不要自己執行任務，一律交給 sub-agent 處理。

不要所有任務都使用 Fable。較簡單的任務請使用 Opus 5.5。

### 模型路由
- **Fable 5.1**：系統架構、困難的 Bug、程式碼審查
- **Opus 5.5**：修改、測試、文件、重構
- **Haiku 4.5**：資料查詢與摘要
- 每次呼叫 Agent 時，都必須指定 `model`

### 任務委派
- 每個任務交給一個 sub-agent，執行前先規劃
- 彼此獨立的 sub-agent 任務要平行執行
- 只閱讀 sub-agent 的報告，不要直接讀取檔案
```

### Claude 的對照分析

- 與影片一致：`frame_0007.jpg`（00:14）畫面兩行與原文第 1–2 句意思相同、用字略異（畫面為「Sub agent」，原文為「sub-agent」；第二行只打到「簡單」，游標停在該處）；講者口述「複雜的任務才交給最強的模型、簡單的工作用 Opus 5.5、可拆分的任務交給 Sub Agent」與原文方向一致。
- 補充直接寫明（影片沒有的）：每次呼叫 Agent 都必須指定 `model`；彼此獨立的 sub-agent 任務平行執行；只讀 sub-agent 的報告、不直接讀檔；以及 Haiku 4.5 負責資料查詢與摘要的分工。
- 據此推定（非補充直接寫明）：講者口述的「最強的模型」未點名，但原文寫明 Fable 5.1 負責系統架構、困難的 Bug、程式碼審查，且畫面出現「不要所有任務都使用 Fable」，因此推定指 Fable 5.1。講者口述的「簡單的工作」對應原文中 Opus 5.5 的範圍（修改、測試、文件、重構）。

### 備註

- 以上為貼文所述，逐字保留；原文含 Markdown 標記（`**`、反引號），在 Word 版會原樣顯示。
- 模型名稱與版本（Fable 5.1、Opus 5.5、Haiku 4.5）取自貼文，未經查證；模型分工能省多少額度是講者的主張，同樣未查證，是否適用請依自己的專案評估。

## 來源

- 原始資料夾：`watch-output/AI/claude-code/2026-10-11_Instagram_Claude-額度省用法-CLAUDE-md-模型分工__DeUPXT1s44U`
- 逐字稿來源：whisper (groq)
