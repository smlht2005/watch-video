# 05: 重匯整個 vault 並同步 Obsidian 文件

**What to build:** 依 02、03 的新筆記格式，更新 Obsidian 相關文件，並以 `--all` 重匯整個 `obsidian-vault/`，讓既有筆記一次統一。

**Blocked by:** 02、03

**Status:** ready-for-agent

- [ ] `obsidian-4e.md` 的筆記內容表、原則（逐字稿放在圖文對照、不另開檔）、移除 `--with-pages` 說明已更新；`CLAUDE.md` 的 Obsidian 規則同步
- [ ] `obsidian_export.py --all` 重匯完成，無錯誤；匯出警告列給使用者
- [ ] 抽查：`_attachments/` 不再有 `mindmap.png`；使用者手寫的筆記與圖片未被改動（git diff 只動 `generated_by: watch-archive` 的檔案與 `_attachments/`）
- [ ] 抽查兩篇（一支 slides 影片、一支圖文貼文）在 Obsidian 格式下截圖與條列正常
- [ ] commit 並在 PR 描述說明大量 vault diff 的原因

## Comments
