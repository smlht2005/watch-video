# Spec：Obsidian 影片筆記改為「思維導圖＋圖文對照」，docx 改為選用

Status: ready-for-agent

## Problem Statement

使用者在 Obsidian 讀影片筆記時，「摘要」與「思維導圖」講的是同一件事、內容重複；思維導圖又是一張 PNG，在 Obsidian 裡無法搜尋、無法複製文字。真正想在筆記裡看到的「每段截圖＋說明＋逐字稿」（報告的〈圖文對照〉）反而只在報告檔裡，vault 筆記沒有。

另外，每次歸檔或重建報告都會產出 Word 檔（`*_report.docx`、教學影片另有 `*_操作SOP.docx`）。使用者平常只看 Markdown 與 Obsidian，docx 只是偶爾要給別人時才需要；每次都產出會拖慢重建、讓 repo 多出大型二進位檔、並在 Word 開著時造成 `PermissionError`。

## Solution

1. **影片筆記（Video note）的內容改成**：屬性 → 思維導圖（文字版，直接嵌入 `mindmap.md` 的縮排條列）→ 圖文對照（每段截圖、標題、說明、該段逐字稿；外語影片含中譯）→ 知識點、連結、操作 SOP、補充資料（照舊）。原本的「摘要」區塊與思維導圖 PNG 從筆記移除；`_attachments/<video_id>/mindmap.png` 不再產生，重匯時清掉。`summary.md` 本身不變，仍出現在報告 md／docx。
2. **docx 改成選用**：`build_report.py` 與 `watch_archive.py` 預設只產 `*_report.md`（與 SOP 的 md、`kb/`）；加 `--docx` 才同時產出 `*_report.docx` 與 `*_操作SOP.docx`。沒加 `--docx` 重建時，資料夾裡舊的 docx 會被刪除，避免與 md 不同步。
3. 改完後以 `--all` 重匯整個 `obsidian-vault/`，讓既有筆記一次統一成新格式。

## User Stories

1. As a 使用者, I want 影片筆記開頭就是思維導圖的文字條列, so that 我在 Obsidian 不用開圖就能掃過整支影片的結構。
2. As a 使用者, I want 思維導圖是文字而非 PNG, so that Obsidian 全文搜尋找得到導圖裡的關鍵字。
3. As a 使用者, I want 筆記不再同時出現「摘要」與「思維導圖」, so that 我不會讀到兩份重複的內容。
4. As a 使用者, I want 筆記有「圖文對照」, so that 我在 Obsidian 裡就能逐段看截圖、說明與逐字稿，不必另開報告檔。
5. As a 使用者, I want 圖文對照的每段帶時間範圍與段落標題, so that 我能回到影片對應的時間點。
6. As a 使用者, I want 圖文對照的截圖存在 `_attachments/<video_id>/` 並用相對路徑, so that 整個 vault 搬到別台電腦仍看得到圖。
7. As a 使用者, I want 截圖在 vault 裡縮到 1024 px 以內, so that repo 與 vault 不會因為大量截圖暴增。
8. As a 使用者, I want 外語影片的圖文對照也帶中譯, so that 筆記和報告一樣好讀。
9. As a 使用者, I want 自動產生的思維導圖（第一行 `<!-- auto … -->`）在筆記裡不顯示那行註解, so that 筆記乾淨。
10. As a 使用者, I want 沒有 `mindmap.md` 也沒有 `slides` 的舊資料夾仍能匯出筆記（省略思維導圖區塊，不報錯）, so that `--all` 重匯不會中斷。
11. As a 使用者, I want 沒有 `slides` 的舊資料夾圖文對照退回逐畫面方式（與報告相同）, so that 舊影片也有圖文對照。
12. As a 使用者, I want 重匯後 `_attachments/` 裡舊的 `mindmap.png` 自動消失, so that vault 不留過期檔。
13. As a 使用者, I want 重匯時我自己寫的筆記與圖片都不被動到, so that 我的手寫內容安全（沿用 `generated_by: watch-archive` 的擁有權規則）。
14. As a 使用者, I want 圖文貼文（carousel）的圖文對照顯示「第 N 頁」截圖與抄錄文字, so that 圖文貼文也有一致的筆記格式。
15. As a 使用者, I want 圖文貼文不再另有「圖文原頁」區塊（`--with-pages`）, so that 頁面圖不會在同一篇筆記出現兩次。
16. As a 使用者, I want 知識點原子筆記、連結、SOP 筆記、索引的行為完全不變, so that 這次改動只影響影片筆記本文。
17. As a 使用者, I want 歸檔與重建預設只產 Markdown, so that 重建更快，也不會因 Word 開著而失敗。
18. As a 使用者, I want 加 `--docx` 就同時產出報告與 SOP 的 Word 檔, so that 要給別人時一個旗標就搞定。
19. As a 使用者, I want `watch_archive.py --docx` 把旗標傳給重建報告, so that 歸檔時一次產出 Word。
20. As a 使用者, I want 不加 `--docx` 重建時刪掉舊 docx, so that 資料夾裡不會留下與 md 不同步的 Word 檔。
21. As a 使用者, I want `kb/` 與 SOP 的 md 不受 `--docx` 影響, so that Obsidian／Notion 仍拿得到 SOP。
22. As a 使用者, I want `review_links.py` 在沒有 docx 時只列 md 連結、不報錯, so that 交付確認流程照常。
23. As a 維護者, I want `CLAUDE.md`、`deliver.md`、`obsidian-4e.md` 的說法與新行為一致（交付前檢查改看 md／思維導圖，要版面才加 `--docx` 轉 PDF；SendUserFile 只在有 docx 時傳；逐字稿放在圖文對照）, so that 下次 session 不會照舊規則做事。
24. As a 維護者, I want 這兩項改動各自有測試, so that 之後重構不會悄悄改回去。
25. As a 使用者, I want 實作後用 `--all` 重匯整個 vault 並 commit, so that 既有約 40 篇筆記一次統一。

