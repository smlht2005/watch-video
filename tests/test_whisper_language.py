"""Whisper-reported language handling. Run: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / ".claude/skills/watch/scripts"))
import transcribe  # noqa: E402
import watch_archive as wa  # noqa: E402
import whisper  # noqa: E402


class NormalizeWhisperLanguage(unittest.TestCase):
    def test_names_and_codes(self):
        for raw, expected in (("english", "en"), ("English", "en"), ("Chinese", "zh"), ("cantonese", "zh"),
                              ("japanese", "ja"), ("korean", "ko"), ("en", "en"), ("zh-TW", "zh"), ("spanish", "es"),
                              ("  ", ""), ("", ""), ("dutch", "nl"), ("haitian creole", "ht"), ("Haitian_Creole", "ht"),
                              ("yue", "zh"), ("zh_tw", "zh"), ("chinese (traditional)", "zh"),
                              ("nn", ""), ("nynorsk", ""), ("123", ""), ("klingon", "")):
            self.assertEqual(wa.normalize_whisper_language(raw), expected, raw)


class ResolveLanguage(unittest.TestCase):
    ENGLISH_TEXT = "[00:01] Welcome to this tutorial on Kind and how clusters work today.\n" * 3
    CHINESE_TEXT = "[00:01] 如果你的額度常常不到一天就用完了，教你一個隱藏用法。\n" * 3

    def test_whisper_language_wins_over_text_heuristic(self):
        # the text looks Chinese, but Whisper said Japanese: trust Whisper
        self.assertEqual(wa.resolve_language(self.CHINESE_TEXT, "japanese"), ("ja", "whisper (text: zh)"))  # Whisper wins, the clash is flagged

    def test_captions_without_whisper_language_use_heuristic(self):
        self.assertEqual(wa.resolve_language(self.ENGLISH_TEXT, ""), ("en", "heuristic"))

    def test_forced_lang_ignores_whisper_echo(self):
        lang, source = wa.resolve_language(self.CHINESE_TEXT, "chinese", forced="zh")
        self.assertEqual(lang, "zh")
        self.assertIn("forced", source)

    def test_empty_transcript_is_unknown_even_if_whisper_reports_a_language(self):
        self.assertEqual(wa.resolve_language("", "english"), ("unknown", "heuristic"))
        self.assertEqual(wa.resolve_language("# t\n_Source: whisper (groq)._\n```\n```\n", "english")[0], "unknown")

    def test_unreliable_or_unparseable_whisper_language_falls_back_to_text(self):
        for raw in ("nn", "123", "klingon"):
            self.assertEqual(wa.resolve_language(self.ENGLISH_TEXT, raw), ("en", "heuristic"), raw)

    def test_conflict_between_whisper_and_text_is_flagged_not_hidden(self):
        lang, source = wa.resolve_language(self.CHINESE_TEXT, "english")  # e.g. an English song at the start
        self.assertEqual(lang, "en")
        self.assertEqual(source, "whisper (text: zh)")
        self.assertEqual(wa.resolve_language(self.ENGLISH_TEXT, "spanish"), ("es", "whisper"))  # Latin vs Latin: no conflict

    def test_yue_counts_as_chinese(self):
        self.assertEqual(wa.resolve_language(self.CHINESE_TEXT, "yue"), ("zh", "whisper"))

    def test_environment_language_counts_as_forced(self):
        self.assertEqual(wa.forced_language("", {"WATCH_WHISPER_LANGUAGE": "zh"}), "zh")
        self.assertEqual(wa.forced_language("en", {"WATCH_WHISPER_LANGUAGE": "zh"}), "en")
        self.assertEqual(wa.forced_language("", {}), "")

    def test_whisper_language_line_matches_report_header_format(self):
        report = "# watch: video report\n\n- **Source:** https://x\n- **Duration:** 00:42 (42.1s)\n- **Whisper language:** chinese\n\n## Transcript\n"
        self.assertEqual(wa.field(report, "Whisper language"), "chinese")
        self.assertEqual(wa.field("- **Duration:** 00:42\n", "Whisper language"), "")

    def test_translation_flag_for_any_known_non_chinese_language(self):
        for lang, expected in (("en", True), ("ja", True), ("es", True), ("zh", False), ("other", False), ("unknown", False)):
            self.assertEqual(wa.needs_zh_translation(lang), expected, lang)


class SegmentsCarryLanguage(unittest.TestCase):
    def test_normalize_segments_keeps_language(self):
        data = {"language": "English", "segments": [{"start": 0, "end": 1, "text": "hi there"}]}
        self.assertEqual(transcribe.normalize_segments(data).language, "english")

    def test_missing_or_bad_language_is_empty(self):
        for lang in (None, 5, ""):
            data = {"language": lang, "segments": [{"start": 0, "end": 1, "text": "x"}]}
            self.assertEqual(transcribe.normalize_segments(data).language, "")

    def test_chunks_use_most_common_language(self):
        def fake(path):
            seg = transcribe.Segments([{"start": 0.0, "end": 1.0, "text": "t"}])
            seg.language = {"a": "english", "b": "english", "c": "chinese"}[path.name]
            return seg
        chunks = [(Path("a"), 0.0), (Path("b"), 10.0), (Path("c"), 20.0)]
        self.assertEqual(whisper.transcribe_chunks(chunks, fake).language, "english")

    def test_tie_is_deterministic_and_silent_chunks_do_not_vote(self):
        def fake(path):
            seg = transcribe.Segments([{"start": 0.0, "end": 1.0, "text": "t"}] if path.name != "s" else [])
            seg.language = {"a": "english", "b": "chinese", "s": "korean"}[path.name]
            return seg
        chunks = [(Path("a"), 0.0), (Path("s"), 10.0), (Path("b"), 20.0)]
        for _ in range(5):  # the winner must not depend on hash order; a tie keeps the earliest chunk's language
            self.assertEqual(whisper.transcribe_chunks(chunks, fake).language, "english")


if __name__ == "__main__":
    unittest.main()
