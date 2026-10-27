"""Subtitle OCR diffing (scripts/subtitle_ocr.py). Run: python3 -m unittest discover -s tests -v"""
import json
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


class FixMisreads(unittest.TestCase):
    def test_v4_look_alike_misreads_are_repaired(self):
        out = so.fix_misreads({"0": "罪生平等", "2": "筱座起", "4": "菩隆摩訶隆"})
        self.assertEqual(out, {"0": "眾生平等", "2": "從座起", "4": "菩薩摩訶隆"})

    def test_legitimate_words_are_left_alone(self):
        self.assertEqual(so.fix_misreads({"0": "编織起來"}), {"0": "编織起來"})


class Segments(unittest.TestCase):
    EVERY = 3

    def fake_ocr(self, calls):
        def ocr(a, b):
            calls.append((a, b))
            return {str(t): f"t{t}" for t in range(a, b, self.EVERY)}
        return ocr

    def test_plan_covers_the_video_with_a_short_last_segment(self):
        self.assertEqual(so.plan_segments(1500, 10, self.EVERY), [(0, 600), (600, 1200), (1200, 1500)])

    def test_plan_respects_start_and_end(self):
        self.assertEqual(so.plan_segments(4000, 10, self.EVERY, start=300, end=1300), [(300, 900), (900, 1300)])

    def test_segment_length_is_a_multiple_of_every(self):
        self.assertEqual(so.plan_segments(2000, 10, 7)[0], (0, 595))   # 600 s rounded down to a multiple of 7

    def test_merge_equals_a_single_pass(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            calls, out = [], Path(d) / "ocr.json"
            segs = so.plan_segments(1500, 10, self.EVERY)
            self.assertEqual(so.run_segmented(out, Path(d) / "s", segs, self.fake_ocr(calls), log=lambda m: None), [])
            merged = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(merged, {str(t): f"t{t}" for t in range(0, 1500, self.EVERY)})
            self.assertEqual(list(merged), sorted(merged, key=int))

    def test_rerun_skips_finished_segments(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            calls, out, sd = [], Path(d) / "ocr.json", Path(d) / "s"
            segs = so.plan_segments(1500, 10, self.EVERY)
            so.run_segmented(out, sd, segs, self.fake_ocr(calls), log=lambda m: None)
            so.seg_path(sd, 600).unlink()
            out.unlink()
            calls.clear()
            so.run_segmented(out, sd, segs, self.fake_ocr(calls), log=lambda m: None)
            self.assertEqual(calls, [(600, 1200)])
            self.assertTrue(out.exists())

    def test_tmp_file_is_not_a_finished_segment(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            calls, sd = [], Path(d) / "s"
            sd.mkdir()
            Path(str(so.seg_path(sd, 0)) + ".tmp").write_text("{half", encoding="utf-8")
            so.run_segmented(Path(d) / "o.json", sd, [(0, 600)], self.fake_ocr(calls), log=lambda m: None)
            self.assertEqual(calls, [(0, 600)])

    def test_missing_segment_means_no_merged_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "o.json"
            segs = [(0, 600), (600, 1200)]


            def ocr(a, b):
                if a == 600:
                    raise RuntimeError("killed")
                return {"0": "x"}
            with self.assertRaises(RuntimeError):
                so.run_segmented(out, Path(d) / "s", segs, ocr, log=lambda m: None)
            self.assertFalse(out.exists())
            self.assertTrue(so.seg_path(Path(d) / "s", 0).exists())

    def test_auto_segment_by_length(self):
        self.assertEqual(so.resolve_segment_min(None, 30 * 60), 0)        # exactly 30 min: one pass
        self.assertEqual(so.resolve_segment_min(None, 30 * 60 + 1), so.SEGMENT_MIN)
        self.assertEqual(so.resolve_segment_min(None, 4333), 10)
        self.assertEqual(so.resolve_segment_min(0, 4333), 0)               # explicit 0 turns it off
        self.assertEqual(so.resolve_segment_min(5, 600), 5)                # explicit N is honoured on short videos
        self.assertEqual(so.resolve_segment_min(None, 1900, auto_min=60), 0)


if __name__ == "__main__":
    unittest.main()
