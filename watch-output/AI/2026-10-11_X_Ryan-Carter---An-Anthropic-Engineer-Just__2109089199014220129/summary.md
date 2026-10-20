# 摘要：Claude Code workshop — Maximizing value from Claude Code

**一句話重點：** 一場約 26 分鐘的網路研討會，用「一個提示 = 很多個請求，每個請求都帶著整段對話」的心智模型，說明 Claude Code 的 token 花在哪、如何靠提示快取（prompt cache）與良好習慣降低成本，最後介紹管理者可用的團隊設定。

| 時間 | 重點 |
|---|---|
| 00:00 | 開場與議程；agentic 時代按「工作」付費，token 是單位，目標是建立心智模型 |
| 02:23 | 一個提示並非只有提示：系統提示、內建工具、CLAUDE.md、skills／MCP 名稱一併送出；模型以工具呼叫迴圈運作，每次來回上下文都變長 |
| 04:52 | 三種 token：輸入、輸出（含工具呼叫、編輯、思考）、快取 |
| 05:21 | 價格頁；輸入可平行處理故便宜，輸出逐 token 生成故最貴 |
| 06:16 | 提示快取：相同前綴以約 0.1 倍輸入價讀回；健康工作階段多數輸入來自快取（用 usage 檢查） |
| 07:32 | 選對模型：不要對不需要的任務用最大模型；小模型不等於差模型 |
| 08:56 | 給對上下文：用 @ 直接帶入檔案；用 context 檢視載入內容 |
| 10:09 | CLAUDE.md 只放每個任務都需要的；任務專屬流程改成 skill；用 /claude-api prompt-audit 清理過時指示 |
| 11:35 | 關閉閒置 MCP 或改用 CLI；留意低於門檻的大量指令輸出（改用安靜回報器、把常用指令寫進 CLAUDE.md、吵雜工作交給子代理） |
| 13:06 | effort：不必一直開最高；「不夠懂」是模型問題，「不夠努力」是 effort 問題 |
| 14:34 | 上下文只增不減：任務間 /clear、必要時 /compact、/rewind；先改名再 clear 可日後 resume |
| 15:51 | 快取從第一個 token 開始比對，一個 token 不同則其後全價 |
| 16:14 | /compact、/clear、中途換模型、（多數模型）換 effort 都會破壞快取；快取視窗約 1 小時（方案）或 5 分鐘（API／雲端），可設 TTL，但長視窗寫入較貴 |
| 18:36 | 四守則：開始時選好 model＋effort；中途換模型先 compact；離開前趁快取熱時 compact；隔天回來前先 compact，冷的 --resume 會全價重讀 |
| 19:53 | 子代理：在獨立上下文做吵雜研究，只回傳結論；自身仍耗 token，但主對話更精簡；可指定不同模型與 effort |
| 21:12 | 管理者：managed settings（起始模型／effort、快取 TTL、允許的 MCP、組織 CLAUDE.md）、分析與 OpenTelemetry 監控、用量點數與支出上限、達上限自動繼續 |
| 24:42 | 結語三原則：開始時選好設定後別動；刻意決定放進對話的內容；保持工作階段專注（clear／趁熱 compact） |

## 名詞與縮寫
- **token**：模型處理的最小計量單位；分輸入、輸出、快取三類。
- **提示快取／前綴（prompt cache／prefix）**：請求開頭與上次完全相同的部分可被重用，以低價讀回。
- **compact／clear／rewind／resume**：壓縮對話為摘要／清空／回退幾輪／接續舊工作階段。
- **sub-agent（子代理）**：有獨立上下文的代理，完成工作後只回傳結論。
- **managed settings**：管理後台定義、全團隊強制套用的設定檔。

## 轉錄校正備註
- 語言：英文（`detected_language: en`）；來源為 X 平台人工字幕（非 Whisper），已補完整中譯 `transcript.zh.md`。
- 字幕常把 Claude 寫成 "Cloud"（含 CloudMD），已由 `glossary/domains/claude-code.json` 與一次性修正處理；另修正 buyer→bar、retool→tool、ride→write、cash→cache 等，詳見 `known_asr_errors`。
- **講者身分**：X 貼文標題與上傳者為「Ryan Carter」，標題寫 “An Anthropic Engineer…”；但影片畫面名牌看起來是另一個名字（Lydia Hallie），講者自述為 Anthropic 團隊成員。這段身分資訊我無法獨立查證，請以原影片為準。
- 價格、倍率（0.1×／1.25×／2×）與「快取視窗約 1 小時／5 分鐘」皆為影片畫面或講者所述，反映錄影當時（畫面標示 2026 年 9 月）的情況，**未經查證，之後可能變動**（講者也提醒價格與功能會持續變動）。
- 約 21:12 起至結尾無對應投影片截圖。
