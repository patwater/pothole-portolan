"""CLAUDE.md keeps the Windows (CRLF) line endings it was supplied with. Run: python3 -I tests/test_line_endings.py

An earlier edit to CLAUDE.md made with a Python script silently rewrote every line to LF, because Python's text
mode converts line endings. The change then showed up in version control as a whole-file rewrite and caused a
merge conflict on every line. This test fails if the file is ever stored with anything other than CRLF, so the
same thing cannot happen unnoticed again.

If the supervisor deliberately moves the file to LF, change this test and the note in docs/cloudflare.md.
"""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

HOW_TO_FIX = (
    "CLAUDE.md must use CRLF line endings on every line. To repair it without changing any wording, run\n"
    "    python3 -I -c \"import pathlib; p = pathlib.Path('CLAUDE.md'); b = p.read_bytes().replace(b'\\r\\n', b'\\n').replace(b'\\n', b'\\r\\n'); p.write_bytes(b)\"\n"
    "To edit the file without changing its endings, use the Edit tool, or in Python read and write with\n"
    "open(path, newline='') so that line endings are not translated."
)


class ClaudeMdLineEndings(unittest.TestCase):
    def test_every_line_ends_in_crlf(self):
        data = (REPO / "CLAUDE.md").read_bytes()
        newlines = data.count(b"\n")
        self.assertGreater(newlines, 0)
        self.assertEqual(data.count(b"\r\n"), newlines, "some lines are not CRLF.\n" + HOW_TO_FIX)

    def test_no_stray_carriage_returns(self):
        data = (REPO / "CLAUDE.md").read_bytes()
        self.assertEqual(data.count(b"\r"), data.count(b"\r\n"), "a carriage return is not part of a CRLF pair.\n" + HOW_TO_FIX)


if __name__ == "__main__":
    unittest.main()
