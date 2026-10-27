---
title: "免費製作 AI 影片：ComfyUI 接上 Claude（MCP）"
type: video-note
source: "https://youtu.be/fAWliYuOiuc"
platform: "YouTube"
video_id: "fAWliYuOiuc"
uploader: "PAPAYA 電腦教室"
category: "AI"
date: "2026-10-13"
status: unreviewed
generated_by: watch-archive
aliases:
  - "免費製作 AI 影片：ComfyUI 接上 Claude（MCP）"
tags:
  - "watch-archive"
  - "AI"
  - "ComfyUI"
  - "Comfy-Cloud"
  - "MCP"
  - "Claude"
  - "Z-Image-Turbo"
  - "ACE-Step"
  - "MiniMax-H3"
  - "GPT-Image-2"
  - "工作流程"
  - "節點"
related:
  - "[[免費製作 AI 影片：ComfyUI 接上 Claude（MCP）_操作SOP]]"
---

# 免費製作 AI 影片：ComfyUI 接上 Claude（MCP）

## 摘要

**一句話重點：** PAPAYA 電腦教室示範在 Mac 上安裝 ComfyUI 桌面版，用內建範本免費在本機生成圖片（Z-Image Turbo）與音樂（ACE-Step），以 Comfy Cloud 點數跑 MiniMax H3 圖生影片，再透過 Comfy MCP 讓 Claude 代為執行、改造工作流程與規劃動畫分鏡。

### 重點時間表

| 時間 | 重點 |
|---|---|
| 00:00 | ComfyUI 以節點流程生成影像；講者主張內建範本加上 AI 助理可大幅降低學習門檻 |
| 00:37 | 官網下載安裝桌面版，選「本地」執行（雲端 GPU 需訂閱付費） |
| 01:34 | 主介面與內建範本：皇冠代表只能雲端執行，可篩選只看本機範本 |
| 02:42 | 基本操作：拖曳節點、子工作流程、滾輪縮放、空白鍵平移、句號鍵聚焦 |
| 03:54 | 側邊欄一鍵下載缺少的模型，Ctrl／Command-R 重新整理；模型存放位置看說明卡片 |
| 05:02 | Z-Image 生成 1280×720 圖片；作品存在 Output 資料夾、資產面板；Ctrl／Command+S 儲存工作流程 |
| 06:31 | ACE-Step 文字生成音樂：曲風、歌詞、速度、調性、長度 |
| 08:07 | MiniMax H3 圖生影片：硬體需求高，改用 Comfy Cloud（註冊、儲值點數） |
| 09:31 | 以泡茶圖為初始影格，設定提示詞、解析度、長度（最長 15 秒，越長越耗點數） |
| 10:45 | ComfyUI 支援 MCP；安裝 Comfy MCP 到 Claude（指定 ComfyUI 資料夾、信任工作區） |
| 11:56 | 請 Claude 用現有工作流程生成中文歌，Claude 先確認主唱、歌詞等細節 |
| 13:06 | 請 Claude 改用 GPT Image 2、一次生成三種風格的警察企鵝；改好的流程可直接換主題 |
| 14:12 | 請 Claude 把柴犬廚師故事拆成分鏡，生成一段動畫 |

### 名詞與縮寫
- **ComfyUI**：以節點（node）組成工作流程的開源影像／影音生成工具，有桌面版。
- **Comfy Cloud**：Comfy 官方雲端算圖服務，採點數制，可執行不開源或硬體需求高的模型（範本上有皇冠圖示）。
- **MCP（Model Context Protocol）**：讓 AI 助理呼叫外部工具的協定；**Comfy MCP** 讓 Claude、ChatGPT 等直接操作 ComfyUI。
- **Z-Image Turbo**：本機文生圖模型範本。**ACE-Step**：文字生成音樂模型。**MiniMax H3**：影片生成模型（圖生／文生／參考生影片）。**GPT Image 2**：OpenAI 影像模型，在此透過 Comfy 點數使用。

### 備註（講者主張，未查證）
- ACE-Step 支援 50 種以上語言、MiniMax H3 主要針對 NVIDIA 顯示卡、雲端影片最長 15 秒、示範儲值 10 美元等數字與說法，均為講者主張，未查證；版本與價格可能已變動。
- 「免費」指本機執行開源模型；雲端範本（MiniMax H3 圖生影片、GPT Image 2）需要付費點數。
- 畫面中 ComfyUI 為 v0.34.3、PyTorch 2.12.1，Claude 桌面版顯示 Opus 5（錄製時狀態）。

### 轉錄校正備註
- 逐字稿來源：Groq Whisper（自動偵測為中文）。ComfyUI 被聽成 KonfiUI、confyUI 等多種寫法，已新增至 `glossary/domains/ai-video.json`；Claude 被聽成「Cloud」只在本支修正。
- OpenCC 台灣用語把「參數」「類型」轉成「引數」「型別」，已改回。
- 07:39–07:56、12:46–13:06、14:41–14:55 為示範音樂與動畫播放，無旁白。
- 其餘推測性校正記在 `meta.json.known_asr_errors`。

## 操作 SOP

- [[免費製作 AI 影片：ComfyUI 接上 Claude（MCP）_操作SOP]]

## 來源

- 原始資料夾：`watch-output/AI/2026-10-13_YouTube_免費製作-AI-影片-ComfyUI-接上-Claude-MCP__fAWliYuOiuc`
- 逐字稿來源：whisper (groq)
