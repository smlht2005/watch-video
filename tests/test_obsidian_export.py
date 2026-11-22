"""Tests for scripts/obsidian_export.py. Run: python3 -m unittest discover -s tests -v"""
import io
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import obsidian_export as oe  # noqa: E402


class Fixture(unittest.TestCase):
    """Temp vault + archive folder builder shared by the export tests."""


    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.vault = self.root / "vault"
        for name, value in (("ROOT", self.root), ("OUT_ROOT", self.root / "watch-output")):
            old = getattr(oe, name)
            setattr(oe, name, value)
            self.addCleanup(setattr, oe, name, old)

    def folder(self, title="測試:影片?", vid="abc123", cat="AI", links=None, sop=False, carousel=False):
        from PIL import Image
        d = self.root / "watch-output" / cat / f"2026-10-27_Web_x__{vid}"
        (d / "frames").mkdir(parents=True)
        Image.new("RGB", (40, 40)).save(d / "frames" / "slide_01.jpg")
        meta = {"url": "https://example.com", "platform": "Web", "title": title, "video_id": vid,
                "keywords": ["知識管理", "2026"], "last_updated": "2026-10-27",
                "slides": [{"start": "00:01", "frame": "slide_01.jpg", "title": "第一頁"}]}
        if carousel:
            meta["media_type"] = "carousel"
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        (d / "summary.md").write_text("# 摘要\n\n內容\n\n## 名詞\n- a\n", encoding="utf-8")
        if links:
            (d / "links.md").write_text(links, encoding="utf-8")
        if sop:
            (d / "kb" / "attachments").mkdir(parents=True)
            Image.new("RGB", (40, 40)).save(d / "kb" / "attachments" / "step-0030.jpg")
            (d / "kb" / "測試_操作SOP.md").write_text('---\ntitle: "x"\ntype: sop\n---\n\n![圖](attachments/step-0030.jpg)\n', encoding="utf-8")
        return d



class MindMapText(Fixture):
    """影片筆記用 mindmap.md 的文字條列取代〈摘要〉與思維導圖 PNG。"""

    def note(self):
        return next((self.vault / "AI").glob("*.md")).read_text(encoding="utf-8")

    def test_text_mind_map_replaces_summary_and_png(self):
        from PIL import Image
        d = self.folder()
        (d / "mindmap.md").write_text("<!-- auto: built from slides -->\n# 大綱\n- 中心\n  - 分支一\n    - 細節\n", encoding="utf-8")
        Image.new("RGB", (10, 10)).save(d / "mindmap.png")
        oe.export(d, self.vault)
        text = self.note()
        self.assertIn("## 思維導圖\n\n- 中心\n  - 分支一\n    - 細節\n", text)
        self.assertNotIn("<!-- auto", text)
        self.assertNotIn("# 大綱", text)
        self.assertNotIn("## 摘要", text)
        self.assertNotIn("mindmap.png", text)
        self.assertFalse((self.vault / "_attachments" / "abc123" / "mindmap.png").exists())

    def test_reexport_clears_an_old_png(self):
        d = self.folder()
        old = self.vault / "_attachments" / "abc123" / "mindmap.png"
        old.parent.mkdir(parents=True)
        old.write_bytes(b"png")
        oe.export(d, self.vault)
        self.assertFalse(old.exists())

    def test_no_mindmap_md_falls_back_to_summary(self):
        oe.export(self.folder(), self.vault)
        text = self.note()
        self.assertNotIn("## 思維導圖", text)
        self.assertIn("## 摘要\n\n內容", text)

    def test_bullet_dots_and_multiline_comment_are_normalised(self):
        d = self.folder()
        (d / "mindmap.md").write_text("<!-- note\nsecond line -->\n• 中心\n  • 分支\n", encoding="utf-8")
        oe.export(d, self.vault)
        text = self.note()
        self.assertIn("## 思維導圖\n\n- 中心\n  - 分支\n", text)
        self.assertNotIn("second line", text)


