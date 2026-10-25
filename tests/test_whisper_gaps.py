"""Refilling silent-looking gaps in API Whisper output. Run: python3 -m unittest discover -s tests -v

Groq's long-form transcription sometimes ends a 30-second window right after a short heading, so the rest of
the window (real speech) never appears; the same 30 seconds sent alone transcribe fine.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".claude/skills/watch/scripts"))
import whisper  # noqa: E402
from transcribe import Segments  # noqa: E402


def segs(*spans, language=""):
    out = Segments(({"start": a, "end": b, "text": t} for a, b, t in spans))
    out.language = language
    return out


class FindGaps(unittest.TestCase):
    def test_gap_between_segments(self):
        self.assertEqual(whisper.find_gaps(segs((0, 2, "a"), (30, 34, "b")), 34), [(2, 30)])

    def test_short_pauses_are_not_gaps(self):
        self.assertEqual(whisper.find_gaps(segs((0, 5, "a"), (12, 20, "b"), (30, 40, "c")), 40), [])

    def test_leading_and_trailing_gaps(self):
        self.assertEqual(whisper.find_gaps(segs((20, 25, "a")), 50), [(0, 20), (25, 50)])

    def test_long_gap_is_split_into_pieces_of_at_most_30s(self):
        self.assertEqual(whisper.find_gaps(segs((0, 1, "a"), (71, 72, "b")), 72), [(1, 31), (31, 61), (61, 71)])

    def test_no_segments_means_whole_audio(self):
        self.assertEqual(whisper.find_gaps(segs(), 40), [(0, 30), (30, 40)])


class FillGaps(unittest.TestCase):
    def test_refilled_segments_are_shifted_and_merged_in_order(self):
        base = segs((0, 2, "標題"), (30, 34, "後面"), language="zh")
        sliced = []

        def slice_audio(start, duration):
            sliced.append((start, duration))
            return f"clip@{start}"

        def transcribe_one(clip):
            self.assertEqual(clip, "clip@2")
            return segs((0, 10, "補回來的前半"), (10, 27, "補回來的後半"))

        out = whisper.fill_gaps(base, [(2, 30)], slice_audio, transcribe_one)
        self.assertEqual(sliced, [(2, 28)])
        self.assertEqual([(s["start"], s["text"]) for s in out],
                         [(0, "標題"), (2, "補回來的前半"), (12, "補回來的後半"), (30, "後面")])
        self.assertEqual(out.language, "zh")

    def test_refill_text_past_the_gap_is_clipped_to_the_gap(self):
        out = whisper.fill_gaps(segs((0, 2, "a"), (30, 34, "b")), [(2, 30)], lambda s, d: "c",
                                lambda c: segs((0, 5, "x"), (29, 31, "past the gap")))
        self.assertEqual([s["text"] for s in out], ["a", "x", "b"])

    def test_failed_refill_is_skipped(self):
        def boom(clip):
            raise SystemExit("network")
        base = segs((0, 2, "a"), (30, 34, "b"))
        out = whisper.fill_gaps(base, [(2, 30)], lambda s, d: "c", boom)
        self.assertEqual([s["text"] for s in out], ["a", "b"])

    def test_no_gaps_returns_input_unchanged(self):
        base = segs((0, 2, "a"))
        self.assertIs(whisper.fill_gaps(base, [], lambda s, d: "c", lambda c: segs()), base)


def talk(start, end, cps=4):
    """A segment of plausible speech density (cps characters per second)."""
    return (start, end, "字" * int((end - start) * cps))


class FindSparseSpans(unittest.TestCase):
    def test_long_segment_with_only_a_heading_is_flagged(self):
        # #12: 07:53-08:21 style — one 28 s segment that kept six characters
        out = whisper.find_sparse_spans(segs(talk(0, 20), (20, 48, "三業不幹壞事"), talk(48, 68)), 68)
        self.assertTrue(any(a <= 30 < b for a, b in out))
        self.assertFalse(any(a <= 5 < b for a, b in out))

    def test_normal_speech_is_not_flagged(self):
        self.assertEqual(whisper.find_sparse_spans(segs(talk(0, 60)), 60), [])

    def test_short_eight_second_hole_inside_speech_is_not_flagged(self):
        self.assertEqual(whisper.find_sparse_spans(segs(talk(0, 26), talk(34, 60)), 60), [])

    def test_prompt_only_segment_is_flagged(self):
        prompt = "阿賴耶識、散善義、敦倫盡分、三業清淨、至誠心、懺悔業障"
        leak = (20, 40, "阿賴耶識散善義敦倫盡分三業清淨至誠心懺悔業障")  # 22 characters = dense enough to pass as speech
        self.assertEqual(whisper.find_sparse_spans(segs(talk(0, 20), leak), 40, prompt=prompt), [(20.0, 40.0)])
        self.assertEqual(whisper.find_sparse_spans(segs(talk(0, 20), leak), 40), [])

    def test_adjacent_sparse_windows_merge_and_tail_under_five_seconds_is_ignored(self):
        self.assertEqual(whisper.find_sparse_spans(segs(talk(0, 20)), 63), [(20.0, 60.0)])
        self.assertEqual(whisper.find_sparse_spans(segs(talk(0, 20)), 23), [])


class FindRefillSpans(unittest.TestCase):
    def test_union_of_holes_and_sparse_windows_cut_into_30s_pieces(self):
        out = whisper.find_refill_spans(segs(talk(0, 20), (20, 40, "標題"), talk(100, 120)), 120)
        self.assertEqual(out, [(20.0, 50.0), (50.0, 80.0), (80.0, 100.0)])

    def test_clean_transcript_has_nothing_to_refill(self):
        self.assertEqual(whisper.find_refill_spans(segs(talk(0, 60)), 60), [])


class LimitRefills(unittest.TestCase):
    def test_failed_chunk_costs_one_so_real_gaps_elsewhere_still_get_budget(self):
        # #13: a 10-minute chunk failed (20 pieces) and must not eat the budget of the 3 later gaps
        chunk = [(i * 30.0, i * 30.0 + 30) for i in range(20)]
        later = [(700.0, 730.0), (800.0, 830.0), (900.0, 930.0)]
        out = whisper.limit_refills(chunk + later, [{"start": 0, "end": 600}], budget=4)
        self.assertEqual(out, chunk + later)

    def test_budget_stops_extra_pieces(self):
        pieces = [(i * 40.0, i * 40.0 + 30) for i in range(5)]
        self.assertEqual(whisper.limit_refills(pieces, [], budget=2), pieces[:2])

    def test_open_ended_chunk_gap(self):
        out = whisper.limit_refills([(100.0, 130.0), (130.0, 160.0)], [{"start": 90, "end": None}], budget=1)
        self.assertEqual(len(out), 2)


class FillGapsUpdate(unittest.TestCase):
    def test_refilled_chunk_is_removed_from_gaps_and_failed_part_stays(self):
        base = segs((0, 2, "a"))
        base.gaps = [{"start": 2, "end": 62}]

        def transcribe_one(clip):
            if clip == "clip@32":
                raise SystemExit("429")
            return segs((0, 5, "補回來的內容很多字"))

        out = whisper.fill_gaps(base, [(2, 32), (32, 62)], lambda s, d: f"clip@{s}", transcribe_one)
        self.assertEqual(out.gaps, [{"start": 32, "end": 62}])
        self.assertEqual([s["text"] for s in out], ["a", "補回來的內容很多字"])

    def test_fully_refilled_chunk_leaves_no_gaps(self):
        base = segs((0, 2, "a"))
        base.gaps = [{"start": 2, "end": 32}]
        out = whisper.fill_gaps(base, [(2, 32)], lambda s, d: "c", lambda c: segs((0, 5, "補回來")))
        self.assertEqual(out.gaps, [])

    def test_sparse_original_is_replaced_but_not_by_a_poorer_refill(self):
        base = segs((20, 40, "標題"))
        richer = whisper.fill_gaps(base, [(20, 40)], lambda s, d: "c", lambda c: segs((0, 10, "補回來的完整內容"), (10, 19, "後半")))
        self.assertEqual([s["text"] for s in richer], ["補回來的完整內容", "後半"])
        poorer = whisper.fill_gaps(base, [(20, 40)], lambda s, d: "c", lambda c: segs((0, 5, "題")))
        self.assertEqual([s["text"] for s in poorer], ["標題"])

    def test_pad_widens_the_slice_but_keeps_only_segments_starting_inside_the_span(self):
        sliced = []

        def slice_audio(start, duration):
            sliced.append((start, duration))
            return "c"

        out = whisper.fill_gaps(segs((0, 2, "a"), (60, 62, "b")), [(30, 60)], slice_audio,
                                lambda c: segs((0, 1, "pre"), (3, 8, "inside"), (33, 34, "post")), pad=2.0)
        self.assertEqual(sliced, [(28.0, 34.0)])
        self.assertEqual([(s["start"], s["text"]) for s in out], [(0, "a"), (31.0, "inside"), (60, "b")])


if __name__ == "__main__":
    unittest.main()
