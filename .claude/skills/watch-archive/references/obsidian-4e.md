# 步驟 4e／5b：Obsidian 知識庫（連結 → 匯出）

> 歸檔結果除了 Word／Markdown 報告，也可匯成同一個 Obsidian vault（`obsidian-vault/`），讓每支影片變成一篇可互相連結的筆記。

## 原則：連結由人選，不靠相似度自動產生

只用語義相似度連出來的 link 看起來很相關、實際沒有關係（亂連只會混亂）。所以匯出腳本**不自動加連結**，只取自手寫的 `links.md`；每條都要寫明「關係」，且使用者確認後才算數。

## 4e 寫 `links.md`（選填，與 `summary.md` 同資料夾，重跑不覆蓋）

格式：每行一條，`[[概念]]` 後用全形「｜」寫關係（為什麼連、方向）。

```
# 連結
- [[知識管理]]｜上位概念：本篇討論的是個人知識管理方法
- [[原子習慣]]｜舉例：用同一本書示範不同背景連出不同網路
```

- 先看 `obsidian-vault/` 既有筆記名稱（`ls obsidian-vault/*/`），能連到既有筆記就用它的原名；新概念照寫（Obsidian 會顯示成「待建立節點」，之後再補）。
- 一篇約 3–7 條；寫不出關係的就不要連。
- 提問清單（挑相關的）：背後證據？牽涉哪些前提？跟人類行為／動機有什麼關係？可應用在哪些決策？在更大的脈絡代表什麼？哪裡不適用（反例與侷限）？
- 回覆使用者時列出所有 `links.md` 的連結，請使用者確認或刪改；`status: unreviewed` 在使用者確認前不要改。

## 5b 匯出

重建報告（步驟 5）之後：

```bash
python3 scripts/obsidian_export.py watch-output/<領域>/<資料夾>    # 單一資料夾
python3 scripts/obsidian_export.py --all                            # 全部重匯
```

產出（預設 `obsidian-vault/`，可用 `--vault <路徑>` 改指向使用者自己的 vault）：

| 檔案 | 內容 |
|---|---|
| `<領域>/<標題>.md` | 屬性（title／type／source／platform／video_id／category／date／status／aliases／tags／related）、摘要、思維導圖、`## 連結`（來自 `links.md`）、操作 SOP 連結、補充資料；圖文貼文另有「圖文原頁」 |
| `<領域>/<標題>_操作SOP.md` | 有 SOP 時，由 `kb/` 複製，圖片路徑改指向 `_attachments/` |
| `_attachments/<video_id>/` | `mindmap.png`、圖文貼文頁面圖、SOP 步驟圖（相對路徑） |
| `00-索引.md` | 依領域列出所有筆記的 `[[連結]]` |

- 重匯只覆蓋帶 `generated_by: watch-archive` 的檔案；使用者自己加的筆記與圖片不動，同名但不是我們產生的筆記也不覆蓋（改存 `<標題> (<id>)`）。標題改名時，舊的產生檔會被清掉。
- 逐字稿不匯入筆記（太長，留在報告裡）；筆記末尾「來源」節註明原始資料夾。
- 要開啟：Obsidian →「Open folder as vault」選 `obsidian-vault/`；`git pull` 後重開即可。

## 圖文貼文（輪播圖，非影片）

- **Threads／IG 輪播的完整圖頁在 `<貼文網址>/embed`**：主頁 HTML 只有 `og:image`（第 1 張）；`curl -A "Mozilla/5.0" <貼文網址>/embed` 的頁面含全部頁面圖（`cdninstagram.com` JPG，第一個 `t51.2885-19` 是頭像，要略過）。主頁的 `og:description` 是貼文本文。不要只看主頁就說缺頁（2026-10-27 教訓：曾因此誤報第 9–10 頁無法取得）。

使用者只給圖片時（例如 IG／Threads 輪播），照影片流程的檔案格式手動歸檔：

- `meta.json` 加 `"media_type": "carousel"`，`platform` 填 `Image`，`duration` 寫頁數（如 `8 頁（共 10 頁，第 9–10 頁未提供）`），`transcript_source` 寫「圖片文字（逐頁人工抄錄，非語音轉錄）」；`slides` 每頁一筆，`start` 用 `00:0N`（第 N 頁），`frame` 指向 `frames/slide_0N.jpg`（同時寫 `frames.json`）。
- `transcript.md` 每頁抄錄圖上文字（標題、副標、關鍵標籤、結語），每行 `[00:0N] 文字`；圖上筆誤照抄並在摘要註明；缺頁寫進 `supplement.md`，不推測內容。
- 報告會顯示「第 N 頁」而非時間範圍；其餘（`summary.md`、`mindmap.md`、`links.md`）與影片相同。