## Implementation Decisions

- **兩張 ticket，分開實作、各自可交付**：①影片筆記改版（匯出器）②docx 選用（報告建置與歸檔 CLI＋文件）。兩者沒有相依，順序不限；`--all` 重匯放在 ① 的最後。
- **匯出器（`obsidian_export`）**：
  - 影片筆記本文順序：標題 → `## 思維導圖`（文字）→ `## 圖文對照（畫面 + 逐字稿[＋中譯]）` → 知識點 → 連結 → 操作 SOP → 補充資料。移除 `## 摘要`。
  - 思維導圖文字來源是資料夾的 `mindmap.md`，嵌入時去掉第一行 auto 註解與檔內一級標題；沒有 `mindmap.md` 就省略此區塊。報告建置會在沒有手寫檔時依 `slides` 自動產生 `mindmap.md`，所以重建過的資料夾都有。
  - 不再把 `mindmap.png` 複製到 `_attachments/`；既有的 per-video 附件資料夾本來每次重建，舊 PNG 自然消失。
  - 圖文對照的段落內容**重用報告建置的段落產生邏輯**（slides 分段／無 slides 時逐畫面、逐字稿切段、中譯對齊、carousel 的「第 N 頁」），不在匯出器另寫一份；匯出器只負責把段落裡的圖片改成 `_attachments/<video_id>/` 的相對路徑並以 1024 px 縮圖複製（沿用知識點出處圖的縮圖做法）。標題層級降一級以配合筆記結構。
  - 這需要報告建置模組提供一個「產生圖文對照段落（含圖片相對路徑清單）」的公開函式，讓報告與匯出器共用。這是本 spec 唯一新增的介面。
  - `--with-pages` 與「圖文原頁」區塊移除；旗標保留為無作用並印一次 WARNING（避免舊指令報錯），文件同步刪除。
  - 筆記屬性（YAML）、擁有權判斷、知識點、連結、SOP、索引、manifest 行為不變。
- **報告建置（`build_report`）**：
  - `build(dest, docx=False)`：預設只寫 `*_report.md`、SOP 的 md 與 `kb/`；`docx=True` 才寫 `*_report.docx` 與 `*_操作SOP.docx`。
  - 不論旗標，重建時照舊清掉舊的 `*_report.*`／SOP 輸出，所以不加 `--docx` 時舊 docx 會被刪掉（已 commit 的舊檔只在該資料夾被重建時才處理，不主動全庫清理）。
  - CLI 加 `--docx`。
