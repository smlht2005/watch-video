<!-- ppt-master-schema: design-spec/v1 -->
# 聊天不要聊自己，要聊對方剛才那一句：七天接話練習 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | 聊天不要聊自己，要聊對方剛才那一句：七天接話練習 |
| Canvas Format | PPT 16:9 (1280×720) |
| Page Count | 11 |
| Primary Language | zh-TW |
| Target Audience | 想改善對話與人際溝通的一般職場人士或學習者 |
| Communication Intent | 把影片的「七天接話練習」整理成可照做的簡報，先講原理對比，再逐日拆解，最後給日常加練與結語 |
| Desired Audience Outcome | 看完能說出「聊對方剛才那一句」的做法，並照七天計畫開始練習 |
| Core Message / Ask / Action | 把注意力放在對方剛才那句話上，話題就接得住、拉得長（講者主張，未查證） |
| Delivery Context | 閱讀為主，也可作為分享講稿（讀者與講者並重） |
| Artifact Afterlife | 可留作自我練習清單與分享素材 |
| Reading Mode | balanced |
| Content Strategy | 只用影片內容；效果類說法一律標「講者主張，未查證」；不加影片沒有的內容 |
| Design Style | 暖調對話氣泡：奶油白底、圓角卡片與對話氣泡、珊瑚橘強調 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — final Stage-2 proactive policy |
| Custom Animations | disabled — workflow default |
| Narration Audio | disabled — workflow default |
| Created Date | 2026-11-05 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px left/right, 48 px top/bottom |
| Content Area | x 64–1216, y 48–672 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode Behavior**: 以教學式步驟推進：先用「聊自己 vs 聊對方」對比建立原理，再每天一頁（做法＋範例句），最後以日常加練和一句核心結語收束；每頁一個重點。
- **Mode References**: instructional
- **Visual style**: custom
- **Visual Style Behavior**: 圓角卡片與對話氣泡為主要載體；大量留白；氣泡用左右兩側與顏色區分「我說／對方說」；天數用大圓形編號；線條圖示，無陰影堆疊，僅極淺的卡片底色層次；標題粗黑體、內文中等字重。
- **Visual Style References**: soft-rounded
- **Theme**: 親切、清楚、像在聊天的練習手冊
- **Tone**: 溫暖、鼓勵、實用

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #FBF6EE | 頁面底色（奶油白） |
| Secondary background | #F3E9DA | 卡片、氣泡底色 |
| Primary | #2F4858 | 標題、重點文字、「對方說」氣泡 |
| Accent | #F26B4E | 天數編號、強調詞、「我說」氣泡 |
| Secondary accent | #E9B872 | 次要標記、裝飾圓點 |
| Body text | #2B2B2B | 內文 |
| Secondary text | #6B7280 | 註記、出處、免責標示 |
| Divider | #E2D6C3 | 分隔線、卡片邊線 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 粗黑體 | Microsoft JhengHei | Arial | sans-serif |
| Body | 中等黑體 | Microsoft JhengHei | Arial | sans-serif |

- **Title stack**: "Microsoft JhengHei", "PingFang TC", Arial, sans-serif
- **Body stack**: "Microsoft JhengHei", "PingFang TC", Arial, sans-serif

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 24 |
| Title | 40 |
| Subtitle | 28 |
| Annotation | 18 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 視線由左上標題與天數編號進入，經中央範例對話氣泡，到下方「做法」要點。
- **Composition tendency**: 左側大編號與標題，右側對話氣泡示範；對比頁左右並列；封面與結語以單一核心句為焦點。
- **Cross-page continuity**: 第一至第七天共用同一版式（左編號圓、右範例氣泡、下方做法卡），讓讀者像翻練習卡；氣泡色固定：我說＝珊瑚橘、對方說＝深藍灰。
- **Spacing posture**: open，錨點頁（封面、結語）更疏，步驟頁適中。
- **Spacing anchors**: page margin 64, block gap 24, column gutter 32, corner radius 20, body leading 1.5

## VI. Icon Usage Specification

- **Primary bundled library**: tabler-outline
- **Stroke Width**: 2

| Icon Path | Suitable Scenarios |
| --- | --- |
| tabler-outline/ear | 聽 |
| tabler-outline/search | 找 |
| tabler-outline/repeat | 複述 |
| tabler-outline/heart | 情緒 |
| tabler-outline/microphone | 採訪 |
| tabler-outline/snowflake | 冷場 |
| tabler-outline/target | 實戰 |
| tabler-outline/device-tv | 看節目 |
| tabler-outline/message-circle | 對話 |
| tabler-outline/messages | 對話 |
| tabler-outline/eye | 注意力 |
| tabler-outline/calendar | 七天 |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## IX. Content Outline

### Part 1: 原理

#### Slide 01 - 封面

- **Audience move**: 不知道怎麼接話 → 想知道「聊對方那一句」是什麼
- **Relationships**: 標題與副標、七天徽章
- **Composition**: 單一焦點：大標題居中偏左，右側一組空白氣泡與一個「7 天」圓徽章；底部一行標示來源
- **Cover impact**: 鉤子＝「聊天不要聊自己」；構圖參考＝一個珊瑚橘氣泡指向一個深藍灰氣泡，中間是「對方剛才那一句」
- **Title**: 聊天不要聊自己，要聊對方剛才那一句
- **Core message**: 七天接話練習
- **Content**: 副標「七天，每天一個小動作」· 來源「TikTok @juzhongren33，3:04」· 註記「內容為講者主張，未查證」

#### Slide 02 - 兩種回法

