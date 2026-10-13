# 教學影片「操作 SOP」步驟 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 電腦工具教學影片歸檔時，多一個「消化報告 → 整理成 step by step 操作 SOP」的步驟，產出 `sop.md`，併入報告並另輸出 `*_sop.docx`。

**Architecture:** `sop.md` 是手寫（由 Claude 撰寫）、重跑不覆蓋的獨立檔，與 `supplement.md` 同一套解析（抽成共用函式）。SOP 內的截圖以 `![說明](frame@MM:SS)` 寫時間，`build_report.py` 在建報告時換成最接近該時間的 `frames/` 檔，所以重跑後檔名重編也對得上。`watch_archive.py` 只新增 `--sop/--no-sop` 旗標與 `meta.json` 的 `video_type`、`sop_mode` 兩個欄位（重跑保留）。

**Tech Stack:** Python 3.12、python-docx、Pillow、unittest（環境沒有 pytest）。

**Spec:** 本對話 /grill-me 的共識（Q1–Q12），摘要如下：
1. 判定：Claude 判斷是否為螢幕操作教學（軟體、網頁、CLI、手機 App／系統設定；實體硬體不算），寫入 `meta.json.video_type: "tutorial"`；`--sop`／`--no-sop` 強制開關，記在 `meta.json.sop_mode`（`auto`／`on`／`off`），重跑沿用。
2. 產出：同資料夾 `sop.md`；報告在「摘要」之後加「操作 SOP」；另輸出 `<stem>_sop.md`＋`<stem>_sop.docx`（只有 SOP 與截圖）。
3. 內容：依任務分章；每章「前置條件／編號步驟／注意事項」；步驟含動作、畫面原文按鈕名稱、預期結果、時間戳；關鍵步驟附截圖；只收可重現的操作；影片沒示範的標「影片未示範」或「推測」；費用、硬體需求標「講者主張，未查證」；影片有示範錯誤時加排解表。
4. 截圖只用 `frames/`（缺圖補 `--timestamps` cue 重跑）。
5. 先用 ComfyUI 影片試作，使用者滿意後才寫進 SKILL.md／CLAUDE.md／README；舊歸檔（Kind、Neo4j）不補。

## Global Constraints

- 回覆與所有文件使用繁體中文（zh-TW）；不得印出或寫入任何 API key。
- 測試指令：`python -m unittest discover -s tests -v`（Windows 本機要先 `export PYTHONUTF8=1`）。
- `sop.md` 與 `supplement.md` 重跑不得被覆蓋；`frames/` 每次重跑會被清空重編號。
- docx 轉換器只支援三層標題（`#`～`###`）、`- ` 項目、表格、圖片、``` 區塊；`1. ` 這類編號行會變成一般段落（保留原文字），可接受。
- Commit 訊息結尾：`Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` 與 `Claude-Session: d2ad0fc7-7ab3-4564-b640-970fac3d580f`。
- 分支：`claude/archive-comfyui-claude`（目前所在）。

## Review Focus

- `sop.md` 只有標題或不存在 → 報告不出現 SOP 章節、不產生 `*_sop.*`。（Task 1、2）
- `sop_mode == "off"` 但 `sop.md` 存在 → 不併入也不輸出。（Task 2）
- `frame@時間` 落在兩張截圖之間、超過 1 小時（`1:02:03`）、或沒有 `frames.json` → 取最近的一張；沒有任何截圖時留下文字提示而非壞圖。（Task 1）
- `sop.md` 被刪除後重建 → 舊的 `*_sop.docx` 不殘留。（Task 2）
- 重跑 `watch_archive.py` 不加旗標 → `video_type`、`sop_mode` 保留；`--sop --no-sop` 同時給要報錯。（Task 3）

## File Structure

- `scripts/build_report.py`（修改）：共用的「獨立檔併入報告」解析、`frame@` 解析、`sop_lines`、獨立 SOP 輸出。
- `scripts/watch_archive.py`（修改）：旗標與 meta 欄位。
- `tests/test_watch_archive.py`（修改）：沿用現有檔案與風格，新增測試類別。
- `watch-output/<ComfyUI 資料夾>/sop.md`（新增，試作）。
- `.claude/skills/watch-archive/SKILL.md`、`CLAUDE.md`、`README.md`、`docs/watch-archive-flow.svg/.png`（Task 5，使用者審過試作後才改）。

---

### Task 1: 共用解析、`frame@` 解析、`sop_lines`

**Files:**
- Modify: `scripts/build_report.py:164-200`（`supplement_lines`）
- Test: `tests/test_watch_archive.py`（在 `FenceHelpers` 之前新增 `SopLines`）

**Interfaces:**
- Consumes: 既有 `FENCE_OPEN`、`fence_close`、`to_sec`。
- Produces:
  - `include_lines(path: Path, heading: str, frames: list | None = None) -> list[str]`：讀 `path`，規則同現有 `supplement_lines`；非 fence 行的 `![x](frame@TS)` 以 `frames` 解析。無內容回 `[]`。
  - `resolve_frame_ref(line: str, frames: list) -> str`
  - `supplement_lines(dest: Path) -> list[str]`（行為不變，改呼叫 `include_lines`）
  - `sop_lines(dest: Path, frames: list) -> list[str]`：標題 `## 操作 SOP（依影片整理，照著做）`。

