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
                              ("  ", ""), ("", ""), ("klingon", "klingon")):
            self.assertEqual(wa.normalize_whisper_language(raw), expected, raw)


class ResolveLanguage(unittest.TestCase):
    ENGLISH_TEXT = "[00:01] Welcome to this tutorial on Kind and how clusters work today.\n" * 3
    CHINESE_TEXT = "[00:01] 如果你的額度常常不到一天就用完了，教你一個隱藏用法。\n" * 3

    def test_whisper_language_wins_over_text_heuristic(self):
        # the text looks Chinese, but Whisper said Japanese: trust Whisper
        self.assertEqual(wa.resolve_language(self.CHINESE_TEXT, "japanese"), ("ja", "whisper"))

    def test_captions_without_whisper_language_use_heuristic(self):
        self.assertEqual(wa.resolve_language(self.ENGLISH_TEXT, ""), ("en", "heuristic"))

    def test_forced_lang_ignores_whisper_echo(self):
        lang, source = wa.resolve_language(self.CHINESE_TEXT, "chinese", forced="zh")
        self.assertEqual(lang, "zh")
        self.assertIn("forced", source)

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


if __name__ == "__main__":
    unittest.main()
