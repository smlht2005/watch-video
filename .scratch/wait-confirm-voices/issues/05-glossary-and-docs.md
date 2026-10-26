# 05：GLOSSARY.md 與流程文件更新

**What to build:** 下次歸檔佛學／講經影片時，流程與文件都會提醒執行 `--wait-confirm`，並說明確認後怎麼改成 `confirmed`；專有用語有統一定義。

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] 新建根目錄 `GLOSSARY.md`，定義三個詞：**推測詞**、**待確認音檔**、**使用者聽音確認**；只寫定義，不寫實作細節
- [ ] 更新 `watch-archive` skill 與 references（`proofread.md`、`deliver.md`）：校稿寫完 `known_asr_errors` 後加一步執行 `--wait-confirm`
- [ ] 文件說明 `status` 欄位寫法，以及使用者聽音後由 Claude 改成 `confirmed`、在 `expected` 加「使用者聽音確認」並重建報告
- [ ] `CLAUDE.md` 硬規則加一條；`README.md`、`references/notes.md` 文字版同步
- [ ] 更新 `docs/watch-archive-flow.png` 流程圖
- [ ] 不寫 ADR（無難以回頭的取捨）

## Comments