class GalleryInNote(Fixture):
    """影片筆記在思維導圖之後加入〈圖文對照〉：截圖縮圖進 _attachments，段落含逐字稿。"""

    def note(self):
        return next((self.vault / "AI").glob("*.md")).read_text(encoding="utf-8")

    def test_gallery_after_mind_map_with_small_relative_pictures_and_transcript(self):
        from PIL import Image
        d = self.folder()
        Image.new("RGB", (2000, 1000)).save(d / "frames" / "slide_01.jpg")
        (d / "mindmap.md").write_text("- 中心\n", encoding="utf-8")
        (d / "transcript.md").write_text("```\n[00:01] 第一句\n[00:03] 第二句\n```\n", encoding="utf-8")
        (d / "knowledge.md").write_text("# 知識點\n## 已確認\n### 點一\n- 出處：00:01\n- 說明：x\n", encoding="utf-8")
        oe.export(d, self.vault)
        text = self.note()
        self.assertLess(text.index("## 思維導圖"), text.index("## 圖文對照（畫面 + 逐字稿）"))
        self.assertLess(text.index("## 圖文對照"), text.index("## 知識點"))
        self.assertIn("### 主題 1：第一頁", text)
        self.assertIn("第一句，第二句。", text)
        self.assertIn("![00:01](../_attachments/abc123/slide_01.jpg)", text)
        pic = self.vault / "_attachments" / "abc123" / "slide_01.jpg"
        self.assertLessEqual(max(Image.open(pic).size), 1024)

    def test_without_slides_gallery_uses_frames(self):
        from PIL import Image
        d = self.folder()
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        meta.pop("slides")
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        Image.new("RGB", (20, 20)).save(d / "frames" / "frame_0001.jpg")
        (d / "frames.json").write_text('[{"file": "frame_0001.jpg", "t": "00:00"}]', encoding="utf-8")
        (d / "transcript.md").write_text("[00:02] 說話\n", encoding="utf-8")
        oe.export(d, self.vault)
        text = self.note()
        self.assertIn("### 畫面 00:00", text)
        self.assertIn("../_attachments/abc123/frame_0001.jpg", text)

    def test_missing_picture_is_left_out(self):
        d = self.folder()
        (d / "frames" / "slide_01.jpg").unlink()
        oe.export(d, self.vault)
        text = self.note()
        self.assertIn("## 圖文對照", text)
        self.assertNotIn("slide_01.jpg", text)


class Export(Fixture):
    def test_note_has_properties_links_and_safe_name(self):
        d = self.folder(links="# 連結\n## 已確認\n- [[知識管理]]｜上位概念：主題\n- [[雙向連結|link]]｜互補：機制\n- [[知識管理]]｜舉例：重複\n## 候選\n- [[未確認]]｜舉例：不匯出\n")
        oe.export(d, self.vault)
        md = next((self.vault / "AI").glob("*.md"))
        self.assertEqual(md.name, "測試影片.md")
        text = md.read_text(encoding="utf-8")
        self.assertIn('video_id: "abc123"', text)
        self.assertIn("generated_by: watch-archive", text)
        self.assertEqual(text.count('  - "[[知識管理]]"'), 1)
        self.assertIn('  - "[[雙向連結]]"', text)
        self.assertNotIn('  - "2026"', text)  # purely numeric tags are invalid in Obsidian
        self.assertIn("## 連結", text)
        self.assertIn("- [[知識管理]]｜上位概念：主題", text)
        self.assertNotIn("未確認", text)

    def test_no_links_md_means_no_links_section(self):
        oe.export(self.folder(), self.vault)
        text = next((self.vault / "AI").glob("*.md")).read_text(encoding="utf-8")
        self.assertNotIn("## 連結", text)
        self.assertNotIn("related:", text)

    def test_carousel_gallery_uses_pages_and_with_pages_only_warns(self):
        d = self.folder(carousel=True, cat="AI/claude-code")
        with mock.patch("sys.stderr", new_callable=io.StringIO) as err:
            oe.export(d, self.vault, with_pages=True)
        md = next((self.vault / "AI" / "claude-code").glob("*.md")).read_text(encoding="utf-8")
        self.assertNotIn("圖文原頁", md)
        self.assertIn("### 第 1 頁：第一頁", md)
        self.assertEqual(md.count("_attachments/abc123/slide_01.jpg"), 1)
        self.assertIn("--with-pages", err.getvalue())

    def test_sop_note_copied_with_rewritten_images_and_linked(self):
        oe.export(self.folder(sop=True), self.vault)
        sop = self.vault / "AI" / "測試_操作SOP.md"
        self.assertIn("](../_attachments/abc123/step-0030.jpg)", sop.read_text(encoding="utf-8"))
        self.assertIn("generated_by: watch-archive", sop.read_text(encoding="utf-8"))
        self.assertIn("[[測試_操作SOP]]", (self.vault / "AI" / "測試影片.md").read_text(encoding="utf-8"))

    def test_rerun_keeps_users_files_and_removes_renamed_stale_note(self):
        d = self.folder()
        oe.export(d, self.vault)
        (self.vault / "AI" / "我的筆記.md").write_text("mine", encoding="utf-8")
        (self.vault / "_attachments").mkdir(exist_ok=True)
        (self.vault / "_attachments" / "mine.png").write_bytes(b"x")
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        meta["title"] = "新標題"
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        oe.export(d, self.vault)
        names = sorted(p.name for p in (self.vault / "AI").glob("*.md"))
        self.assertEqual(names, ["我的筆記.md", "新標題.md"])
        self.assertTrue((self.vault / "_attachments" / "mine.png").exists())

    def test_same_title_other_video_does_not_overwrite(self):
        oe.export(self.folder(vid="aaa111"), self.vault)
        oe.export(self.folder(vid="bbb222"), self.vault)
        self.assertEqual(len(list((self.vault / "AI").glob("*.md"))), 2)

    def test_users_note_with_same_name_is_never_overwritten(self):
        (self.vault / "AI").mkdir(parents=True)
        (self.vault / "AI" / "測試影片.md").write_text("mine", encoding="utf-8")
        oe.export(self.folder(), self.vault)
        self.assertEqual((self.vault / "AI" / "測試影片.md").read_text(encoding="utf-8"), "mine")
        self.assertEqual(len(list((self.vault / "AI").glob("*.md"))), 2)

    def test_index_lists_generated_notes_only(self):
        oe.export(self.folder(), self.vault)
        (self.vault / "AI" / "我的筆記.md").write_text("mine", encoding="utf-8")
        oe.write_index(self.vault)
        idx = (self.vault / "00-索引.md").read_text(encoding="utf-8")
        self.assertIn("[[測試影片]]", idx)
        self.assertNotIn("我的筆記", idx)


