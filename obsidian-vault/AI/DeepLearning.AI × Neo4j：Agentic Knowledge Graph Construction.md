---
title: "DeepLearning.AI × Neo4j：Agentic Knowledge Graph Construction（知識圖譜與 Google ADK 多代理）"
type: video-note
source: "https://x.com/Grow_withAI/status/2108904705854411211"
platform: "X"
video_id: "2108904705854411211"
uploader: "Ryan Carter"
category: "AI"
date: "2026-10-12"
status: unreviewed
origin_folder: "watch-output/AI/2026-10-12_X_DeepLearning-AI-×-Neo4j-Agentic-Knowledg__2108904705854411211"
generated_by: watch-archive
aliases:
  - "DeepLearning.AI × Neo4j：Agentic Knowledge Graph Construction（知識圖譜與 Google ADK 多代理）"
tags:
  - "watch-archive"
  - "AI"
  - "知識圖譜"
  - "Neo4j"
  - "Cypher"
  - "多代理系統"
  - "Google-ADK"
  - "GraphRAG"
  - "領域圖-詞彙圖-主題圖"
  - "LiteLLM"
  - "tool-context"
  - "session-state"
---

# DeepLearning.AI × Neo4j：Agentic Knowledge Graph Construction（知識圖譜與 Google ADK 多代理）

## 摘要

**一句話重點：** 約 65 分鐘的課程影片，介紹如何用 Google ADK 設計多代理系統，把結構化資料（CSV）與非結構化資料（Markdown）轉成知識圖譜；內容從知識圖譜概念與 Cypher，到多代理架構，再到用 ADK 建單一代理與多代理團隊的實作示範。

| 時間 | 重點 |
|---|---|
| 00:00 | 課程簡介：Neo4j 合作；ADK 多代理系統；講師為 Neo4j 的 Andreas Kollegger |
| 03:13 | 知識圖譜概念：從關聯式 join 對比圖；Cypher 樣式比對與「推薦沒買過的商品」範例；節點／關係／屬性 |
| 09:37 | 根因分析情境（家具製造商客訴）；目標資料模型：領域圖＋詞彙圖＋主題圖 |
| 13:41 | 代理與多代理系統：迴圈＋LLM＋工具；委派與「代理當工具」 |
| 16:31 | 要建的架構：結構化／非結構化／GraphRAG 三條流程；圖建構計畫與知識抽取計畫 |
| 23:17 | Lesson 3 Part I：用 ADK 建代理、定義工具、Runner 與事件迴圈、agent caller |
| 44:47 | Lesson 3 Part II：根代理＋子代理、委派、session state 與 tool context |
| 63:58 | 結語 |

### 名詞與縮寫
- **知識圖譜（knowledge graph）**：以節點與一等公民的關係表示資訊的資料庫，可同時結合圖樣式比對與向量相似度搜尋。
- **Cypher**：Neo4j 的圖查詢語言；`$` 開頭是查詢參數。
- **領域圖／詞彙圖／主題圖**：結構化資料建成的圖／文字塊及其結構／從文字抽出的實體與事實，並連回領域圖。
- **Google ADK（Agent Development Kit）**：建構代理的框架；**LiteLLM** 是讓 ADK 呼叫 OpenAI 的封裝。
- **root agent／sub-agent／delegate**：根代理、子代理、委派（對話控制權交給子代理）。
- **tool context／session state／output key**：工具取得與更新共享狀態的方式／跨代理共享的狀態字典／把代理最終回應存進狀態。
- **ABK**：講師名字縮寫（Andreas B. Kollegger），範例中的使用者名稱。

### 轉錄校正備註
- 語言為英文（`detected_language: en`，來源是 X 平台人工字幕、非 Whisper）；已附**重點式**中譯 `transcript.zh.md`：因課程影片很長，中譯是各段重點的摘譯，不是逐句翻譯；要查原話請看英文逐字稿。
- 字幕把 Neo4j 寫成 "new for j"、Cypher 寫成 "cipher"、LiteLLM 寫成 "light LLM"，講師姓氏拼成 "Colliger"（畫面為 Kollegger），已由 `glossary/domains/neo4j.json` 修正；其餘不確定處記在 `known_asr_errors`。
- **身分與出處**：X 貼文標題為「Ryan Carter - Andrew Ng just released a 1-hour course…」，上傳者顯示 Ryan Carter；影片本身有 DeepLearning.AI 與 Neo4j 標誌，字幕出現 Andrew 與 Andreas 的名字。「這是 Andrew Ng 的新課程」是貼文的說法，我沒有獨立查證，也沒有用外貌辨識人物。
- 影片中關於代理的優缺點（慢、貴、token 成本快速累積）與 GPT-4o 的使用皆為講者說法，**未經查證**。
- 截圖：自動抽圖會跳過變化小的 notebook 畫面，所以另在每個主題轉換點指定擷取 1024px 寬的截圖（31 張，`meta.json.cue_timestamps`），程式碼與投影片文字都可閱讀；報告切成 33 段、平均約 2 分鐘。個別截圖可能因畫面捲動而被切邊（例如 38:40）。

## 來源

- 原始資料夾：`watch-output/AI/2026-10-12_X_DeepLearning-AI-×-Neo4j-Agentic-Knowledg__2108904705854411211`
- 逐字稿來源：captions (en, manual, unknown)
