<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-TW
- audience: 想改善對話與人際溝通的一般職場人士或學習者
- objective: 讓讀者看完能說出「聊對方剛才那一句」的做法，並照七天計畫開始練習
- core_message: 把注意力放在對方剛才那句話上，話題就接得住、拉得長（講者主張，未查證）
- consumption_mode: balanced

## mode
- mode: custom
- mode_references: instructional
- mode_behavior: 以教學式步驟推進：先用「聊自己 vs 聊對方」對比建立原理，再每天一頁（做法＋範例句），最後以日常加練和一句核心結語收束；每頁一個重點。

## visual_style
- visual_style: custom
- visual_style_references: soft-rounded
- visual_style_behavior: 圓角卡片與對話氣泡為主要載體；大量留白；氣泡用左右兩側與顏色區分我說與對方說；天數用大圓形編號；線條圖示，無陰影堆疊，僅極淺的卡片底色層次；標題粗黑體、內文中等字重。

## colors
- background: #FBF6EE
- secondary_bg: #F3E9DA
- primary: #2F4858
- accent: #F26B4E
- secondary_accent: #E9B872
- body_text: #2B2B2B
- secondary_text: #6B7280
- divider: #E2D6C3

## typography
- font_family: "Microsoft JhengHei", "PingFang TC", Arial, sans-serif
- title_family: "Microsoft JhengHei", "PingFang TC", Arial, sans-serif
- body_family: "Microsoft JhengHei", "PingFang TC", Arial, sans-serif
- body: 24
- title: 40
- subtitle: 28
- annotation: 18

## icons
- library: tabler-outline
- stroke_width: 2
- inventory: tabler-outline/ear, tabler-outline/search, tabler-outline/repeat, tabler-outline/heart, tabler-outline/microphone, tabler-outline/snowflake, tabler-outline/target, tabler-outline/device-tv, tabler-outline/message-circle, tabler-outline/messages, tabler-outline/eye, tabler-outline/calendar

## page_rhythm
- P01: anchor
- P02: dense
- P03: dense
- P04: dense
- P05: dense
- P06: dense
- P07: dense
- P08: dense
- P09: dense
- P10: breathing
- P11: anchor

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