- [ ] **Step 1: 寫失敗的測試**

在 `tests/test_watch_archive.py` 的 `class FenceHelpers` 前加入：

```python
class SopLines(unittest.TestCase):
    FRAMES = [{"file": "cue_0001.jpg", "t": "01:00"}, {"file": "cue_0002.jpg", "t": "05:26"},
              {"file": "cue_0003.jpg", "t": "1:02:03"}]

    def run_sop(self, text, frames=None):
        d = Path(tempfile.mkdtemp())
        if text is not None:
            (d / "sop.md").write_text(text, encoding="utf-8")
        return br.sop_lines(d, self.FRAMES if frames is None else frames)

    def test_missing_empty_and_title_only(self):
        self.assertEqual(self.run_sop(None), [])
        self.assertEqual(self.run_sop(""), [])
        self.assertEqual(self.run_sop("# 操作 SOP\n\n"), [])

    def test_heading_and_chapters(self):
        out = self.run_sop("# 操作 SOP\n\n## 一、安裝\n1. 下載\n### 注意事項\n- 費用\n")
        self.assertEqual(out[0], "## 操作 SOP（依影片整理，照著做）")
        self.assertIn("### 一、安裝", out)
        self.assertIn("1. 下載", out)
        self.assertIn("**注意事項**", out)

    def test_frame_ref_picks_nearest_frame(self):
        out = "\n".join(self.run_sop("## 一\n![設定畫面](frame@05:00)\n![x](frame@1:02:00)\n"))
        self.assertIn("![設定畫面](frames/cue_0002.jpg)", out)  # 05:00 is closer to 05:26 than 01:00
        self.assertIn("![x](frames/cue_0003.jpg)", out)

    def test_frame_ref_inside_fence_untouched(self):
        out = self.run_sop("## 一\n```\n![a](frame@01:00)\n```\n")
        self.assertIn("![a](frame@01:00)", out)

    def test_frame_ref_without_any_frames_leaves_note_not_broken_image(self):
        out = "\n".join(self.run_sop("## 一\n![a](frame@01:00)\n步驟\n", frames=[]))
        self.assertNotIn("frame@", out)
        self.assertNotIn("![", out)
        self.assertIn("（缺截圖：01:00）", out)
        self.assertIn("步驟", out)

    def test_supplement_behaviour_unchanged(self):
        d = Path(tempfile.mkdtemp())
        (d / "supplement.md").write_text("# 補充資料\n\n## S1｜x\n- a\n", encoding="utf-8")
        out = br.supplement_lines(d)
        self.assertEqual(out[0], "## 補充資料（影片未呈現的資訊）")
        self.assertIn("### S1｜x", out)
```

- [ ] **Step 2: 執行確認失敗**

Run: `export PYTHONUTF8=1; python -m unittest tests.test_watch_archive.SopLines -v`
Expected: FAIL，`AttributeError: module 'build_report' has no attribute 'sop_lines'`

- [ ] **Step 3: 實作**

把 `scripts/build_report.py` 的 `supplement_lines` 整段（`def supplement_lines` 到 `return ["## 補充資料（影片未呈現的資訊）", ""] + out + [""]`）換成：

