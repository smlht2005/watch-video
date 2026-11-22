# 摘要：上週我讓 AI 連續跑了整整 27 個小時不間斷（/goal 與 Rubric）

**一句話重點**：講者主張，/goal 這類「長時間自動執行」功能的成敗不在提示詞技巧，而在你能否把「做得好」定義成可驗證的評分標準（Evaluation／Rubric）；並分享六步驟 SOP，把個人品味拆成 AI 評審可執行的準則。（影片中的數字與主張皆為講者主張，未查證。）

| 時間 | 重點 |
|---|---|
| 00:00 | 開場：講者稱讓 AI agent 連跑 27 小時；真正的自動化是解放注意力 |
| 01:44 | Claude Code、Codex、Hermes Agent 同時推出 /goal：寫下目標，AI 做到完成為止 |
| 02:14 | AI 偷懶的原因：Context Anxiety（轉述 Anthropic 研究） |
| 03:07 | /goal 原理：實作者＋評審雙角色循環；前身為 Ralph Loop |
| 04:33 | 好 goal 提示詞的 5 要素：Outcome、Verification、Constraints、Iteration policy、Error handling |
| 06:21 | 難題：白領／主觀工作沒有單元測試 |
| 06:51 | Anthropic 網頁設計實驗：把「漂亮」拆成 4 維度、加重弱項權重、評審看真實畫面 |
| 09:44 | 共同指向 Evaluation，而非 Prompt／Context Engineering |
| 10:28 | 六步驟 SOP：先跑 baseline → 寫下皺眉理由 → 分類成維度 → 寫具體案例 → 多樣化案例 → 交給評審實跑 |
| 15:07 | 兩個提示詞（Rubric Builder、Goal Prompt Builder）在影片資訊欄，影片未呈現全文 |

## 名詞與縮寫
- **/goal**：在對話框輸入目標，agent 持續執行直到達成的功能。逐字稿原本辨識為「Go」，依投影片改為 /goal。
- **Context Anxiety**：講者轉述 Anthropic 研究，LLM 感到 context window 快滿時會急著收尾。
- **Rubric**：評分標準，供評審 agent 逐維度打分。
- **Baseline**：未加任何指引時 AI 的基準產出。

## 轉錄校正備註
- 逐字稿來源為 Groq Whisper；「Cloud」統一改為 Claude、「Go」依投影片改為 /goal、「Playwright」「Anthropic」等依畫面校正。
- 標「推測」的校正見 `meta.json.known_asr_errors`（如「大災問→大學問」「月籤→躍遷」）。