- **歸檔（`watch_archive`）**：CLI 加 `--docx`，不記進 `meta.json`（每次執行自己決定，不沿用），轉傳給報告建置；結尾提示文字同步。
- **`review_links`**：已是依檔案存在與否列出，不必改行為；確認沒有 docx 時輸出正常。
- **文件**：`CLAUDE.md`（交付前檢查、Obsidian 規則中「逐字稿不進筆記」）、`deliver.md`（步驟 5 檢查、步驟 6 SendUserFile 改為有 `--docx` 時才傳）、`obsidian-4e.md`（筆記內容表、原則、移除 `--with-pages`）、`archive.md`／`params.md`（產出清單與旗標）、`README.md` 產出說明。
- **Domain 用語**：沿用 `GLOSSARY.md` 的「影片筆記」「知識點」「圖文對照」「思維導圖」。

## Testing Decisions

- 好的測試只看外部行為：給一個暫存的歸檔資料夾，呼叫匯出／建置的公開進入點，檢查產出的檔案與內容；不測內部函式的切法。
- **Seam ①：匯出器的單一資料夾匯出進入點**（現有 `tests/test_obsidian_export.py` 的 Fixture 已建暫存 vault 與資料夾，沿用）。新增／修改的測試：
  - 筆記有 `## 思維導圖` 且內容是 `mindmap.md` 的條列（auto 註解不出現）、沒有 `## 摘要`、沒有 `mindmap.png` 圖片連結，`_attachments/<vid>/` 沒有 `mindmap.png`。
  - 筆記有 `## 圖文對照`，每段截圖指向 `_attachments/<vid>/` 的相對路徑且檔案存在、寬度 ≤ 1024；段落含該段逐字稿。
  - 沒有 `mindmap.md` 時省略思維導圖區塊不報錯；沒有 slides 時仍有圖文對照（逐畫面）。
  - carousel 筆記的圖文對照用「第 N 頁」，且沒有「圖文原頁」區塊；`--with-pages` 只印 WARNING。
  - 既有測試中檢查「摘要」或 carousel 頁面旗標的斷言改寫為新行為；擁有權、索引、知識點測試不變且仍通過。
- **Seam ②：報告建置的 `build(dest, docx=…)`**（prior art：`tests/test_watch_archive.py` 中檢查 SOP docx 產出的測試）：
  - 預設只產 md，沒有任何 `.docx`；`docx=True` 時報告與 SOP 的 docx 都在。
  - 先以 `docx=True` 建再以預設重建，舊 docx 消失。
  - `watch_archive` 的 CLI 解析接受 `--docx` 並傳到建置（以 CLI 參數解析層測，不跑下載）。
- 全套測試在開 PR 前跑（使用者慣例）。

## Out of Scope

- 不刪除或改動 `summary.md` 的產生與內容，報告 md／docx 仍有〈摘要〉。
- 不改知識點原子筆記、`links.md`／`knowledge.md` 的格式與匯出規則。
- 不主動清理 repo 裡已 commit 的舊 docx（只有重建到的資料夾才會變）。
- 不改 vault 筆記檔名 60 字上限（另議）。
- 不改報告 md 本身的章節內容與順序。

## Further Notes

- 來源：2026-11-16 與使用者的 grilling（Q1–Q8）。使用者決定：摘要與思維導圖重複，筆記只留文字版思維導圖並移除 PNG；其餘依建議（含逐字稿、`--all` 重匯、1024 px、`--docx` 含 SOP、無旗標刪舊 docx、文件同步、另開分支兩張 ticket）。
- carousel 的「圖文原頁」併入圖文對照是依建議推定，使用者未明確反對；實作前若有異議再調整。
- `--all` 重匯會讓 `obsidian-vault/` 出現大量 diff 與 `_attachments/` 新截圖，PR 描述要說明。
- 分支：`claude/vault-gallery-docx-flag`（自 main 開出，與歸檔分支 `claude/archive-LrvC2KNcxYs` 無關）。
