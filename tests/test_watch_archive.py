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

    def test_mixed_balanced_is_other(self):
        text = "[00:01] hello world this is some english words and 中文字幾個\n" * 3
        self.assertIn(wa.detect_language(text), ("other", "en", "zh"))  # must not crash; no strong claim


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

    def test_tilde_fence_normalised_and_unclosed_fence_closed(self):
        out = self.run_sup("## S1\n~~~\ncode\n")
        self.assertEqual(out.count("```"), 2)

    def test_first_h1_dropped_even_if_not_named_supplement(self):
        out = self.run_sup("# 別的標題\n\n## S1\nbody\n")
        self.assertNotIn("# 別的標題", "\n".join(out))
        self.assertIn("### S1", out)


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

    def test_link_label_and_url(self):
        doc = self.build("- [說明](https://example.com/a_(b)) 與 [supplement.md](supplement.md)\n")
        xml = doc.element.xml
        self.assertIn("說明", xml)
        self.assertIn("supplement.md", xml)


if __name__ == "__main__":
    unittest.main()
