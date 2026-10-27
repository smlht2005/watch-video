---
title: "MiniMax H3 最開放模型！本地無限制，越獄解鎖更多玩法！想生成什麼就生成"
type: video-note
source: "https://drive.google.com/file/d/1EIhyh60imHgwatjkElA-8di38oYtiv0T/view?usp=drivesdk"
platform: "GoogleDrive"
video_id: "1EIhyh60imHgwatjkElA-8di38oYtiv0T"
uploader: "零度解說（YouTube 頻道）"
category: "AI"
date: "2026-10-12"
status: unreviewed
origin_folder: "watch-output/AI/2026-10-12_GoogleDrive_MiniMax-H3-最開放模型-本地無限制-越獄解鎖更多玩法-想生成什麼就生成__1EIhyh60imHgwatjkElA-8di38oYtiv0T"
generated_by: watch-archive
aliases:
  - "MiniMax H3 最開放模型！本地無限制，越獄解鎖更多玩法！想生成什麼就生成"
tags:
  - "watch-archive"
  - "AI"
  - "MiniMax-H3"
  - "ComfyUI"
  - "文生影片"
  - "圖生影片"
  - "本地部署"
  - "去審查模型"
  - "量化版"
  - "8GB-顯卡"
  - "AI-影片生成"
  - "零度解說"
---

# MiniMax H3 最開放模型！本地無限制，越獄解鎖更多玩法！想生成什麼就生成

## 摘要

- 來源：YouTube 頻道「零度解說」，原網址 https://youtu.be/NbL9xD2KV4E（2026-09-10 上傳，長度 09:17）。YouTube 擋雲端 IP，本次改從使用者上傳的 Google Drive 副本下載
- 逐字稿來源：Groq Whisper 轉錄（非平台字幕）；原音為簡體中文口語，已轉為繁體，並依畫面字幕校正 34 處
- 影片類型：本地部署教學兼推廣。以下為**講者的說法**，模型規格、檔案大小與效果均未經查證

### 一句話重點

講者示範在 Windows 上用 ComfyUI Desktop 本機執行 MiniMax H3 影片生成模型（文生影片、圖生影片），並介紹以第三方「越獄版」去審查文字編碼器替換官方版、移除內容限制；另稱 NF4 量化版最低 8GB 顯卡即可執行。

### 重點（含時間戳）

| 時間 | 重點 |
|---|---|
| 00:00–01:14 | 開場：播放多段寫實短片，請觀眾猜哪些是 AI 生成；講者稱只確定第三、四段是真人拍攝 |
| 01:15–02:30 | 依講者部落格教學，安裝開源的 ComfyUI Desktop，從模型下載中心取得官方的文生影片、圖生影片、參考生成影片模型；講者稱另有限制較少的「越獄版」 |
| 02:31–03:49 | 文生影片實測：以李白〈早發白帝城〉當提示詞，數分鐘生成山水動畫；講者稱低解析度效果已不錯 |
| 03:50–04:52 | 圖生影片實測：上傳圖片、長度 15 秒；畫素倍數 0.4 約 864×480，最高 1080p。建議先用低解析度縮短時間，再用免費放大工具提升畫質；講者稱畫面與音效一次生成，15 秒影片數分鐘完成 |
| 04:53–05:30 | 「越獄版」模型：畫面顯示為 Qwen3-VL 32B 的 uncensored／heretic 文字編碼器，有 BF16 完整版（講者稱 50 多 GB）與量化版（講者稱 26.4GB）；講者暗示可生成成人內容但不便明說 |
| 05:31–07:40 | 安裝方式：下載工作流節點 ZIP 放入 ComfyUI Desktop 的自訂節點資料夾，模型檔放入 models 的文字編碼器資料夾，重新啟動後載入越獄版工作流 |
| 07:41–08:01 | 低顯存：ModelScope 貼文稱 MiniMax-H3 的 4-bit 量化版搭配 DiffSynth-Studio，最低 8GB VRAM 可跑；講者稱不同量化版在一般任務下差異不大 |
| 08:02–08:49 | 作品展示：角色一致性影片、網友以 RTX 3060 生成的影片、動態 MV、餃子廣告；講者主張可作為主力工具，能做電影級畫質與商業廣告 |
| 08:50–09:17 | 結尾：資料與連結放在影片說明欄 |

### 名詞與縮寫說明

| 名詞 | 意思 |
|---|---|
| MiniMax H3 | 講者所稱 MiniMax 公司的開源影片生成模型（版本與開源狀態未查證） |
| ComfyUI／ComfyUI Desktop | 開源的節點式 AI 圖像、影片生成工具；Desktop 為桌面安裝版 |
| 文生影片（T2V） | 用文字提示詞生成影片 |
| 圖生影片（I2V） | 用一張圖片加提示詞生成影片 |
| 工作流（workflow） | ComfyUI 中串接各節點的處理流程檔 |
| 自訂節點（custom nodes） | 第三方擴充的 ComfyUI 功能節點 |
| 文字編碼器（text encoder） | 把提示詞轉成模型能理解向量的模型元件，本片用 Qwen3-VL 32B |
| 越獄版／uncensored／heretic | 第三方移除安全限制的修改版模型，非官方釋出 |
| BF16 | 16 位元浮點精度，品質高但檔案大、需要大顯存 |
| 量化版／NF4／INT8 | 降低數值精度以縮小檔案與顯存需求；NF4 為 4 位元 |
| VRAM（顯存） | 顯示卡記憶體，決定能跑多大的模型 |
| DiffSynth-Studio | ModelScope 的開源擴散模型推論框架 |
| ModelScope（魔搭） | 阿里巴巴的模型分享平台 |
| LoRA | 低成本微調模型的方法 |
| ASR | Automatic Speech Recognition，自動語音辨識 |

### 注意事項

- 「越獄版」去審查模型是第三方修改版，生成內容需自行遵守當地法規與平台政策；用真人肖像生成影片涉及肖像權與深偽（deepfake）風險。
- 影片中的模型與工作流來自講者部落格與第三方 GitHub 等非官方來源，數十 GB 的檔案下載前應確認來源與雜湊值。
- 檔案大小講者說法與畫面文字不完全一致（講者說 50 多 GB 與 26.4GB，畫面約為 47.97G 與 24.55G，低解析度辨識），以實際下載頁為準。

### 轉錄校正備註

- 主要誤聽：「ComfyUI」被聽成 Configure Code、config、convi以外、空隙以外；「越獄版」被聽成越域版、域域版、粵語版；「文生影片」被聽成紋身影片；「零度博客」被聽成聯絡博上、零度博物館；〈早發白帝城〉整首詩聽錯，已依原詩校正。
- 共 34 處校正記在 `meta.json.known_asr_errors`，標「推測」者依上下文推斷；穩定錯誤已寫入新詞典 `glossary/domains/ai-video.json`。
- 未確定、保留原文：01:37「TDM Fuzz 多執行緒下載器」、04:44「影片傳傳」、07:55「到聲音在3G下載」。

## 來源

- 原始資料夾：`watch-output/AI/2026-10-12_GoogleDrive_MiniMax-H3-最開放模型-本地無限制-越獄解鎖更多玩法-想生成什麼就生成__1EIhyh60imHgwatjkElA-8di38oYtiv0T`
- 逐字稿來源：whisper (groq)