- **Audience move**: 以為自己有在聊 → 看出「聊自己」會讓話題斷
- **Relationships**: contrast：聊自己 vs 聊對方；同一句開場對應兩種回應
- **Composition**: 左右並列兩組對話；右側（聊對方）較突出
- **Title**: 同一句話，兩種回法
- **Core message**: 回「學多久了？」比回「我也在學」更能讓對方越聊越來勁（講者主張）
- **Content**: 對方「我最近在學做菜」· 聊自己：「我也在學，我做了紅燒肉」→ 話題斷 · 聊對方：「學多久了？」→ 對方越聊越來勁（講者主張，未查證）

### Part 2: 七天練習

#### Slide 03 - 第一天 聽完再開口

- **Audience move**: 習慣搶話 → 願意先默數兩秒
- **Relationships**: order：對方說完 → 默數兩秒 → 再接
- **Composition**: 左大編號「1」，右範例氣泡，下方做法卡
- **Title**: 第一天　聽完再開口
- **Core message**: 等對方完整說完，再接話
- **Content**: 做法：等對方完整說完 · 默數兩秒再接 · 理由：避免說到一半就在組織自己的回答、漏聽後半段（講者主張，未查證）

#### Slide 04 - 第二天 找鉤子詞

- **Audience move**: 不知道問什麼 → 知道從哪個詞下手
- **Relationships**: parent：鉤子詞 → 圍繞它發問
- **Composition**: 同第一天版式；範例氣泡中將鉤子詞以強調色標示
- **Title**: 第二天　找鉤子詞
- **Core message**: 對方話裡資訊量最大或情緒最重的詞，就是下一句的切入點
- **Content**: 做法：挑出資訊量最大或最有情緒的詞 · 圍繞它發問 · 不必自己找話題（講者主張，未查證）

#### Slide 05 - 第三天 複述加一問

- **Audience move**: 只會「嗯嗯」 → 會先複述再追問
- **Relationships**: order：複述 → 追問
- **Composition**: 同版式；範例為複述氣泡後接追問氣泡
- **Title**: 第三天　複述加一問
- **Core message**: 先複述讓對方覺得被聽見，再追問讓話題延續
- **Content**: 做法：先複述對方的話 · 再追問一個問題 · 對方覺得被聽見、話題自然延續（講者主張，未查證）

#### Slide 06 - 第四天 先接情緒再接事件

- **Audience move**: 只回事情 → 先回應感受
- **Relationships**: order：情緒 → 事件
- **Composition**: 同版式；範例氣泡含「被當眾批評，那挺難受的吧？」
- **Title**: 第四天　先接情緒，再接事件
- **Core message**: 只接事件會顯得敷衍，先接情緒對方更願意說
- **Content**: 做法：先回應情緒，再決定怎麼接事件 · 範例：「被當眾批評，那挺難受的吧？」（講者主張，未查證）

#### Slide 07 - 第五天 模仿採訪式問法

- **Audience move**: 不知道怎麼追問 → 知道可以向主持人學
- **Relationships**: link：主持人的問法 → 自己的練習
- **Composition**: 同版式；範例為「主持人式」連續追問
- **Title**: 第五天　模仿採訪式問法
- **Core message**: 觀察主持人如何在對方的話上推進，不跳題、不轉移
- **Content**: 做法：看主持人怎麼追問 · 不跳題、不轉移話題 · 在對方的話上往下推進（講者主張，未查證）

#### Slide 08 - 第六天 專項破冷場

- **Audience move**: 遇到「還好」就卡住 → 會給選擇式追問
- **Relationships**: link：冷淡回應 → 追問＋選項
- **Composition**: 同版式；範例為「還好」被追問
- **Title**: 第六天　專項破冷場
- **Core message**: 對「還好」追問意思，並給選擇降低回答門檻
- **Content**: 範例：「還好是什麼意思？比上次好一點，還是差不多？」· 做法：追問加二選一（講者主張，未查證）

#### Slide 09 - 第七天 綜合實戰

- **Audience move**: 零散技巧 → 能整合使用並檢討
- **Relationships**: order：每句從對方那句出發 → 聊完檢討
- **Composition**: 同版式；做法卡改為檢核清單
- **Title**: 第七天　綜合實戰
- **Core message**: 每句話都從對方剛才那句出發，聊完檢討有沒有聊回自己
- **Content**: 做法：每句從對方剛才那句出發 · 聊完檢討：有沒有聊回自己（講者主張，未查證）

### Part 3: 延伸與結語

#### Slide 10 - 日常加練

- **Audience move**: 七天後不知道怎麼持續 → 有一個簡單的日常習慣
- **Relationships**: none
- **Composition**: 單一焦點：左側圖示與大字，右側一句說明
- **Title**: 日常加練
- **Core message**: 每天十分鐘看談話節目
- **Content**: 每天十分鐘看談話節目 · 觀察主持人如何接話（講者主張，未查證）

#### Slide 11 - 結語

- **Audience move**: 記住技巧 → 記住根本是注意力
- **Relationships**: none
- **Composition**: 單一核心句置中，周圍留白，一個「眼睛」圖示
- **Closing impact**: 綁定要點＝「底層是你有沒有真的把注意力放在對方身上」；構圖參考＝置中大字加一個氣泡
- **Title**: 底層是注意力
- **Core message**: 接話的根本是把注意力放在對方身上
- **Content**: 「底層是你有沒有真的把注意力放在對方身上」（講者主張，未查證）· 註記：資料來自 TikTok 影片，未經查證

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 每頁 2–4 句口語說明，只依影片內容；效果類說法標明為講者主張
- **Total duration**: 約 6 分鐘
- **Notes style**: conversational
- **Presentation purpose**: 把影片的「七天接話練習」整理成可照做的簡報，先講原理對比，再逐日拆解，最後給日常加練與結語
