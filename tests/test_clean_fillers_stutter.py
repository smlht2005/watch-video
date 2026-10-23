"""Stutter merge / pause-space punctuation (scripts/clean_fillers.py) and cross-line check (scripts/stutter_check.py)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import clean_fillers as cf  # noqa: E402
import stutter_check as sc  # noqa: E402


class Stutter(unittest.TestCase):
    def test_inline_stutter_merged(self):
        self.assertEqual(cf.strip_fillers("記得幾則公案以後 逢人 逢人就是談公案"), "記得幾則公案以後，逢人就是談公案")
        self.assertEqual(cf.strip_fillers("指月錄裡面 指月錄裡面很多公案"), "指月錄裡面很多公案")

    def test_adjacent_filler_words_merged(self):
        self.assertEqual(cf.strip_fillers("記得那個那個那個公案"), "記得那個公案")

    def test_distributive_repeat_kept(self):
        self.assertEqual(cf.strip_fillers("一個一個來"), "一個一個來")
        self.assertEqual(cf.strip_fillers("每個 每個人"), "每個，每個人")

    def test_pause_space_becomes_comma(self):
        self.assertEqual(cf.strip_fillers("我們要念佛 求生淨土"), "我們要念佛，求生淨土")

    def test_cross_line_overlap_listed_not_removed(self):
        lines = [("01:00", "離開迷惑"), ("01:03", "離開迷惑 離開煩惱")]
        self.assertEqual(sc.find_overlaps(lines), [("01:00", "01:03", "離開迷惑")])


if __name__ == "__main__":
    unittest.main()
