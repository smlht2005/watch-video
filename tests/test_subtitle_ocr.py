"""Subtitle OCR diffing (scripts/subtitle_ocr.py). Run: python3 -m unittest discover -s tests -v"""
import json
import os
import socket
import sys
import time
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

    def test_rerun_with_different_params_is_refused(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            calls, out, sd = [], Path(d) / "ocr.json", Path(d) / "s"
            segs = [(0, 600)]
            so.run_segmented(out, sd, segs, self.fake_ocr(calls), log=lambda m: None, params={"model": "v4"})
            calls.clear()
            with self.assertRaises(so.PlanMismatch) as cm:
                so.run_segmented(out, sd, segs, self.fake_ocr(calls), log=lambda m: None, params={"model": "v5"})
            self.assertIn("model", str(cm.exception))
            self.assertEqual(calls, [])

    def test_rerun_with_same_params_still_resumes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            calls, out, sd = [], Path(d) / "ocr.json", Path(d) / "s"
            so.run_segmented(out, sd, [(0, 600)], self.fake_ocr(calls), log=lambda m: None, params={"model": "v5"})
            calls.clear()
            so.run_segmented(out, sd, [(0, 600)], self.fake_ocr(calls), log=lambda m: None, params={"model": "v5"})
            self.assertEqual(calls, [])

    def test_plan_without_params_from_an_older_run_is_accepted(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            calls, sd = [], Path(d) / "s"
            sd.mkdir()
            (sd / "plan.json").write_text(json.dumps({"out": "o", "every": 3, "segments": [[0, 600]]}), encoding="utf-8")
            so.run_segmented(Path(d) / "o.json", sd, [(0, 600)], self.fake_ocr(calls), log=lambda m: None,
                             params={"model": "v5"})
            self.assertEqual(calls, [(0, 600)])

    def test_write_atomic_uses_a_tmp_name_per_process(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "x.json"
            with mock.patch("subtitle_ocr.os.replace") as rep:
                so.write_atomic(target, {"a": 1})
            src = str(rep.call_args[0][0])
            self.assertIn(str(os.getpid()), src)
            self.assertTrue(src.endswith(".tmp"))
            so.write_atomic(target, {"a": 1})
            self.assertEqual([f.name for f in Path(d).glob("*.tmp")], [])

    def test_auto_segment_by_length(self):
        self.assertEqual(so.resolve_segment_min(None, 30 * 60), 0)        # exactly 30 min: one pass
        self.assertEqual(so.resolve_segment_min(None, 30 * 60 + 1), so.SEGMENT_MIN)
        self.assertEqual(so.resolve_segment_min(None, 4333), 10)
        self.assertEqual(so.resolve_segment_min(0, 4333), 0)               # explicit 0 turns it off
        self.assertEqual(so.resolve_segment_min(5, 600), 5)                # explicit N is honoured on short videos
        self.assertEqual(so.resolve_segment_min(None, 1900, auto_min=60), 0)


class Progress(unittest.TestCase):
    def run_it(self, d, segs, ocr, **kw):
        lines = []
        so.run_segmented(Path(d) / "o.json", Path(d) / "s", segs, ocr, log=lines.append, **kw)
        return lines

    def test_one_progress_line_per_segment_with_range_and_count(self):
        import re
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            lines = self.run_it(d, [(0, 600), (600, 1200)], lambda a, b: {str(a): "x", str(a + 3): "y"})
            self.assertEqual(len(lines), 2)
            self.assertRegex(lines[0], r"^\[seg 1/2\] 0:00:00-0:10:00 done: 2 samples, \d+s$")
            self.assertRegex(lines[1], r"^\[seg 2/2\] 0:10:00-0:20:00 done: 2 samples, \d+s$")

    def test_skipped_segment_is_reported_as_already_done(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.run_it(d, [(0, 600)], lambda a, b: {"0": "x"})
            self.assertEqual(self.run_it(d, [(0, 600)], lambda a, b: {})[0], "[seg 1/1] 0:00:00-0:10:00 already done, skipping")

    def test_status_without_a_run_says_so(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("no segmented run", so.status_report(Path(d) / "o.json")[0])

    def test_status_partway_lists_running_and_waiting(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d) / "s"

            def ocr(a, b):
                if a == 600:
                    raise RuntimeError("killed")
                return {"0": "x"}
            with self.assertRaises(RuntimeError):
                so.run_segmented(Path(d) / "o.json", sd, [(0, 600), (600, 1200), (1200, 1500)], ocr, log=lambda m: None)
            so.claim_segment(sd, 600)
            lines = so.status_report(Path(d) / "o.json", sd)
            self.assertEqual(lines[0], "1/3 segments done, 2 left")
            self.assertEqual(lines[1], "running: 0:10:00-0:20:00")
            self.assertEqual(lines[2], "waiting: 0:20:00-0:25:00")
            self.assertTrue(lines[3].startswith("last segment finished"))

    def test_status_does_not_call_a_dead_lock_running(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d) / "s"

            def ocr(a, b):
                if a == 600:
                    raise RuntimeError("killed")
                return {"0": "x"}
            with self.assertRaises(RuntimeError):
                so.run_segmented(Path(d) / "o.json", sd, [(0, 600), (600, 1200)], ocr, log=lambda m: None)
            so.lock_path(sd, 600).write_text(json.dumps(
                {"pid": 4194301, "host": socket.gethostname(), "time": time.time()}), encoding="utf-8")
            lines = so.status_report(Path(d) / "o.json", sd)
            self.assertFalse(any(x.startswith("running:") for x in lines))
            self.assertIn("waiting: 0:10:00-0:20:00", lines)

    def test_status_when_finished_says_merged(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.run_it(d, [(0, 600)], lambda a, b: {"0": "x"})
            self.assertEqual(so.status_report(Path(d) / "o.json", Path(d) / "s")[-1], f"all segments done; merged into {Path(d) / 'o.json'}")
            (Path(d) / "o.json").unlink()
            self.assertIn("rerun the same run command", so.status_report(Path(d) / "o.json", Path(d) / "s")[-1])


class Locks(unittest.TestCase):
    def dir(self):
        import tempfile
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return Path(d.name)

    def test_only_one_of_many_simultaneous_claimers_wins(self):
        import threading
        d, results, gate = self.dir(), [], threading.Barrier(8)

        def go():
            gate.wait()
            results.append(so.claim_segment(d, 0))
        threads = [threading.Thread(target=go) for _ in range(8)]
        [x.start() for x in threads]
        [x.join() for x in threads]
        self.assertEqual(results.count(True), 1)

    def test_live_fresh_lock_is_respected(self):
        d = self.dir()
        self.assertTrue(so.claim_segment(d, 0))
        self.assertFalse(so.claim_segment(d, 0))

    def test_lock_older_than_ttl_is_taken_over(self):
        d = self.dir()
        so.lock_path(d, 0).write_text(json.dumps({"pid": 1, "host": "elsewhere", "time": 1000}), encoding="utf-8")
        self.assertFalse(so.claim_segment(d, 0, ttl=60, now=lambda: 1050))
        self.assertTrue(so.claim_segment(d, 0, ttl=60, now=lambda: 1100))

    def test_old_lock_of_a_live_process_on_this_machine_is_respected(self):
        d = self.dir()
        so.claim_segment(d, 0, now=lambda: 1000)
        self.assertFalse(so.claim_segment(d, 0, ttl=60, now=lambda: 10 ** 6, alive=lambda pid: True))

    def test_takeover_never_removes_a_lock_created_in_between(self):
        d, calls = self.dir(), []

        def alive(pid):
            calls.append(pid)
            if len(calls) == 1:   # another process replaces the stale lock with its own live one right after we judged it
                so.lock_path(d, 0).write_text(json.dumps(
                    {"pid": os.getpid(), "host": socket.gethostname(), "time": time.time()}), encoding="utf-8")
                return False
            return True
        so.lock_path(d, 0).write_text(json.dumps(
            {"pid": 1, "host": socket.gethostname(), "time": time.time()}), encoding="utf-8")
        self.assertFalse(so.claim_segment(d, 0, alive=alive))
        self.assertEqual(json.loads(so.lock_path(d, 0).read_text(encoding="utf-8"))["pid"], os.getpid())

    def test_lock_of_a_dead_process_on_this_machine_is_taken_over(self):
        d = self.dir()
        so.claim_segment(d, 0)
        self.assertFalse(so.claim_segment(d, 0, alive=lambda pid: True))
        self.assertTrue(so.claim_segment(d, 0, alive=lambda pid: False))

    def test_lock_from_another_host_is_only_judged_by_age(self):
        d = self.dir()
        so.lock_path(d, 0).write_text(json.dumps({"pid": 1, "host": "elsewhere", "time": 10 ** 12}), encoding="utf-8")
        self.assertFalse(so.claim_segment(d, 0, alive=lambda pid: False))

    def test_garbled_lock_is_stale(self):
        d = self.dir()
        so.lock_path(d, 0).write_text("", encoding="utf-8")
        self.assertTrue(so.claim_segment(d, 0))

    def test_real_pid_check(self):
        self.assertTrue(so.pid_alive(os.getpid()))
        self.assertFalse(so.pid_alive(4194301))

    def test_finished_segment_releases_its_lock(self):
        d = self.dir()
        so.run_segmented(d / "o.json", d / "s", [(0, 600)], lambda a, b: {"0": "x"}, log=lambda m: None)
        self.assertFalse(so.lock_path(d / "s", 0).exists())

    def test_failed_segment_releases_its_lock(self):
        d = self.dir()

        def boom(a, b):
            raise RuntimeError("x")
        with self.assertRaises(RuntimeError):
            so.run_segmented(d / "o.json", d / "s", [(0, 600)], boom, log=lambda m: None)
        self.assertFalse(so.lock_path(d / "s", 0).exists())

    def test_segment_held_by_another_process_is_left_alone_and_nothing_is_merged(self):
        d, calls, lines = self.dir(), [], []
        (d / "s").mkdir()
        self.assertTrue(so.claim_segment(d / "s", 600))        # "another process" holds the second segment
        missing = so.run_segmented(d / "o.json", d / "s", [(0, 600), (600, 1200)],
                                   lambda a, b: calls.append(a) or {"0": "x"}, log=lines.append)
        self.assertEqual((calls, missing), ([0], [600]))
        self.assertFalse((d / "o.json").exists())
        self.assertIn("being run by another process", lines[-1])
        self.assertTrue(so.lock_path(d / "s", 600).exists())   # not released by us

    def test_two_runs_on_the_same_dir_share_the_work(self):
        d, done = self.dir(), []
        segs = [(a, a + 600) for a in range(0, 3000, 600)]

        def second(a, b):
            done.append(("b", a))
            return {str(a): "b"}

        def first(a, b):
            done.append(("a", a))
            if a == 0:   # while the first run is busy with segment 0, a second run starts and works through the rest
                so.run_segmented(d / "o.json", d / "s", segs, second, log=lambda m: None)
            return {str(a): "a"}
        so.run_segmented(d / "o.json", d / "s", segs, first, log=lambda m: None)
        self.assertEqual(sorted(a for _, a in done), [0, 600, 1200, 1800, 2400])   # every segment OCR'd exactly once
        self.assertEqual(len(json.loads((d / "o.json").read_text(encoding="utf-8"))), 5)


class Background(unittest.TestCase):
    def test_child_command_drops_background_and_adds_low_priority(self):
        cmd = so.background_command(["run", "v.mp4", "--out", "o.json", "--background", "--every", "3"], "/x/subtitle_ocr.py")
        self.assertEqual(cmd[1:], ["-u", "/x/subtitle_ocr.py", "run", "v.mp4", "--out", "o.json", "--every", "3", "--low-priority"])
        self.assertNotIn("--background", cmd)

    def test_low_priority_is_not_added_twice(self):
        cmd = so.background_command(["run", "v.mp4", "--low-priority", "--background"], "s.py")
        self.assertEqual(cmd.count("--low-priority"), 1)

    def test_start_background_detaches_and_logs(self):
        import tempfile
        seen = {}

        class FakeProc:
            pid = 4242

        def fake_popen(cmd, **kw):
            seen.update(cmd=cmd, kw=kw)
            return FakeProc()
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "segs" / "progress.log"
            proc = so.start_background(["python", "x"], log, popen=fake_popen)
            self.assertEqual(proc.pid, 4242)
            self.assertTrue(log.exists())                      # log dir and file are created up front
            kw = seen["kw"]
            self.assertEqual(kw["env"]["PYTHONUTF8"], "1")
            if os.name == "nt":
                self.assertTrue(kw["creationflags"] & 0x00000008)   # DETACHED_PROCESS
            else:
                self.assertTrue(kw["start_new_session"])

    @unittest.skipUnless(os.name == "nt", "Windows priority classes")
    def test_apply_low_priority_really_sets_idle_class_on_windows(self):
        import subprocess
        import sys
        code = ("import sys, os, subprocess; sys.path.insert(0, sys.argv[1]); import subtitle_ocr as so; "
                "so.apply_low_priority(); print(subprocess.run(['powershell', '-NoProfile', '-Command', "
                "'(Get-Process -Id %d).PriorityClass' % os.getpid()], capture_output=True, text=True).stdout.strip())")
        out = subprocess.run([sys.executable, "-c", code, str(Path(so.__file__).parent)], capture_output=True, text=True)
        self.assertEqual(out.stdout.strip(), "Idle")

    def run_cli(self, extra, patches):
        import io
        import contextlib
        from unittest import mock
        out = io.StringIO()
        with mock.patch.multiple(so, **patches), contextlib.redirect_stdout(out):
            rc = so.main(["run", "v.mp4", "--out", "o.json"] + extra)
        return rc, out.getvalue()

    def test_background_flag_starts_a_child_and_returns_without_ocr(self):
        from unittest import mock
        started = {}

        class P:
            pid = 7

        def fake_start(cmd, log_path, popen=None):
            started.update(cmd=cmd, log=log_path)
            return P()
        rc, text = self.run_cli(["--background"], {
            "check_video": lambda v: None, "start_background": fake_start, "video_duration": mock.Mock(side_effect=AssertionError("no OCR here")),
            "ocr_range": mock.Mock(side_effect=AssertionError("no OCR here"))})
        self.assertEqual(rc, 0)
        self.assertIn("--low-priority", started["cmd"])
        self.assertNotIn("--background", started["cmd"])
        self.assertEqual(Path(started["log"]).name, "progress.log")
        self.assertIn("status o.json", text)
        self.assertIn("pid 7", text)

    def test_low_priority_flag_lowers_priority_only_when_asked(self):
        from unittest import mock
        calls = []
        patches = {"check_video": lambda v: None, "apply_low_priority": lambda: calls.append(1), "video_duration": lambda v: 60.0,
                   "ocr_range": lambda *a, **k: {"0": "x"}}
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for extra, expected in (([], 0), (["--low-priority"], 1)):
                calls.clear()
                with mock.patch.multiple(so, **patches):
                    so.main(["run", "v.mp4", "--out", str(Path(d) / "o.json")] + extra)
                self.assertEqual(len(calls), expected)


class Power(unittest.TestCase):
    def test_format_power(self):
        self.assertEqual(so.format_power(1, 88), "AC 88%")
        self.assertEqual(so.format_power(0, 62), "battery 62%")
        self.assertEqual(so.format_power(255, 255), "unknown power")
        self.assertEqual(so.format_power(1, 255), "AC")   # desktop without a battery

    def test_power_status_never_raises(self):
        self.assertIsInstance(so.power_status(), str)

    def test_trace_header_and_footer_show_power(self):
        from unittest import mock
        lines = []
        with mock.patch.multiple(so, power_status=lambda: "battery 40%", extract_band=lambda *a, **k: [],
                                 thumbnails=lambda p: []):
            so.ocr_range("v.mp4", 1, 3, "c", "v5", log=lines.append)
        self.assertIn("power battery 40%", lines[0])
        self.assertIn("power battery 40%", lines[-1])


class StageTiming(unittest.TestCase):
    def test_read_text_timed_splits_stages_and_counts_boxes(self):
        import tempfile
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL not installed")

        def engine(path):
            box = lambda x, text: [[[x, 0], [x + 5, 0], [x + 5, 5], [x, 5]], text, 0.9]   # noqa: E731
            return [box(50, "世"), box(0, "觀")], [0.5, 0.0, 1.5]
        with tempfile.TemporaryDirectory() as d:
            png = Path(d) / "a.png"
            Image.new("L", (40, 8)).save(png)
            text, info = so.read_text_timed(engine, png)
        self.assertEqual(text, "觀世")                      # left-to-right
        self.assertEqual((info["det"], info["cls"], info["rec"], info["boxes"]), (0.5, 0.0, 1.5, 2))
        self.assertEqual((info["w"], info["h"]), (40, 8))
        self.assertGreaterEqual(info["other"], 0.0)

    def test_no_text_means_zero_boxes_and_zero_stages(self):
        import tempfile
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("PIL not installed")
        with tempfile.TemporaryDirectory() as d:
            png = Path(d) / "a.png"
            Image.new("L", (10, 4)).save(png)
            text, info = so.read_text_timed(lambda p: (None, None), png)
        self.assertEqual((text, info["boxes"], info["det"], info["rec"]), ("", 0, 0.0, 0.0))

    def test_mean_and_description(self):
        a = {"wall": 4.0, "det": 1.0, "cls": 0.0, "rec": 2.0, "other": 1.0, "boxes": 2, "w": 100, "h": 10}
        b = {"wall": 8.0, "det": 3.0, "cls": 0.0, "rec": 4.0, "other": 1.0, "boxes": 4, "w": 100, "h": 10}
        m = so.mean_info([a, b])
        self.assertEqual((m["wall"], m["det"], m["rec"], m["boxes"]), (6.0, 2.0, 3.0, 3.0))
        self.assertEqual(so.describe_info(m), "6.0s = det 2.0 + cls 0.0 + rec 3.0 + other 1.0, 3.0 boxes, 100x10px")

    def test_slow_image_gets_its_own_trace_line(self):
        from unittest import mock
        slow = {"wall": 20.0, "det": 5.0, "cls": 0.0, "rec": 14.0, "other": 1.0, "boxes": 6, "w": 1050, "h": 130}
        fast = dict(slow, wall=2.0, det=0.5, rec=1.0, other=0.5)

        class Pool:
            def __init__(self, n): pass
            def __enter__(self): return self
            def __exit__(self, *a): return False

            def submit(self, fn, job):
                from concurrent.futures import Future
                f = Future()
                f.set_result((["a"] * len(job[1]), [fast, slow][:len(job[1])]))
                return f
        lines = []
        with mock.patch.multiple(so, extract_band=lambda *a, **k: ["p0", "p1"], thumbnails=lambda p: [[0] * 4, [255] * 4],
                                 ProcessPoolExecutor=Pool):
            so.ocr_range("v.mp4", 1, 3, "c", "v5", start=600, log=lines.append)
        slow_lines = [l for l in lines if "slow image" in l]
        self.assertEqual(len(slow_lines), 1)
        self.assertIn("at 603s", slow_lines[0])
        self.assertIn("rec 14.0", slow_lines[0])
        self.assertTrue(any("avg per image" in l and "slowest 20.0s" in l for l in lines))


class CliChecks(unittest.TestCase):
    def args(self, **kw):
        import argparse
        base = dict(background=False, low_priority=False, segment_min=0, seg_dir=None, video="v.mp4", out="o.json",
                    workers=1, every=3, crop="c", model="v5", start=None, end=None, raw_argv=[])
        return argparse.Namespace(**{**base, **kw})

    def test_negative_segment_min_is_rejected(self):
        import argparse
        with self.assertRaises(argparse.ArgumentTypeError):
            so.segment_min_arg("-5")
        self.assertEqual((so.segment_min_arg("0"), so.segment_min_arg("10")), (0, 10))

    def test_missing_video_stops_before_background_start(self):
        from unittest import mock
        with mock.patch("subtitle_ocr.start_background") as start:
            with self.assertRaises(SystemExit):
                so.cmd_run(self.args(background=True, video="no/such.mp4"))
        start.assert_not_called()

    def test_seg_dir_with_single_pass_warns(self):
        import contextlib
        import io
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            video = Path(d) / "v.mp4"
            video.write_bytes(b"x")
            err = io.StringIO()
            with mock.patch("subtitle_ocr.ocr_range", return_value={}), contextlib.redirect_stderr(err),                     contextlib.redirect_stdout(io.StringIO()):
                so.cmd_run(self.args(video=str(video), out=str(Path(d) / "o.json"), seg_dir="x"))
            self.assertIn("--seg-dir", err.getvalue())
            self.assertIn("ignored", err.getvalue())


class Models(unittest.TestCase):
    def test_default_is_the_mobile_recognizer_and_server_is_still_selectable(self):
        self.assertEqual(so.MODEL_CHOICES[0], "v5")
        self.assertIn("mobile", so.V5_MODELS["v5"][0])
        self.assertIn("monkt", so.V5_MODELS["v5-server"][1])
        for _, _, files in so.V5_MODELS.values():
            self.assertEqual(sorted(files.values()), ["rec_keys_path", "rec_model_path"])

    def test_v4_has_no_downloadable_files(self):
        self.assertNotIn("v4", so.V5_MODELS)


if __name__ == "__main__":
    unittest.main()
