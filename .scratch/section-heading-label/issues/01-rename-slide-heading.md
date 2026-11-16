Status: ready-for-agent

# 01 程式：段落標題預設「主題 N」，支援 meta.section_label

Spec：`.scratch/section-heading-label/spec.md`

## 要做
- `scripts/build_report.py` `slide_blocks`：carousel →「第 N 頁」；`meta.section_label` 有值 → 用它；否則「主題」。
- 確認 `watch_archive.py` 重跑時保留 `section_label`（加進保留欄位）。
- 測試：更新既有「投影片 N」斷言；新增 section_label、carousel、無 slides、知識點錨點案例。
- 文件：`content.md` 4a 補 `section_label` 用法。

## 驗收
- 全套測試通過。

## Comments

- 2026-11-16 grill 結論：預設「主題」（使用者提議），真投影片影片以 `section_label: "投影片"` 保留，圖文貼文維持「第 N 頁」，保留編號。
