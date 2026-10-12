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


if __name__ == "__main__":
    unittest.main()