if __name__ == "__main__":
    unittest.main()


POINTS = """# 知識點
## 已確認
### 連結是在定義關係
- 出處：第 1 頁
- 引文：「第一頁文字」
- 說明：link 不是排版。
- 連結：[[知識管理]]｜上位概念：主題
### 沒填標示的點
- 出處：00:31
- 說明：只有說明。
## 候選
### 還沒確認的點
- 說明：不該匯出
"""


class KnowledgePoints(Fixture):
    def folder(self, **kw):
        kw.setdefault("carousel", True)
        d = super().folder(**kw)
        (d / "transcript.md").write_text("```\n[00:01] 第一頁文字\n```\n", encoding="utf-8")
        (d / "knowledge.md").write_text(POINTS, encoding="utf-8")
        (d / "frames.json").write_text(json.dumps([{"file": "slide_01.jpg", "t": "00:01"}]), encoding="utf-8")
        return d

    def pts(self):
        return self.vault / "知識點"

    def test_only_confirmed_points_become_atomic_notes_with_source_and_default_flag(self):
        oe.export(self.folder(), self.vault)
        names = sorted(p.stem for p in self.pts().glob("*.md"))
        self.assertEqual(names, ["沒填標示的點", "連結是在定義關係"])
        text = (self.pts() / "連結是在定義關係.md").read_text(encoding="utf-8")
        self.assertIn("type: knowledge-point", text)
        self.assertIn("claim: \"講者／作者主張，未查證\"", text)
        self.assertIn("> 「第一頁文字」", text)
        self.assertIn("- [[知識管理]]｜上位概念：主題", text)
        self.assertIn("[[測試影片]]", text)  # provenance link is automatic
        video = (self.vault / "AI" / "測試影片.md").read_text(encoding="utf-8")
        self.assertIn("- [[連結是在定義關係]]", video)
        self.assertIn("status: reviewed", video)
        self.assertNotIn("還沒確認的點", video + "".join(p.read_text(encoding="utf-8") for p in self.pts().glob("*.md")))

    def test_point_carries_its_source_picture_shrunk(self):
        from PIL import Image
        d = self.folder()
        Image.new("RGB", (3000, 2000), (9, 9, 9)).save(d / "frames" / "slide_01.jpg")
        oe.export(d, self.vault)
        text = (self.pts() / "連結是在定義關係.md").read_text(encoding="utf-8")
        self.assertIn("![出處圖](../_attachments/abc123/slide_01.jpg)", text)
        self.assertLessEqual(max(Image.open(self.vault / "_attachments" / "abc123" / "slide_01.jpg").size), oe.IMG_MAX)
        self.assertIn("slide_01.jpg", (self.pts() / "沒填標示的點.md").read_text(encoding="utf-8"))  # 00:31 -> nearest frame

    def test_no_headings_means_all_candidates_and_a_warning(self):
        import contextlib
        import io
        d = self.folder()
        (d / "knowledge.md").write_text("### 沒標分區\n- 說明：x\n", encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            oe.export(d, self.vault)
        self.assertFalse(self.pts().exists() and list(self.pts().glob("*.md")))
        self.assertIn("候選知識點未匯出", err.getvalue())

    def test_unfound_quote_and_link_without_relation_warn(self):
        import contextlib
        import io
        d = self.folder()
        (d / "knowledge.md").write_text(
            "## 已確認\n### 轉述的點\n- 出處：第 1 頁\n- 引文：「原文裡沒有這句」\n- 說明：x\n- 連結：[[概念]]｜沒有冒號\n", encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            oe.export(d, self.vault)
        self.assertIn("找不到，可能是轉述", err.getvalue())
        self.assertIn("缺關係說明", err.getvalue())

    def test_link_without_relation_is_rejected(self):
        c, cand, problems = oe.read_links("## 已確認\n- [[甲]]｜互補：理由\n- [[乙]]\n- [[丙]]｜只有類型\n## 候選\n- [[丁]]｜舉例：待確認\n")
        self.assertEqual(c, [("甲", "互補", "理由")])
        self.assertEqual(cand, [("丁", "舉例", "待確認")])
        self.assertEqual(len(problems), 2)

    def test_index_lists_points_pending_nodes_same_name_and_orphans(self):
        d1 = self.folder(vid="aaa111")
        oe.export(d1, self.vault)
        oe.export(self.folder(vid="bbb222"), self.vault)
        oe.write_index(self.vault)
        idx = (self.vault / "00-索引.md").read_text(encoding="utf-8")
        self.assertIn("## 知識點（4）", idx)
        self.assertIn("同名，待人工合併", idx)
        self.assertIn("## 待建立節點", idx)
        self.assertIn("[[知識管理]]", idx)
        import shutil
        shutil.rmtree(d1)
        oe.write_index(self.vault)
        self.assertIn("來源資料夾已不存在", (self.vault / "00-索引.md").read_text(encoding="utf-8"))

    def test_vault_option_confines_everything_to_watch_archive_subfolder(self):
        mine = self.root / "myvault"
        (mine / "筆記").mkdir(parents=True)
        (mine / "筆記" / "x.md").write_text("mine", encoding="utf-8")
        before = {p for p in mine.rglob("*")}
        oe.export(self.folder(), mine / "watch-archive")
        oe.write_index(mine / "watch-archive")
        new = {p for p in mine.rglob("*")} - before
        self.assertTrue(all("watch-archive" in p.parts for p in new))


class ReviewRegressions(Fixture):
    """Findings of the 2026-10-27 code review."""

    def test_title_up_to_the_limit_is_kept_whole(self):
        title = "【兆華艾綸說】ETF逢低撿 金字塔加碼法 市值、正2、高息型 全都解｜李兆華、艾綸、股魚 2026.10.21 part2"
        oe.export(self.folder(title=title), self.vault)
        self.assertEqual(next((self.vault / "AI").glob("*.md")).stem, title)
        self.assertEqual(oe.NAME_MAX, 100)

    def test_long_titles_equal_in_first_n_chars_do_not_overwrite_each_other(self):
        import contextlib
        import io
        d = self.folder(carousel=True)
        same = "長" * oe.NAME_MAX
        (d / "knowledge.md").write_text(f"## 已確認\n### {same}甲\n- 說明：一\n### {same}乙\n- 說明：二\n", encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            oe.export(d, self.vault)
        self.assertEqual(len(list((self.vault / "知識點").glob("*.md"))), 1)
        self.assertIn("檔名相同", err.getvalue())
        video = next((self.vault / "AI").glob("*.md")).read_text(encoding="utf-8")
        self.assertEqual(video.count(f"- [[{same}]]"), 1)

    def test_users_copy_of_a_generated_note_survives_reexport(self):
        d = self.folder()
        oe.export(d, self.vault)
        src = self.vault / "AI" / "測試影片.md"
        copy = self.vault / "AI" / "測試影片 我的筆記.md"
        copy.write_text(src.read_text(encoding="utf-8") + "\n我加的\n", encoding="utf-8")
        oe.export(d, self.vault)
        self.assertTrue(copy.exists())
        oe.write_index(self.vault)
        self.assertNotIn("我的筆記", (self.vault / "00-索引.md").read_text(encoding="utf-8"))

    def test_users_suffixed_note_is_not_overwritten_either(self):
        (self.vault / "AI").mkdir(parents=True)
        (self.vault / "AI" / "測試影片.md").write_text("mine", encoding="utf-8")
        (self.vault / "AI" / "測試影片 (abc123).md").write_text("mine too", encoding="utf-8")
        oe.export(self.folder(), self.vault)
        self.assertEqual((self.vault / "AI" / "測試影片 (abc123).md").read_text(encoding="utf-8"), "mine too")
        self.assertTrue((self.vault / "AI" / "測試影片 (abc123) 2.md").exists())

    def test_pages_ordered_by_time_not_by_string(self):
        from PIL import Image
        d = self.folder(carousel=True)
        for name in ("a.jpg", "b.jpg"):
            Image.new("RGB", (20, 20)).save(d / "frames" / name)
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        meta["slides"] = [{"start": "00:10", "frame": "b.jpg", "title": "後"}, {"start": "0:05", "frame": "a.jpg", "title": "前"}]
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        oe.export(d, self.vault)
        text = next((self.vault / "AI").glob("*.md")).read_text(encoding="utf-8")
        self.assertIn("### 第 1 頁：前", text)
        self.assertLess(text.index("第 1 頁：前"), text.index("第 2 頁：後"))


class CarouselReport(unittest.TestCase):
    def test_carousel_report_uses_page_headings_and_no_time_range(self):
        import build_report as br
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "2026-10-27_Image_測試__x"
            (d / "frames").mkdir(parents=True)
            Image.new("RGB", (40, 40)).save(d / "frames" / "slide_01.jpg")
            Image.new("RGB", (40, 40)).save(d / "frames" / "slide_02.jpg")
            meta = {"url": "u", "platform": "Image", "title": "測試", "duration": "2 頁（圖文）", "media_type": "carousel",
                    "slides": [{"start": "00:01", "frame": "slide_01.jpg", "title": "甲"},
                               {"start": "00:02", "frame": "slide_02.jpg", "title": "乙"}]}
            (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            (d / "summary.md").write_text("# 摘要\n\n內容\n", encoding="utf-8")
            (d / "transcript.md").write_text("```\n[00:01] 第一頁文字\n[00:02] 第二頁文字\n```\n", encoding="utf-8")
            (d / "frames.json").write_text("[]", encoding="utf-8")
            md = br.build(d)[0].read_text(encoding="utf-8")
        self.assertIn("### 第 1 頁：甲", md)
        self.assertIn("### 第 2 頁：乙", md)
        self.assertIn("第二頁文字", md)
        self.assertNotIn("（00:01", md)
        self.assertIn("- 頁數：2 頁（圖文）", md)


class PointSourceContext(Fixture):
    """知識點的出處連到影片筆記的段落、附 YouTube 時間點，並帶前後 30 秒的逐字稿。"""

    def make(self, url="https://www.youtube.com/watch?v=abc123", platform="YouTube", carousel=False,
             transcript=None, zh=None, supplement="", quote="所以最後四個單位要順勢加碼", source="00:50"):
        d = self.folder(carousel=carousel)
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        starts = ["00:01", "00:02", "00:03"] if carousel else ["00:00", "00:40", "01:30"]
        meta.update(url=url, platform=platform, duration="02:00 (120.0s)",
                    slides=[{"start": s, "frame": "slide_01.jpg", "title": f"第{i + 1}段"} for i, s in enumerate(starts)])
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        if transcript is None:
            transcript = [(f"00:{s:02d}", f"第{s}秒的話") for s in range(0, 60, 2)] + [("00:51", "所以最後四個單位"), ("00:52", "要順勢加碼")]
            transcript.sort()
        (d / "transcript.md").write_text("# t\n\n```\n" + "\n".join(f"[{ts}] {t}" for ts, t in transcript) + "\n```\n", encoding="utf-8")
        if zh:
            (d / "transcript.zh.md").write_text("\n".join(f"[{ts}] {t}" for ts, t in zh) + "\n", encoding="utf-8")
        if supplement:
            (d / "supplement.md").write_text(supplement, encoding="utf-8")
        (d / "knowledge.md").write_text(f"# 知識點\n## 已確認\n### 順勢加碼\n- 出處：{source}\n- 引文：「{quote}」\n- 說明：x\n## 候選\n", encoding="utf-8")
        oe.export(d, self.vault)
        note = next((self.vault / "AI").glob("*.md")).stem
        return note, (self.vault / "知識點" / "順勢加碼.md").read_text(encoding="utf-8")

    def test_source_links_to_the_section_containing_the_time(self):
        note, text = self.make()
        self.assertIn(f"> — [[{note}#主題 2：第2段（00:40–01:30）|00:50]]", text)
        self.assertIn(f"- [[{note}#主題 2：第2段（00:40–01:30）|{note}]]（00:50）", text)
        video = (self.vault / "AI" / f"{note}.md").read_text(encoding="utf-8")
        self.assertIn("### 主題 2：第2段（00:40–01:30）\n", video)

    def test_section_boundaries(self):
        anchors = [(0, "a"), (40, "b"), (90, "c")]
        self.assertEqual(oe.source_section("00:40", anchors, False), 1)
        self.assertEqual(oe.source_section("01:29", anchors, False), 1)
        self.assertEqual(oe.source_section("05:00", anchors, False), 2)
        self.assertEqual(oe.source_section("沒有時間", anchors, False), None)
        self.assertEqual(oe.source_section("00:10", [(30, "a")], False), 0)

    def test_youtube_gets_a_time_link(self):
        _, text = self.make()
        self.assertIn("[▶ 原影片 00:50](https://www.youtube.com/watch?v=abc123&t=50s)", text)
        self.assertEqual(oe.youtube_at("https://youtu.be/abc", 637), "https://youtu.be/abc?t=637s")
        self.assertEqual(oe.youtube_at("https://www.youtube.com/watch?v=x&t=5s", 9), "https://www.youtube.com/watch?v=x&t=9s")

    def test_other_platforms_get_no_time_link(self):
        _, text = self.make(url="https://www.tiktok.com/@a/video/1", platform="TikTok")
        self.assertNotIn("原影片", text)

    def test_context_is_a_collapsed_callout_capped_and_centred(self):
        _, text = self.make()
        self.assertIn("> [!quote]- 前後文（", text)
        rows = [l for l in text.splitlines() if l.startswith("> - ")]
        self.assertEqual(len(rows), oe.CONTEXT_MAX)
        self.assertIn("> - **[00:51] 所以最後四個單位**", text)  # quote across two lines: both bold
        self.assertIn("> - **[00:52] 要順勢加碼**", text)
        self.assertNotIn("[00:10]", text)  # outside ±30 s

    def test_quote_only_in_supplement_has_no_context(self):
        _, text = self.make(quote="畫面上的表格文字", supplement="# 補充\n\n畫面上的表格文字\n")
        self.assertNotIn("[!quote]", text)
        self.assertIn("#主題 2：", text)  # still linked to the section

    def test_foreign_video_context_uses_translation(self):
        zh = [("00:48", "中譯一"), ("00:52", "中譯二")]
        _, text = self.make(transcript=[("00:48", "first"), ("00:52", "second")], zh=zh, quote="second")
        self.assertIn("前後文（中譯）（00:48–00:52）", text)
        self.assertIn("> - [00:48] 中譯一", text)
        self.assertNotIn("first", text.split("[!quote]")[1])

    def test_carousel_page_links_to_page_and_shows_its_text(self):
        transcript = [("00:01", "封面"), ("00:02", "第二頁第一句"), ("00:02", "第二頁第二句"), ("00:03", "第三頁")]
        note, text = self.make(carousel=True, transcript=transcript, quote="第二頁第二句", source="第 2 頁")
        self.assertIn(f"[[{note}#第 2 頁：第2段|第 2 頁]]", text)
        self.assertIn("前後文（第 2 頁）", text)
        self.assertIn("> - **[00:02] 第二頁第二句**", text)
        self.assertNotIn("第三頁", text.split("[!quote]")[1])
        self.assertNotIn("原影片", text)

    def test_section_label_changes_the_link_anchor(self):
        d = self.folder()
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        meta.update(section_label="投影片", slides=[{"start": "00:00", "frame": "slide_01.jpg", "title": "開場"}])
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        (d / "transcript.md").write_text("```\n[00:05] 開場白\n```\n", encoding="utf-8")
        (d / "knowledge.md").write_text("# 知識點\n## 已確認\n### 開場\n- 出處：00:05\n- 引文：「開場白」\n- 說明：x\n## 候選\n", encoding="utf-8")
        oe.export(d, self.vault)
        text = (self.vault / "知識點" / "開場.md").read_text(encoding="utf-8")
        self.assertIn("#投影片 1：開場", text)