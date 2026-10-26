"""Clip window helpers (scripts/clip_check.py). Run: python3 -m unittest discover -s tests -v"""
import json
import sys
import tempfile
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


TRANSCRIPT = "# t\n[00:30] a\n[01:41] 一介螻蟻，萬聖覆援\n[01:57] b\n[10:00] 難清\n[20:00] 無關"


def make_folder(tmp, errors, **meta):
    d = Path(tmp)
    meta = {"url": "http://x", "category": "佛學", "known_asr_errors": errors, **meta}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (d / "transcript.md").write_text(TRANSCRIPT, encoding="utf-8")
    return d


class WaitConfirm(unittest.TestCase):
    def run_wc(self, errors, **meta):
        calls, warns = [], []

        def cut(url, at, before, after, mp3, jpg):
            calls.append((at, before, after))
            mp3.write_bytes(b"")
            jpg.write_bytes(b"")

        with tempfile.TemporaryDirectory() as tmp:
            d = make_folder(tmp, errors, **meta)
            rows = cc.wait_confirm(d, cut=cut, warn=warns.append)
            wc = d / "waitConfirm"
            index = (wc / "index.md").read_text(encoding="utf-8") if (wc / "index.md").exists() else None
            files = sorted(p.name for p in wc.iterdir()) if wc.exists() else []
        return rows, calls, warns, index, files

    def test_only_suspected_single_times_are_cut(self):
        errors = [
            {"time": "01:41", "heard": "螻蟻／覆援", "expected": "螻螘／互援", "status": "suspected"},
            {"time": "10:00", "heard": "難清", "expected": "難侵", "status": "confirmed"},
            {"time": "10:00", "heard": "舊資料", "expected": "x"},
            {"time": "26:52–36:31", "heard": "區間", "expected": "x", "status": "suspected"},
            {"time": "全片", "heard": "全片", "expected": "x", "status": "suspected"},
        ]
        rows, calls, warns, index, files = self.run_wc(errors)
        self.assertEqual(calls, [(101, 5, 25)])
        self.assertEqual(files, ["01_01-41_螻蟻.jpg", "01_01-41_螻蟻.mp3", "index.md"])
        self.assertEqual(len([w for w in warns if "not a single" in w]), 2)
        self.assertIn("一介螻蟻，萬聖覆援", index)
        self.assertIn("[▶ 重聽](./01_01-41_螻蟻.mp3)", index)
        self.assertIn("螻螘／互援", index)

    def test_time_without_transcript_line_is_skipped_with_warning(self):
        errors = [{"time": "05:00", "heard": "沒有", "expected": "x", "status": "suspected"},
                  {"time": "10:00", "heard": "難清", "expected": "難侵", "status": "suspected"}]
        rows, calls, warns, index, files = self.run_wc(errors)
        self.assertEqual([r["heard"] for r in rows], ["難清"])
        self.assertTrue(any("no transcript line" in w for w in warns))
        self.assertIn("01_10-00_難清.mp3", files)

    def test_other_folders_get_no_directory(self):
        rows, calls, warns, index, files = self.run_wc(
            [{"time": "01:41", "heard": "x", "expected": "y", "status": "suspected"}], category="AI")
        self.assertEqual((rows, calls, files), ([], [], []))

    def test_lecture_video_type_counts_outside_佛學(self):
        rows, *_ = self.run_wc(
            [{"time": "01:41", "heard": "x", "expected": "y", "status": "suspected"}], category="AI", video_type="lecture")
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
