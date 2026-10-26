"""Clip window helpers (scripts/clip_check.py). Run: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import clip_check as cc  # noqa: E402


class Times(unittest.TestCase):
    def test_parse_and_format(self):
        self.assertEqual([cc.parse_ts(t) for t in ("95", "01:35", "1:02:03")], [95, 95, 3723])
        self.assertEqual((cc.fmt(95), cc.fmt(3723)), ("01:35", "1:02:03"))

    def test_window_never_starts_before_zero(self):
        self.assertEqual(cc.window(40, 40, 35), (0, 75))
        self.assertEqual(cc.window(10, 40, 30), (0, 40))


class Lines(unittest.TestCase):
    def test_lines_in_window_give_clip_offsets(self):
        text = "# t\n[00:30] a\n[01:41] 一介螻螘\n[01:57] b\n[02:30] c"
        self.assertEqual(cc.lines_in_window(text, 95, 135), [(101, 6, "一介螻螘"), (117, 22, "b")])


if __name__ == "__main__":
    unittest.main()