```python
FRAME_REF = re.compile(r"!\[([^\]]*)\]\(frame@(\d+:\d+(?::\d+)?)\)")


def resolve_frame_ref(line: str, frames: list) -> str:
    """Replace ![alt](frame@MM:SS) with the frames/ file closest in time (frames/ is renumbered on every run, so
    hand-written files refer to a time, not a file name). With no frames, leave a text note instead of a broken image."""
    def repl(m):
        cands = [(abs(to_sec(f["t"]) - to_sec(m.group(2))), f["file"]) for f in frames if f.get("file") and f.get("t")]
        if not cands:
            return f"（缺截圖：{m.group(2)}）"
        return f"![{m.group(1)}](frames/{min(cands)[1]})"
    return FRAME_REF.sub(repl, line)


def include_lines(path: Path, heading: str, frames=None):
    """Body of a hand-written side file (supplement.md, sop.md) for the report, under '## <heading>'.

    The file's leading '# …' title is dropped; '#'/'##' headings -> '###' heading; '###' and deeper -> bold line
    (the docx converter handles at most three heading levels). Fenced blocks (``` or ~~~) are kept verbatim with
    their original markers, so a ~~~ block may contain ```; an unclosed fence is closed at the end, and md_to_docx
    renders fences as indented monospace. Outside fences, ![alt](frame@MM:SS) is resolved against `frames`.
    Returns [] when the file is missing or has no content besides its title.
    """
    if not path.exists():
        return []
    out, fence, has_body, started = [], None, False, False
    for line in path.read_text(encoding="utf-8").splitlines():
        m_fence = FENCE_OPEN.match(line)
        if fence:
            if fence_close(fence, line):
                out.append(fence)
                fence = None
            else:
                out.append(line)
        elif m_fence:
            fence, has_body, started = m_fence.group(1), True, True
            out.append(fence)
        elif (m := re.match(r"^(#{1,6})\s+(.*)$", line)):
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1 and not started:  # the file's own title; the section heading replaces it
                started = True
                continue
            started = has_body = True
            out.append(f"**{text}**" if level >= 3 else f"### {text}")
        else:
            if line.strip():
                started = has_body = True
            out.append(resolve_frame_ref(line, frames or []) if frames is not None else line)
    if fence:
        out.append(fence)
    if not has_body:
        return []
    return [f"## {heading}", ""] + out + [""]


def supplement_lines(dest: Path):
    return include_lines(dest / "supplement.md", "補充資料（影片未呈現的資訊）")


def sop_lines(dest: Path, frames: list):
    return include_lines(dest / "sop.md", "操作 SOP（依影片整理，照著做）", frames)
```

- [ ] **Step 4: 執行確認通過（含舊測試）**

Run: `python -m unittest discover -s tests -v 2>&1 | tail -5`
Expected: `OK`（原有 73 個加新增 6 個，皆通過）

- [ ] **Step 5: Commit**

```bash
git add scripts/build_report.py tests/test_watch_archive.py docs/superpowers/plans/2026-10-13-tutorial-sop.md
git commit -m "build_report：抽出 include_lines，新增 sop_lines 與 frame@時間 截圖解析

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: d2ad0fc7-7ab3-4564-b640-970fac3d580f"
```

---

### Task 2: 報告併入 SOP、輸出獨立 `*_sop.docx`

**Files:**
- Modify: `scripts/build_report.py`（`build_md`、`build`）
- Test: `tests/test_watch_archive.py`（新增 `BuildWithSop`）

**Interfaces:**
- Consumes: Task 1 的 `sop_lines(dest, frames)`。
- Produces:
  - `build_md(dest, meta, summary, segs, frames)`：`meta.get("sop_mode") != "off"` 時，在摘要後、補充資料前插入 `sop_lines`。
  - `sop_md(dest, meta, frames) -> str | None`：獨立 SOP 的 Markdown；無 SOP 或 `sop_mode == "off"` 回 `None`。
  - `build(dest) -> tuple[Path, ...]`：回傳 `(report.md, report.docx)`，有 SOP 時再加 `(sop.md, sop.docx)`；舊的 `*_sop.*` 會先清掉。

- [ ] **Step 1: 寫失敗的測試**

