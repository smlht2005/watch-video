# 03：下載失敗的清楚錯誤訊息

**What to build:** 影片不在本機、需要用 yt-dlp 下載時段，若 YouTube 擋下載或要求登入，使用者看到清楚的原因與下一步（Windows 只能用 Firefox cookies），而不是一串堆疊追蹤。一筆失敗不影響其他項目。

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] 下載被擋（429／要求登入）時印出原因與處理建議，Windows 提示使用 Firefox cookies
- [ ] 失敗的項目在終端機列出並跳過，其餘項目照常產生
- [ ] `index.md` 不為失敗的項目放無效的重聽連結
- [ ] 測試用替身模擬下載失敗，驗證訊息與其他項目不受影響

## Comments
