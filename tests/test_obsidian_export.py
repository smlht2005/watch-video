"""Tests for scripts/obsidian_export.py. Run: python3 -m unittest discover -s tests -v"""
import json
import sys
import tempfile
import unittest
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

    def test_carousel_pages_only_with_flag_and_relative_attachments(self):
        d = self.folder(carousel=True, cat="AI/claude-code")
        oe.export(d, self.vault)
        md = next((self.vault / "AI" / "claude-code").glob("*.md"))
        self.assertNotIn("圖文原頁", md.read_text(encoding="utf-8"))
        self.assertFalse((self.vault / "_attachments" / "abc123" / "slide_01.jpg").exists())
        oe.export(d, self.vault, with_pages=True)
        self.assertIn("![第 1 頁](../../_attachments/abc123/slide_01.jpg)", md.read_text(encoding="utf-8"))
        self.assertTrue((self.vault / "_attachments" / "abc123" / "slide_01.jpg").exists())

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

    def test_long_titles_equal_in_first_60_chars_do_not_overwrite_each_other(self):
        import contextlib
        import io
        d = self.folder(carousel=True)
        same = "長" * 60
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
        oe.export(d, self.vault, with_pages=True)
        text = next((self.vault / "AI").glob("*.md")).read_text(encoding="utf-8")
        self.assertIn("**第 1 頁：前**", text)


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
