# 摘要：Anthropic Prompting 101：用車禍報告範例逐步打造提示詞

**一句話重點**：Anthropic Applied AI 團隊的 Hannah 與 Christian 以「瑞典車險車禍報告表＋手繪草圖」為例，在 console 從極簡提示詞（Claude 誤判成滑雪事故）一路迭代到五版，示範十個提示詞要點，最後得到格式嚴謹、有信心的判定輸出。

> 注意：原推文標題寫「Claude Code 中你不知道的免費功能」，但影片實際內容是 Prompting 101（Claude API／console 的提示詞技巧），與 Claude Code 功能無關。

## 重點表

| 時間 | 重點 |
|---|---|
| 00:00 | 開場；提示工程＝寫清楚指令、給足脈絡、安排資訊順序 |
| 00:52 | 情境：瑞典保險公司以車禍報告表（17 個勾選框）＋手繪草圖判斷誰有過失 |
| 02:05 | v1 極簡提示詞：Claude 誤以為是滑雪事故 |
| 03:17 | 提示詞結構與十個要點總覽；提示工程是迭代的實證科學 |
| 05:25 | v2：任務脈絡＋語氣（保持事實、有把握才判斷） |
| 08:40 | 背景資料放系統提示詞；固定內容適合 prompt caching |
| 09:37 | v3：用 XML 標籤組織資訊；Claude 更有信心判定 B 車有過失 |
| 12:51 | 範例（few-shot）：把棘手案例與解法放進系統提示詞 |
| 14:55 | 對話歷史：面向使用者的應用才需要 |
| 15:45 | 結尾重述任務、防幻覺（看不清就說看不清） |
| 16:56 | v4：逐步思考，先看表單再看草圖，順序很重要 |
| 20:01 | v5：輸出格式，最終判定包進 final verdict 標籤 |
| 22:10 | 預填回應（prefill）控制輸出開頭與格式 |
| 23:14 | 延伸思考可當提示工程的輔助，用思考軌跡改進系統提示詞 |
| 24:14 | 結語；預告「面向智能體的提示詞」場次 |

## 十個要點（影片投影片）

1. Task context　2. Tone context　3. Background data, documents, images　4. Detailed task description & rules　5. Examples　6. Conversation history　7. Immediate task description or request　8. Thinking step by step　9. Output formatting　10. Prefilled response

## 名詞與縮寫

- **System prompt（系統提示詞）**：放不隨查詢改變的背景與規則。
- **Prompt caching**：快取固定內容以省時省成本。
- **Few-shot（範例）**：以範例引導模型行為。
- **Prefill**：預先寫好 Assistant 回應開頭，讓模型接著寫。
- **Extended thinking（延伸思考）**：混合推理模型可開啟的思考模式。

## 轉錄校正備註

- 來源為平台英文字幕（人工）。全文把 `Cloud` 改回 `Claude`（影片明確講 Claude 3.7／Claude 4／ClaudePlays Pokémon）。
- 「Claude 4 solid」→「Sonnet」、「max soaking budget」→「max thinking budget」為**推測**；「Edelman application」語意不明，保留原文，見 `meta.json.known_asr_errors`。
- 影片數字與模型說法（如 Claude 4 Sonnet、temperature 0、17 個勾選框）皆為講者主張，未查證。
