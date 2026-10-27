"""Tests for scripts/obsidian_export.py. Run: python3 -m unittest discover -s tests -v"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import obsidian_export as oe  # noqa: E402


class Export(unittest.TestCase):
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

    def test_carousel_pages_and_relative_attachments(self):
        oe.export(self.folder(carousel=True, cat="AI/claude-code"), self.vault)
        md = next((self.vault / "AI" / "claude-code").glob("*.md"))
        text = md.read_text(encoding="utf-8")
        self.assertIn("![第 1 頁](../../_attachments/abc123/slide_01.jpg)", text)
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
