Status: ready-for-agent
Blocked by: 01

# 02 標記既有投影片影片並重建全部報告與 vault

Spec：`.scratch/section-heading-label/spec.md`

## 要做
- 看各影片截圖，列出「一段對一張全螢幕投影片」的影片（候選：DeepLearning.AI × Neo4j、Anthropic Prompting 101、新模型提示詞 7 個改法、AI 逐字稿驗收課、淨土安心法門系列…），給使用者確認。
- 確認後在那些 `meta.json` 寫 `"section_label": "投影片"`。
- 重建所有報告（`build_report.py`，已有 docx 者一併更新），`obsidian_export.py --all`。
- 抽查：一支訪談（主題 N）、一支投影片（投影片 N）、一篇知識點連結可跳轉。

## 驗收
- 使用者確認清單；全部重建無錯誤、匯出無新警告。

## Comments
