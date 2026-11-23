import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build_report  # noqa: E402


class CarouselLines(unittest.TestCase):
    def test_each_line_is_its_own_paragraph_or_bullet(self):
        out = build_report.carousel_lines(["標題", "• 父條列：", "○ 子條列一", "○ 子條列二", "• 第二個父條列", "收尾句"])
        self.assertEqual(out, ["標題", "", "- 父條列：", "  - 子條列一", "  - 子條列二", "- 第二個父條列", "", "收尾句", ""])

    def test_nothing_is_joined_or_repunctuated(self):
        out = build_report.carousel_lines(["第一行沒有標點", "第二行"])
        self.assertEqual(out, ["第一行沒有標點", "", "第二行", ""])

    def test_text_lines_uses_it_only_for_carousels(self):
        segs = [("00:01", "甲"), ("00:01", "乙")]
        self.assertEqual(build_report.text_lines({"media_type": "carousel"}, segs, 1, 2), ["甲", "", "乙", ""])
        self.assertEqual(build_report.text_lines({}, segs, 1, 2), ["甲，乙。", ""])


if __name__ == "__main__":
    unittest.main()
