"""Unit tests for language detection and supplement.md handling. Run: python3 -m unittest discover -s tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_report as br  # noqa: E402
import watch_archive as wa  # noqa: E402


class DetectLanguage(unittest.TestCase):
    def test_english(self):
        self.assertEqual(wa.detect_language("[00:01] Welcome to this tutorial on Kind and how clusters work today.\n" * 3), "en")

    def test_chinese(self):
        self.assertEqual(wa.detect_language("[00:01] 如果你的額度常常不到一天就用完了，教你一個隱藏用法。\n" * 3), "zh")

    def test_chinese_with_many_english_terms(self):
        text = "[00:01] 用 kubectl config get-contexts 查看 cluster 與 context，再用 kind create cluster 建立。\n" * 3
        self.assertEqual(wa.detect_language(text), "zh")

    def test_japanese_not_zh(self):
        self.assertEqual(wa.detect_language("[00:01] これはテストです。今日は東京で会議があります。\n" * 5), "ja")

    def test_korean(self):
        self.assertEqual(wa.detect_language("[00:01] 안녕하세요 오늘은 서울에서 회의가 있습니다 감사합니다\n" * 5), "ko")

    def test_too_short_is_unknown(self):
        self.assertEqual(wa.detect_language("[00:00] hi"), "unknown")
        self.assertEqual(wa.detect_language(""), "unknown")

    def test_ignores_timestamps_and_headers(self):
        text = "# 標題標題標題標題標題標題標題標題\n_Source: whisper (groq)._\n```\n[00:01] ok\n```\n"
        self.assertEqual(wa.detect_language(text), "unknown")

    def test_real_japanese_prose_is_ja(self):
        self.assertEqual(wa.detect_language("[00:01] これはテストです。今日は東京で会議があります。\n" * 5), "ja")

    def test_kanji_heavy_japanese_is_left_for_human_check(self):
        # hiragana is only ~9% of the CJK characters: not confident enough for 'ja', must not become 'zh'
        text = "[00:01] 日本国内経済成長率予測発表政府統計調査結果概要説明資料公開である\n" * 3
        self.assertEqual(wa.detect_language(text), "other")

    CHINESE_LINES = ("[00:01] 今天要跟大家分享一個很實用的方法，可以讓你的工作效率提升很多，而且完全不用花錢。\n"
                     "[00:08] 首先打開設定頁面，選擇你需要的功能，接著按照畫面上的步驟一步一步操作就可以了。\n"
                     "[00:15] 最後記得儲存，這樣下次打開的時候就會自動套用，非常方便，大家可以試試看。\n")

    def test_chinese_with_one_japanese_phrase_is_zh(self):
        text = self.CHINESE_LINES + "[00:22] 影片最後講者用日文說了ありがとうございます，謝謝大家的收看。\n"
        self.assertEqual(wa.detect_language(text), "zh")

    def test_chinese_mentioning_japanese_titles_is_zh(self):
        text = self.CHINESE_LINES + "[00:22] 我最喜歡的宮崎駿作品是となりのトトロ和もののけ姫，劇情非常感人，畫面也很美。\n"
        self.assertEqual(wa.detect_language(text), "zh")

    def test_chinese_with_katakana_brands_is_zh(self):
        self.assertEqual(wa.detect_language("[00:01] 今天我們去了東京的ユニクロ和セブンイレブン，買了很多東西回家。\n" * 3), "zh")
        self.assertEqual(wa.detect_language("[00:01] 這台車的外觀很好看，內裝比トヨタ還要精緻，但是價格比トヨタ貴很多。\n" * 3), "zh")

    def test_short_real_chinese_is_unknown_not_other(self):
        self.assertEqual(wa.detect_language("[00:01] 好的謝謝\n"), "unknown")

    def test_repeated_single_word_is_unknown(self):
        self.assertEqual(wa.detect_language("[00:01] ok\n" * 15), "unknown")

    def test_mostly_english_with_little_chinese_is_other(self):
        text = "[00:01] hello world this is some english words and more english text here 中文\n" * 5
        self.assertEqual(wa.detect_language(text), "other")  # too much Chinese for 'en', too little for 'zh'

    def test_balanced_mixed_text_is_zh_by_design(self):
        text = "[00:01] hello world this is some english words and 中文字幾個\n" * 3
        self.assertEqual(wa.detect_language(text), "zh")  # >=10 han characters and >=20% of the units


class LanguagePolicy(unittest.TestCase):
    def test_translation_flag_only_for_en_ja_ko(self):
        for lang, expected in (("en", True), ("ja", True), ("ko", True), ("zh", False), ("other", False), ("unknown", False)):
            self.assertEqual(wa.needs_zh_translation(lang), expected, lang)

    def test_opencc_skipped_for_ja_ko_other(self):
        for lang, expected in (("zh", True), ("unknown", True), ("en", True), ("ja", False), ("ko", False), ("other", False)):
            self.assertEqual(wa.convert_to_traditional(lang), expected, lang)

    def test_opencc_would_really_corrupt_japanese(self):
        if wa._S2T is None:
            self.skipTest("opencc not installed")
        self.assertNotEqual(wa.to_traditional("会議学校"), "会議学校")  # the reason for the ja/ko skip


class SupplementLines(unittest.TestCase):
    def run_sup(self, text):
        d = Path(tempfile.mkdtemp())
        if text is not None:
            (d / "supplement.md").write_text(text, encoding="utf-8")
        return br.supplement_lines(d)

    def test_missing_empty_and_title_only(self):
        self.assertEqual(self.run_sup(None), [])
        self.assertEqual(self.run_sup(""), [])
        self.assertEqual(self.run_sup("# 補充資料\n\n"), [])

    def test_headings_and_fence(self):
        out = self.run_sup("# 補充資料\n\n## S1｜x\n- a\n### 原文\n```\n# in fence\n**b**\n```\n#### deep\ntext\n")
        self.assertEqual(out[0], "## 補充資料（影片未呈現的資訊）")
        self.assertIn("### S1｜x", out)
        self.assertIn("**原文**", out)
        self.assertIn("**deep**", out)
        i = out.index("```")
        self.assertEqual(out[i + 1:i + 3], ["# in fence", "**b**"])  # verbatim, not parsed as heading/bold

    def test_tilde_fence_kept_and_unclosed_fence_closed(self):
        out = self.run_sup("## S1\n~~~\ncode\n")
        self.assertEqual(out.count("~~~"), 2)  # opened as ~~~, closed with ~~~ at the end

    def test_tilde_fence_may_contain_backtick_fence(self):
        out = self.run_sup("## S1\n~~~\n```\ninner\n```\n~~~\nafter\n")
        i = out.index("~~~")
        self.assertEqual(out[i + 1:i + 4], ["```", "inner", "```"])  # inner fence does not close the outer one
        self.assertEqual(out[i + 4], "~~~")
        self.assertIn("after", out)

    def test_first_h1_dropped_even_if_not_named_supplement(self):
        out = self.run_sup("# 別的標題\n\n## S1\nbody\n")
        self.assertNotIn("# 別的標題", "\n".join(out))
        self.assertIn("### S1", out)


class FenceHelpers(unittest.TestCase):
    def test_language_tag_inside_fence_does_not_close_it(self):
        out = Path(tempfile.mkdtemp())
        (out / "supplement.md").write_text("## S1\n```text\n```python\nx = 1\n```\nafter\n", encoding="utf-8")
        lines = br.supplement_lines(out)
        i = lines.index("```")
        self.assertEqual(lines[i + 1:i + 3], ["```python", "x = 1"])
        self.assertEqual(lines[i + 3], "```")  # closed by the bare fence
        self.assertIn("after", lines)

    def test_unclosed_fence_in_summary_is_closed(self):
        md = "intro\n```\ncode with no end\n"
        fixed = br.close_open_fence(md)
        self.assertEqual(fixed.count("```"), 2)
        self.assertEqual(br.close_open_fence("fine\n```\nx\n```"), "fine\n```\nx\n```")

    def test_longer_fence_needs_equal_or_longer_close(self):
        self.assertFalse(br.fence_close("````", "```"))
        self.assertTrue(br.fence_close("````", "````"))
        self.assertTrue(br.fence_close("~~~", "~~~"))
        self.assertFalse(br.fence_close("```", "~~~"))


class DocxFenceAndLinks(unittest.TestCase):
    def build(self, md):
        from docx import Document  # noqa: F401
        d = Path(tempfile.mkdtemp())
        out = d / "t.docx"
        br.md_to_docx(d, md, out)
        from docx import Document as D
        return D(str(out))

    def test_fence_rendered_verbatim_monospace(self):
        doc = self.build("## x\n\n```\n# 模型路由\n- **Fable 5.1**：架構\n```\n")
        texts = [p.text for p in doc.paragraphs]
        self.assertIn("# 模型路由", texts)
        self.assertIn("- **Fable 5.1**：架構", texts)
        self.assertEqual([p.style.name for p in doc.paragraphs if p.text == "# 模型路由"], ["Normal"])  # not a heading

    def test_tilde_fence_in_docx(self):
        doc = self.build("## x\n\n~~~\n# not a heading\n~~~\n")
        self.assertEqual([p.style.name for p in doc.paragraphs if p.text == "# not a heading"], ["Normal"])

    def test_link_label_and_url(self):
        doc = self.build("- [說明](https://example.com/a_(b)) 與 [supplement.md](supplement.md)\n")
        xml = doc.element.xml
        self.assertIn("說明", xml)
        self.assertIn("supplement.md", xml)


if __name__ == "__main__":
    unittest.main()
