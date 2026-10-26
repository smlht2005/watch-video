"""Clip window helpers (scripts/clip_check.py). Run: python3 -m unittest discover -s tests -v"""
import json
import sys
import tempfile
import unittest
from unittest import mock
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


TRANSCRIPT = "# t\n[00:30] a\n[01:41] 一介螻蟻，萬聖覆援\n[01:57] b\n[02:05] 甲一\n[02:20] 乙二\n[03:30] 丙三\n[10:00] 難清\n[20:00] 無關"


def make_folder(tmp, errors, **meta):
    d = Path(tmp)
    meta = {"url": "http://x", "category": "佛學", "known_asr_errors": errors, **meta}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (d / "transcript.md").write_text(TRANSCRIPT, encoding="utf-8")
    return d


class WaitConfirm(unittest.TestCase):
    def run_wc(self, errors, **meta):
        calls, warns = [], []

        def audio(url, start, end, mp3):
            calls.append((start, end))
            mp3.write_bytes(b"")

        self.frame_calls = []

        def frames(url, start, end, items):
            self.frame_calls.append((start, end, [at for at, _ in items]))
            for _, jpg in items:
                jpg.write_bytes(b"")

        with tempfile.TemporaryDirectory() as tmp:
            d = make_folder(tmp, errors, **meta)
            rows = cc.wait_confirm(d, cut_audio=audio, cut_frames=frames, warn=warns.append)
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
        self.assertEqual(calls, [(96, 126)])
        self.assertEqual(files, ["01_01-41_螻蟻.jpg", "01_01-41_螻蟻.mp3", "index.md"])
        self.assertEqual(len([w for w in warns if "not a single" in w]), 2)
        self.assertIn("一介螻蟻，萬聖覆援", index)
        self.assertIn("[▶ 重聽](./01_01-41_螻蟻.mp3)", index)
        self.assertIn("螻螘／互援", index)

    def test_times_within_30_seconds_share_one_clip_chained(self):
        errors = [{"time": t, "heard": h, "expected": "x", "status": "suspected"}
                  for t, h in (("01:41", "一"), ("02:05", "二"), ("02:20", "三"), ("03:30", "四"))]
        rows, calls, warns, index, files = self.run_wc(errors)
        self.assertEqual(calls, [(96, 165), (205, 235)])  # 101->125->140 chain into one clip; 210 alone
        self.assertEqual(sorted(f for f in files if f.endswith(".mp3")), ["01_01-41_一.mp3", "04_03-30_四.mp3"])
        self.assertEqual(len([f for f in files if f.endswith(".jpg")]), 4)
        self.assertEqual([r["offset"] for r in rows], [5, 29, 44, 5])
        self.assertIn("[▶ 重聽](./01_01-41_一.mp3) | 第 44 秒", index)

    def test_failed_download_is_reported_and_other_entries_still_cut(self):
        warns = []

        def audio(url, start, end, mp3):
            if start == 96:
                raise cc.CutError("YouTube 擋下載")
            mp3.write_bytes(b"")

        def frames(url, start, end, items):
            for _, jpg in items:
                jpg.write_bytes(b"")

        errors = [{"time": "01:41", "heard": "一", "expected": "x", "status": "suspected"},
                  {"time": "10:00", "heard": "難清", "expected": "難侵", "status": "suspected"}]
        with tempfile.TemporaryDirectory() as tmp:
            d = make_folder(tmp, errors)
            rows = cc.wait_confirm(d, cut_audio=audio, cut_frames=frames, warn=warns.append)
            index = (d / "waitConfirm" / "index.md").read_text(encoding="utf-8")
            files = sorted(p.name for p in (d / "waitConfirm").iterdir())
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("audio 01:36-02:06 failed: YouTube 擋下載" in w for w in warns))
        self.assertNotIn("01_01-41_一.mp3", index)
        self.assertIn("（下載失敗）", index)
        self.assertIn("[▶ 重聽](./02_10-00_難清.mp3)", index)
        self.assertIn("02_10-00_難清.mp3", files)
        self.assertNotIn("01_01-41_一.mp3", files)

    def test_blocked_youtube_message_has_cookies_hint(self):
        msg = cc.explain_failure("ERROR: Sign in to confirm you're not a bot")
        self.assertIn("WATCH_COOKIES_FROM_BROWSER", msg)
        self.assertIn("WATCH_COOKIES_FILE", msg)
        self.assertIn("WATCH_COOKIES_CONTENT", msg)
        self.assertIn("YouTube 擋下載", msg)
        self.assertNotIn("擋下載", cc.explain_failure("ERROR: Video unavailable"))

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


    def test_screenshots_are_downloaded_once_per_group(self):
        errors = [{"time": t, "heard": h, "expected": "x", "status": "suspected"}
                  for t, h in (("01:41", "一"), ("02:05", "二"), ("02:20", "三"), ("03:30", "四"))]
        self.run_wc(errors)
        self.assertEqual(self.frame_calls, [(100, 142, [101, 125, 140]), (209, 212, [210])])

    def test_failed_frame_only_marks_that_entry(self):
        def audio(url, start, end, mp3):
            mp3.write_bytes(b"")

        def frames(url, start, end, items):
            for at, jpg in items:
                if at != 125:
                    jpg.write_bytes(b"")
            return [125]

        errors = [{"time": t, "heard": h, "expected": "x", "status": "suspected"} for t, h in (("01:41", "一"), ("02:05", "二"))]
        with tempfile.TemporaryDirectory() as tmp:
            d = make_folder(tmp, errors)
            cc.wait_confirm(d, cut_audio=audio, cut_frames=frames, warn=lambda m: None)
            index = (d / "waitConfirm" / "index.md").read_text(encoding="utf-8")
        self.assertEqual(index.count("（下載失敗）"), 1)
        self.assertIn("[截圖](./01_01-41_一.jpg)", index)

    def test_group_is_capped_so_dense_entries_do_not_chain_into_one_huge_clip(self):
        rows = [{"at": 100 + 25 * i} for i in range(10)]  # every 25 s, 225 s in total
        groups = cc.group_rows(rows)
        self.assertGreater(len(groups), 1)
        for g in groups:
            self.assertLessEqual(g[-1]["at"] - g[0]["at"], cc.MAX_GROUP_SPAN)

    def test_rerun_removes_stale_files(self):
        errors = [{"time": "01:41", "heard": "一", "expected": "x", "status": "suspected"}]
        with tempfile.TemporaryDirectory() as tmp:
            d = make_folder(tmp, errors)
            wc = d / "waitConfirm"
            wc.mkdir()
            for name in ("03_10-00_舊.mp3", "03_10-00_舊.jpg", "index.md", "notes.txt"):
                (wc / name).write_bytes(b"")
            cc.wait_confirm(d, cut_audio=lambda *a: None, cut_frames=lambda *a: None, warn=lambda m: None)
            files = sorted(p.name for p in wc.iterdir())
        self.assertEqual(files, ["index.md", "notes.txt"])

    def test_nothing_to_cut_returns_empty_and_main_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = make_folder(tmp, [{"time": "01:41", "heard": "x", "expected": "y"}])  # no status
            with mock.patch("sys.stderr"):
                self.assertEqual(cc.main([str(d), "--wait-confirm"]), 1)
            self.assertFalse((d / "waitConfirm" / "index.md").exists())

    def test_names_are_safe_in_markdown_links(self):
        self.assertEqual(cc.clip_name(1, 41, "大乘起信論(論)#1%[x]"), "01_00-41_大乘起信論論1x")

    def test_missing_url_is_a_clear_error(self):
        errors = [{"time": "01:41", "heard": "一", "expected": "x", "status": "suspected"}]
        with tempfile.TemporaryDirectory() as tmp:
            d = make_folder(tmp, errors)
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            del meta["url"]
            (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(cc.CutError, "沒有 url"):
                cc.wait_confirm(d, cut_audio=lambda *a: None, cut_frames=lambda *a: None, warn=lambda m: None)


class Tools(unittest.TestCase):
    def test_missing_executable_becomes_cut_error(self):
        with self.assertRaisesRegex(cc.CutError, "找不到 no-such-tool-xyz"):
            cc.run_tool(["no-such-tool-xyz"])

    def test_nonzero_exit_becomes_cut_error_with_last_stderr_line(self):
        code = "import sys; sys.stderr.write('boom' + chr(10) + 'real reason'); sys.exit(2)"
        with self.assertRaisesRegex(cc.CutError, "real reason"):
            cc.run_tool([sys.executable, "-c", code])

    def test_auth_args_survives_missing_watch_scripts(self):
        with tempfile.TemporaryDirectory() as tmp,                 mock.patch.object(cc, "WATCH_SCRIPTS", Path(tmp)),                 mock.patch.dict(sys.modules):
            sys.modules.pop("config", None)
            sys.modules.pop("download", None)
            self.assertEqual(cc.auth_args(), [])

    def test_video_format_falls_back_to_muxed_stream(self):
        self.assertIn("/b[height<=720]", cc.VIDEO_FMT)


if __name__ == "__main__":
    unittest.main()