```python
class BuildWithSop(unittest.TestCase):
    def make(self, sop=None, sop_mode=None):
        import json
        from PIL import Image
        root = Path(tempfile.mkdtemp())
        d = root / "2026-10-13_YouTube_測試影片__abc123"
        (d / "frames").mkdir(parents=True)
        Image.new("RGB", (320, 180), (200, 200, 200)).save(d / "frames" / "cue_0001.jpg")
        meta = {"url": "https://example.com/v", "platform": "YouTube", "title": "測試影片", "duration": "01:00 (60s)",
                "keywords": ["k"], "slides": []}
        if sop_mode:
            meta["sop_mode"] = sop_mode
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        (d / "summary.md").write_text("# 摘要\n\n內容\n", encoding="utf-8")
        (d / "transcript.md").write_text("# t\n\n```\n[00:01] 你好\n```\n", encoding="utf-8")
        (d / "frames.json").write_text(json.dumps([{"file": "cue_0001.jpg", "t": "00:30"}]), encoding="utf-8")
        if sop is not None:
            (d / "sop.md").write_text(sop, encoding="utf-8")
        return d

    SOP = "# 操作 SOP\n\n## 一、安裝\n1. 下載（00:30）\n![畫面](frame@00:31)\n"

    def names(self, d):
        return sorted(p.name for p in d.iterdir() if p.is_file())

    def test_sop_in_report_before_supplement_and_standalone_files(self):
        d = self.make(self.SOP)
        (d / "supplement.md").write_text("## S1\n- a\n", encoding="utf-8")
        outs = br.build(d)
        self.assertEqual(len(outs), 4)
        md = outs[0].read_text(encoding="utf-8")
        self.assertLess(md.index("## 操作 SOP"), md.index("## 補充資料"))
        self.assertLess(md.index("## 摘要與名詞說明"), md.index("## 操作 SOP"))
        self.assertIn("![畫面](frames/cue_0001.jpg)", md)
        sop = (d / [n for n in self.names(d) if n.endswith("_sop.md")][0]).read_text(encoding="utf-8")
        self.assertTrue(sop.startswith("# 測試影片：操作 SOP"))
        self.assertNotIn("## 摘要", sop)
        self.assertNotIn("你好", sop)  # no transcript in the standalone SOP
        self.assertIn("## 一、安裝", sop)  # chapters promoted one level
        from docx import Document
        doc = Document(str([d / n for n in self.names(d) if n.endswith("_sop.docx")][0]))
        self.assertEqual(len(doc.inline_shapes), 1)

    def test_no_sop_file_means_no_section_and_no_sop_outputs(self):
        d = self.make(None)
        outs = br.build(d)
        self.assertEqual(len(outs), 2)
        self.assertNotIn("操作 SOP", outs[0].read_text(encoding="utf-8"))
        self.assertFalse([n for n in self.names(d) if "_sop." in n])

    def test_title_only_sop_means_nothing(self):
        d = self.make("# 操作 SOP\n\n")
        self.assertEqual(len(br.build(d)), 2)

    def test_sop_mode_off_skips_even_with_file(self):
        d = self.make(self.SOP, sop_mode="off")
        outs = br.build(d)
        self.assertEqual(len(outs), 2)
        self.assertNotIn("操作 SOP", outs[0].read_text(encoding="utf-8"))

    def test_stale_sop_outputs_removed_when_sop_deleted(self):
        d = self.make(self.SOP)
        br.build(d)
        (d / "sop.md").unlink()
        br.build(d)
        self.assertFalse([n for n in self.names(d) if "_sop." in n])
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -m unittest tests.test_watch_archive.BuildWithSop -v 2>&1 | tail -8`
Expected: FAIL（`len(outs)` 為 2、或報告沒有 SOP 章節）

- [ ] **Step 3: 實作**

在 `scripts/build_report.py` 的 `build_md` 裡，把

```python
    L += ["## 摘要與名詞說明", "", close_open_fence(strip_h1(summary).strip()), ""]
    sup = supplement_lines(dest)
```

改成

```python
    L += ["## 摘要與名詞說明", "", close_open_fence(strip_h1(summary).strip()), ""]
    if meta.get("sop_mode") != "off":
        L += sop_lines(dest, frames)
    sup = supplement_lines(dest)
```

在 `build_md` 之後新增：

```python
def sop_md(dest: Path, meta, frames):
    """Standalone SOP document (no transcript): title, source, then the SOP chapters one heading level up."""
    if meta.get("sop_mode") == "off":
        return None
    lines = sop_lines(dest, frames)
    if not lines:
        return None
    body = ["## " + l[4:] if l.startswith("### ") else l for l in lines[2:]]
    head = [f"# {meta['title']}：操作 SOP", "",
            f"- 來源：{meta['url']}（影片中的操作，步驟後標註影片時間）",
            f"- 更新日期：{meta.get('last_updated', '')}",
            "- 說明：本文由影片整理；影片中的價格、硬體需求與效果為講者主張，未查證。", ""]
    return "\n".join(head + body)
```

