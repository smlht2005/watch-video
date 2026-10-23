"""Subtitle OCR diffing (scripts/subtitle_ocr.py). Run: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import subtitle_ocr as so  # noqa: E402


class MergeEvents(unittest.TestCase):
    def test_similar_neighbours_fold_into_one_event_keeping_longest_read(self):
        ocr = {"0": "觀世音菩薩", "2": "觀世音菩薩圓通", "4": "觀世音菩薩圓通", "6": "完全不同的另一句字幕"}
        ev = so.merge_events(ocr)
        self.assertEqual([(e["start"], e["end"], e["raw"]) for e in ev],
                         [(0, 6, "觀世音菩薩圓通"), (6, 8, "完全不同的另一句字幕")])

    def test_blank_reads_are_skipped_and_split_events(self):
        ev = so.merge_events({"0": "同一句字幕內容", "2": "", "20": "同一句字幕內容"})
        self.assertEqual(len(ev), 2)

    def test_int_keys_work_too(self):
        self.assertEqual(len(so.merge_events({0: "字幕一二三四五"})), 1)


class Transcript(unittest.TestCase):
    def test_parses_mmss_and_hmmss_lines_only(self):
        t = so.parse_transcript("# title\n[01:05] 你好\n[1:02:03] 再見\nnot a line")
        self.assertEqual([(s, b) for s, _, b in t], [(65, "你好"), (3723, "再見")])


class Compare(unittest.TestCase):
    def test_flags_misheard_term_and_passes_matching_line(self):
        lines = so.parse_transcript("[00:00] 耳根遠通最殊勝\n[00:06] 我們繼續往下講")
        events = so.merge_events({"0": "耳根圓通最殊勝", "6": "我們繼續往下講"})
        self.assertEqual(so.compare(lines, events, thr=0.9)[0]["line"], "[00:00] 耳根遠通最殊勝")
        self.assertEqual(len(so.compare(lines, events, thr=0.9)), 1)

    def test_no_subtitle_in_window_is_flagged_with_zero_coverage(self):
        flagged = so.compare(so.parse_transcript("[00:00] 沒有字幕的一句話"), [], thr=0.85)
        self.assertEqual(flagged[0]["coverage"], 0.0)

    def test_punctuation_and_digits_are_ignored(self):
        self.assertEqual(so.coverage("第6卷，開始。", "第六卷開始"), 1.0)


class BandChanged(unittest.TestCase):
    def test_identical_and_first_images(self):
        self.assertTrue(so.band_changed(None, [0, 0]))
        self.assertFalse(so.band_changed([10, 10], [11, 9]))
        self.assertTrue(so.band_changed([0, 0], [255, 255]))


if __name__ == "__main__":
    unittest.main()
