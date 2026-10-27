# watch-video

把影片歸檔成圖文報告時，校稿階段用來確認逐字稿修正的用語。

## Language

**推測詞**:
`known_asr_errors` 裡 `status` 為 `suspected` 的校正項：逐字稿已改成目前的寫法，但還沒有人聽音或看原畫面確認。
_Avoid_: 存疑詞（那是逐字稿中標為存疑的行，是另一回事）、待查詞

**待確認音檔**:
為推測詞剪出的音檔與截圖，放在影片資料夾的 `waitConfirm/`，附 `index.md` 讓人點連結重聽；只存本機，不入庫。
_Avoid_: 試聽檔、clip

**使用者聽音確認**:
使用者聽過待確認音檔（或看過畫面）後定案的推測詞，`status` 為 `confirmed`。
_Avoid_: 已驗證、已查證（影片中的數字與主張另有「講者主張，未查證」的標法）

## Obsidian 知識庫（學習重點，出處：王啟樺 Threads 圖文〈AI 時代為什麼 Obsidian 反而更重要？〉，作者主張，未查證）

**知識庫筆記**:
由 `scripts/obsidian_export.py` 從歸檔資料夾匯出的 Obsidian 筆記，位於 `obsidian-vault/<領域>/`，屬性帶 `generated_by: watch-archive`。
_Avoid_: 報告（那是 `*_report.docx／.md`，含逐字稿與逐段截圖）

**人選連結**:
只取自手寫 `links.md`、每條寫明關係、經使用者確認的 `[[ ]]` 連結。核心主張：link 是在定義關係，不是排版；AI 只依語義相似度連出的連結不算數。
_Avoid_: 自動連結、相關連結（用 `keywords` 或相似度自動產生的不屬於本詞）

**待建立節點**:
先寫下 `[[概念]]` 但尚未撰寫的筆記，用來保留思考入口；`links.md` 允許指向還不存在的筆記。

**圖文貼文**:
只有圖片、沒有影片的輪播貼文（`meta.json.media_type: "carousel"`）；以頁碼代替時間碼，文字由人工逐頁抄錄，不是語音轉錄。
_Avoid_: 影片、投影片（報告內部沿用 `slides` 欄位，但對使用者稱「頁」）
