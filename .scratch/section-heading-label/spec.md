Status: ready-for-agent

# 段落標題：預設「主題 N」，真投影片才用「投影片 N」

## Problem Statement

報告（md／docx）與 Obsidian 影片筆記的每段標題一律是「投影片 N：標題（時間）」。但大部分影片是訪談、實拍、講座、步驟示範，畫面根本沒有投影片，讀起來不自然（例：財經一路發「投影片 9：買進第一步」）。

## Solution

- 預設段落標題改成 **「主題 N：標題（開始–結束）」**。
- 一段對一張投影片的簡報／投影片錄影，在 `meta.json` 寫 `"section_label": "投影片"`，標題維持「投影片 N」。
- 圖文貼文（`media_type: carousel`）維持「第 N 頁」；沒有 `slides` 時的「畫面 MM:SS–…」不變。
- 改完重建所有報告（md，已有 docx 的一併更新）並 `obsidian_export.py --all`；知識點的段落連結由 `section_anchors()` 從實際標題取得，會自動跟著改。

## User Stories

1. 看訪談、講座的報告時，段落叫「主題 N」，不會誤以為有投影片。
2. 看簡報錄影時，段落仍叫「投影片 N」，對得上畫面。
3. 從知識點點出處，仍跳到正確段落。

## Implementation Decisions

- `build_report.slide_blocks`：標籤 = `第 N 頁`（carousel）／`meta.section_label`（有值時）／`主題`（預設）。`section_label` 只接受非空字串；不限白名單（例：「章節」也可）。
- 編號保留：段落標題可能重複，編號讓錨點唯一。
- `section_label` 重跑 `watch_archive.py` 會保留（與 `slides` 同樣是手寫欄位；確認 `watch_archive.py` 的保留清單）。
- 哪些既有影片要設 `section_label: "投影片"`：Claude 看各影片截圖提出清單（畫面以全螢幕投影片為主、一段對一張投影片者），使用者確認後才寫入。
- 文件：`content.md` 4a 補一句 `section_label` 的用法；`GLOSSARY.md` 若有「投影片」定義一併調整。
- 風險：使用者手寫、連到「#投影片 N…」的 Obsidian 連結會斷；匯出產生的連結不受影響。

## Testing Decisions

- `test_watch_archive.py`、`test_obsidian_export.py` 既有斷言改成「主題 N」。
- 新增：`section_label: "投影片"` → 「投影片 N」；carousel 仍「第 N 頁」；無 slides 仍「畫面」；知識點連結錨點跟著標籤變。
- PR 前跑全套測試。

## Out of Scope

- 段落切法、`slides` 內容本身不改。