把 `build` 換成：

```python
def build(dest: Path):
    meta, summary, segs, frames = load(dest)
    md = build_md(dest, meta, summary, segs, frames)
    stem = file_stem(dest)
    for old in ("report.md", "report.docx", *dest.glob("*_report.*"), *dest.glob("*_sop.*")):  # drop stale / legacy names
        (dest / old).unlink(missing_ok=True)
    out_md, out_docx = dest / f"{stem}_report.md", dest / f"{stem}_report.docx"
    out_md.write_text(md, encoding="utf-8")
    md_to_docx(dest, md, out_docx, meta.get("keywords"))
    outs = [out_md, out_docx]
    standalone = sop_md(dest, meta, frames)
    if standalone:
        s_md, s_docx = dest / f"{stem}_sop.md", dest / f"{stem}_sop.docx"
        s_md.write_text(standalone, encoding="utf-8")
        md_to_docx(dest, standalone, s_docx, meta.get("keywords"))
        outs += [s_md, s_docx]
    return tuple(outs)
```

- [ ] **Step 4: 執行確認通過**

Run: `python -m unittest discover -s tests -v 2>&1 | tail -4`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/build_report.py tests/test_watch_archive.py
git commit -m "build_report：報告併入操作 SOP，並另輸出 *_sop.md／*_sop.docx

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: d2ad0fc7-7ab3-4564-b640-970fac3d580f"
```

---

### Task 3: `--sop`／`--no-sop` 旗標與 meta 欄位

**Files:**
- Modify: `scripts/watch_archive.py`（`main()` 的參數區約 L362–366，meta 區約 L474–477；新增 `resolve_sop_mode`）
- Test: `tests/test_watch_archive.py`（新增 `SopMode`）

**Interfaces:**
- Produces: `resolve_sop_mode(sop: bool, no_sop: bool, remembered: str) -> str`，回傳 `"on"`／`"off"`／`"auto"`；`meta.json` 新欄位 `sop_mode`（字串）與 `video_type`（字串，預設 `""`，手動／Claude 寫入，重跑保留）。

- [ ] **Step 1: 寫失敗的測試**

```python
class SopMode(unittest.TestCase):
    def test_default_is_auto(self):
        self.assertEqual(wa.resolve_sop_mode(False, False, ""), "auto")

    def test_flags_override_and_are_remembered(self):
        self.assertEqual(wa.resolve_sop_mode(True, False, ""), "on")
        self.assertEqual(wa.resolve_sop_mode(False, True, "on"), "off")
        self.assertEqual(wa.resolve_sop_mode(False, False, "off"), "off")  # rerun without flag keeps it

    def test_unknown_remembered_value_falls_back_to_auto(self):
        self.assertEqual(wa.resolve_sop_mode(False, False, "weird"), "auto")

    def test_both_flags_rejected_by_cli(self):
        import subprocess
        p = subprocess.run([sys.executable, str(Path(wa.__file__)), "https://youtu.be/x", "--sop", "--no-sop"],
                           capture_output=True, text=True, env=dict(os.environ, PYTHONUTF8="1"))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("not allowed with", p.stderr)
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -m unittest tests.test_watch_archive.SopMode -v 2>&1 | tail -6`
Expected: FAIL，`AttributeError: ... no attribute 'resolve_sop_mode'`

- [ ] **Step 3: 實作**

在 `pick_whisper` 前加入：

```python
def resolve_sop_mode(sop: bool, no_sop: bool, remembered: str) -> str:
    """'on'/'off' forced by --sop/--no-sop (remembered across reruns); otherwise 'auto' = Claude decides from the video."""
    if sop:
        return "on"
    if no_sop:
        return "off"
    return remembered if remembered in ("on", "off") else "auto"
```

在 `ap.add_argument("--resolution"...)` 之後、`args = ap.parse_args()` 之前加入：

```python
    sg = ap.add_mutually_exclusive_group()
    sg.add_argument("--sop", action="store_true", help="force the step-by-step SOP step (computer-tool tutorials); remembered")
    sg.add_argument("--no-sop", action="store_true", help="skip the SOP step even if sop.md exists; remembered")
