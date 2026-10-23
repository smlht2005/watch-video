"""Slide-vs-transcript near-miss check (scripts/slide_text_check.py). Run: python3 -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import slide_text_check as stc  # noqa: E402

SUPP = "# 補充\n\n## 蕅祖\n- 不為生死大事，辨幾句名相，以為佛法盡此矣。（蕅祖）\n"


class NearMiss(unittest.TestCase):
    def test_clauses_split_on_punctuation_and_drop_headings(self):
        cs = stc.clauses(SUPP)
        self.assertIn("以為佛法盡此矣", cs)
        self.assertNotIn("補充", cs)

    def test_substituted_char_is_flagged_with_timestamp(self):
        lines = stc.transcript_lines("```\n[09:31] 遍己俱名相以為佛法盡此意\n```")
        hits = stc.find_near_misses(stc.clauses(SUPP), lines)
        self.assertTrue(any(t == "09:31" and c == "以為佛法盡此矣" and w == "以為佛法盡此意"
                            for t, c, w, _ in hits))

    def test_line_already_containing_clause_is_not_flagged(self):
        lines = stc.transcript_lines("[09:31] 以為佛法盡此矣")
        self.assertEqual(stc.find_near_misses(stc.clauses(SUPP), lines), [])


if __name__ == "__main__":
    unittest.main()
