"""waitConfirm lines of scripts/review_links.py. Run: python3 -m unittest discover -s tests -v"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import review_links as rl  # noqa: E402


class WaitConfirmLines(unittest.TestCase):
    def test_no_folder_prints_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(rl.wait_confirm_lines(Path(tmp)), [])

    def test_index_gives_absolute_local_path_and_github_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            wc = Path(tmp) / "waitConfirm"
            wc.mkdir()
            (wc / "index.md").write_text("x", encoding="utf-8")
            lines = rl.wait_confirm_lines(Path(tmp))
            index = (wc / "index.md").resolve()
        self.assertEqual(lines[0], f"待確認音檔（本機）: {index}")
        self.assertTrue(Path(lines[0].split(": ", 1)[1]).is_absolute())
        self.assertNotIn("file://", lines[0])
        self.assertIn("GitHub 上看不到", lines[1])

    def test_folder_without_index_warns_and_gives_no_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "waitConfirm").mkdir()
            lines = rl.wait_confirm_lines(Path(tmp))
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].startswith("WARNING:"))
        self.assertNotIn("待確認音檔（本機）", lines[0])


class Gitignore(unittest.TestCase):
    def test_wait_confirm_files_are_ignored(self):
        root = Path(__file__).resolve().parent.parent
        for name in ("index.md", "01_00-05_x.mp3", "01_00-05_x.jpg"):
            path = f"watch-output/佛學/某影片/waitConfirm/{name}"
            run = subprocess.run(["git", "check-ignore", "-q", path], cwd=root)
            self.assertEqual(run.returncode, 0, f"{path} should be gitignored")


if __name__ == "__main__":
    unittest.main()
