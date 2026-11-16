Status: resolved

# 01 匯出程式：出處連到段落＋自動前後文

Spec：`.scratch/knowledge-context/spec.md`

## 要做
- `scripts/obsidian_export.py` 知識點筆記：
  - `> — 10:37` → `> — [[<影片筆記>#<段落標題>|10:37]]`；YouTube 再加 ` ・ [▶ 原影片 10:37](<url>&t=637s)`。
  - 引文下方加 `> [!quote]- 前後文（起–迄）` callout（±30 秒、最多 12 行、引文行加粗；外語有中譯用中譯；圖文貼文用該頁全文）。
  - 段落標題由產生影片筆記標題的同一個函式取得。
- 底部「## 出處」的 `[[影片筆記]]（10:37）` 也改成段落連結。
- `tests/test_obsidian_export.py` 補 spec「Testing Decisions」列的案例。
- `python3 scripts/obsidian_export.py --all` 重匯，抽看 3 篇（中文影片、外語影片若有、圖文貼文若有）在 Obsidian 的顯示。

## 驗收
- 全套測試通過。
- 點 `10:37` 跳到影片筆記正確段落；前後文預設收起、展開後引文行加粗。
- 非 YouTube 沒有外部時間連結。

## Comments

- 2026-11-16 完成：出處改連段落（錨點取自 gallery() 實際標題）、YouTube 加 t= 連結、前後文 callout（±30 秒、上限 12 行、引文行加粗；中譯優先；圖文貼文取整頁；引文只在 supplement 時不放）。新增 8 個測試，全套 334 通過；--all 重匯。