```

在 `meta = {` 內 `"slides": ...` 之後加入：

```python
        "video_type": prev.get("video_type", ""),  # hand-curated: "tutorial" when the video is a screen-operation tutorial
        "sop_mode": resolve_sop_mode(args.sop, args.no_sop, prev.get("sop_mode", early_meta.get("sop_mode", ""))),
```

- [ ] **Step 4: 執行確認通過**

Run: `python -m unittest discover -s tests -v 2>&1 | tail -4`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/watch_archive.py tests/test_watch_archive.py
git commit -m "watch_archive：新增 --sop／--no-sop，meta 保留 video_type 與 sop_mode

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: d2ad0fc7-7ab3-4564-b640-970fac3d580f"
```

---

### Task 4: ComfyUI 試作 `sop.md`（完成後停下，交使用者審）

**Files:**
- Create: `watch-output/2026-10-13_YouTube_免費製作-AI-影片-ComfyUI-接上-Claude-MCP__fAWliYuOiuc/sop.md`
- Modify: 同資料夾 `meta.json`（加 `"video_type": "tutorial"`、`"sop_mode": "on"`）

**Interfaces:**
- Consumes: Task 1–3 的建置；`transcript.md`、`frames.json`、`supplement` 無。

章節（依任務）與每章來源時間：一、安裝與啟動（00:37–01:34）；二、使用範本與基本操作（01:34–03:54）；三、下載缺少的模型與模型位置（03:54–05:02）；四、生成圖片並儲存（05:02–06:31）；五、生成音樂（06:31–08:07）；六、雲端生成影片（08:07–10:45）；七、安裝 Comfy MCP 並讓 Claude 操作（10:45–14:55）；八、錯誤排解表（缺少模型；缺少初始圖檔）。每章格式：

```markdown
## 一、章名（影片 MM:SS–MM:SS）
### 前置條件
- …（費用／硬體標「講者主張，未查證」；影片沒說明的標「影片未示範」）
### 步驟
1. 動作，按鈕名稱照畫面原文（MM:SS）。預期結果：…
   ![說明](frame@MM:SS)   # 只有關鍵步驟才附
### 注意事項
- …
```

- [ ] **Step 1: 依逐字稿與 cue 截圖寫 `sop.md`**（Claude 以 Read 逐章重看 `transcript.md` 與 `frames/cue_*.jpg`，按鈕名稱以畫面為準；影片沒示範者標註）
- [ ] **Step 2: 更新 `meta.json`**

```bash
python - <<'EOF'
import json
p="watch-output/2026-10-13_YouTube_免費製作-AI-影片-ComfyUI-接上-Claude-MCP__fAWliYuOiuc/meta.json"
m=json.load(open(p,encoding="utf-8")); m["video_type"]="tutorial"; m["sop_mode"]="on"
json.dump(m,open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
EOF
```

- [ ] **Step 3: 重建並檢查**

```bash
python scripts/build_report.py "watch-output/2026-10-13_YouTube_免費製作-AI-影片-ComfyUI-接上-Claude-MCP__fAWliYuOiuc"
soffice --headless --convert-to pdf --outdir "$SCRATCH" "<資料夾>/*_sop.docx"
```
Expected: 輸出四個檔；SOP PDF 的中文、截圖、編號步驟都正常，頁數合理（目標 ≤ 8 頁）。

- [ ] **Step 4: 交付使用者審閱（SendUserFile 傳 `*_sop.docx`，摘要 SOP 結構）；等使用者確認格式後才做 Task 5。不 commit 文件變更。**

---

### Task 5: 寫進流程文件並提交（使用者確認試作後才做）

**Files:**
- Modify: `.claude/skills/watch-archive/SKILL.md`（流程總覽、步驟 1 旗標、產出清單、新增 4d）
- Modify: `CLAUDE.md`（硬規則一條、常用指令加 `[--sop|--no-sop]`）
- Modify: `README.md`（資料夾結構加 `sop.md`、`*_sop.docx`；新增「操作 SOP」小節）
- Modify: `docs/watch-archive-flow.svg`、`docs/watch-archive-flow.png`

- [ ] **Step 1: SKILL.md** — 流程總覽的文字行 `4c 補充資料 ─▶ 5 重建報告` 前插入 `4d 教學影片→操作 SOP(選用 sop.md)`；步驟 1 加 `--sop／--no-sop` 說明；產出清單加 `sop.md`、`<stem>_sop.md`、`<stem>_sop.docx`；在 4c 之後新增：

```markdown
   - **4d 操作 SOP（`sop.md`，電腦工具教學影片）**：影片是在螢幕上示範軟體、網頁服務、CLI、程式碼、手機 App 或系統設定的操作時（實體硬體教學不算），消化報告後把它重新整理成可照著做的 SOP，寫入 `meta.json.video_type: "tutorial"`；`--sop`／`--no-sop` 可強制開關（記在 `sop_mode`，重跑沿用）。
     - **依任務分章**，每章：`### 前置條件`（硬體、帳號、費用、要先完成的章節）、編號步驟、`### 注意事項`。
     - **每個步驟**：動作＋畫面上的按鈕或欄位**原文**（以截圖為準，不憑逐字稿）＋預期結果＋影片時間；關鍵步驟（設定畫面、錯誤提示、參數欄位）附 `![說明](frame@MM:SS)`，建報告時會換成最接近該時間的截圖，所以重跑後仍對得上；缺圖時補 `--timestamps` cue 重跑。
     - **只收可重現的操作**；講者的觀點與評價不收。影片沒示範的標「影片未示範」，Claude 補的標「推測」；價格、硬體需求、版本、效果一律標「講者主張，未查證」。
     - 影片有示範錯誤時，章末加「錯誤排解」表（現象／原因／做法／影片時間）。
     - `build_report.py` 會把 SOP 放在報告「摘要」之後，並另輸出 `<stem>_sop.docx`（只有 SOP 與截圖）；交付時一併傳送。
```

- [ ] **Step 2: CLAUDE.md** — 硬規則加一條：`- 電腦工具教學影片（螢幕操作示範）：消化報告後另寫 sop.md（依任務分章、編號步驟、按鈕名稱照畫面原文、沒示範的標「影片未示範」／「推測」），見 SKILL 4d。`；常用指令的歸檔列加 `[--sop|--no-sop]`。
- [ ] **Step 3: README.md** — 資料夾結構加兩行；在「補充資料」小節後加「### 操作 SOP（`sop.md`）」，內容同 SKILL 4d 的摘要。
- [ ] **Step 4: 流程圖** — 在 SVG 的 4c 與 5 之間加一個橘色方框「4d 教學影片→操作 SOP」，依 SKILL.md 的 Windows 指令用 Edge headless 重新產生 PNG，Read 看圖確認文字沒超出方框。
- [ ] **Step 5: 全部測試與 SOP 重建確認**

Run: `python -m unittest discover -s tests -v 2>&1 | tail -3` 與 `python scripts/build_report.py <ComfyUI 資料夾>`
Expected: `OK`；四個檔案產出。

- [ ] **Step 6: Commit 並 push**

```bash
git add .claude/skills/watch-archive/SKILL.md CLAUDE.md README.md docs/ watch-output/2026-10-13_YouTube_免費製作-AI-影片-ComfyUI-接上-Claude-MCP__fAWliYuOiuc
git commit -m "watch-archive：教學影片新增 4d 操作 SOP 步驟；ComfyUI 試作 sop.md

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: d2ad0fc7-7ab3-4564-b640-970fac3d580f"
git push
```

---

## Self-Review

- **Spec coverage：** 判定與旗標（Q1）→ Task 3；產出位置與獨立 docx（Q2、Q7、Q8）→ Task 1、2；內容規則（Q3、Q4、Q5、Q10）→ Task 4、5（文件）；截圖（Q9）→ Task 1（`frame@`）、Task 5；範圍（Q11）→ Task 5；先試作（Q6、Q12）→ Task 4 停點、Task 5 在審後。無缺口。
- **Placeholder scan：** Task 4 的 `sop.md` 內容由 Claude 讀逐字稿撰寫，章節與格式已定；其餘步驟皆有程式或具體文字。
- **型別一致：** `include_lines(path, heading, frames=None)`、`sop_lines(dest, frames)`、`sop_md(dest, meta, frames)`、`resolve_sop_mode(sop, no_sop, remembered)`、`build()` 回傳 tuple，各 Task 引用一致。注意 `include_lines` 在 `frames is None`（supplement）時不解析 `frame@`，`frames=[]`（SOP 無截圖）時才輸出「缺截圖」提示。
- **Review Focus：** 五項皆有對應測試（Task 1：frame@ 邊界與無截圖；Task 2：off、空檔、殘留；Task 3：重跑保留與互斥旗標）。
