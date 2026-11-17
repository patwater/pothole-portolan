"""Tests for the rule 7 sanitizer in scripts/fetch_source.py. Run: python3 -I tests/test_fetch.py -v"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import fetch_source as f  # noqa: E402

VIEWS = "https://data.example.org/api/views/abcd-1234"


class SanitizeTest(unittest.TestCase):
    def body(self):
        return json.dumps({
            "name": "311 Cases",
            "columns": [
                {"fieldName": "address", "cachedContents": {"top": [{"item": "1 Example St", "count": 9}]}},
                {"fieldName": "service_name", "description": "Type of request", "cachedContents": {"top": [{"item": "x"}]}},
            ],
            "nested": {"deep": [{"cachedContents": {"top": [{"item": "jane@example.com"}]}}]},
        }).encode()

    def test_cached_contents_removed_everywhere(self):
        out, note = f.sanitize(VIEWS, "application/json", self.body())
        text = out.decode()
        self.assertNotIn("cachedContents", text)
        self.assertNotIn("Example St", text)
        self.assertNotIn("jane@example.com", text)
        self.assertIn("3", note)

    def test_names_and_descriptions_survive(self):
        out, _ = f.sanitize(VIEWS, "application/json; charset=utf-8", self.body())
        data = json.loads(out)
        self.assertEqual([c["fieldName"] for c in data["columns"]], ["address", "service_name"])
        self.assertEqual(data["columns"][1]["description"], "Type of request")

    def test_output_is_deterministic(self):
        a, _ = f.sanitize(VIEWS, "application/json", self.body())
        b, _ = f.sanitize(VIEWS, "application/json", self.body())
        self.assertEqual(a, b)

    def test_other_urls_and_types_are_untouched(self):
        body = self.body()
        self.assertEqual(f.sanitize("https://data.example.org/resource/abcd-1234.json", "application/json", body), (body, None))
        self.assertEqual(f.sanitize(VIEWS, "text/html", body), (body, None))

    def test_invalid_json_raises_so_it_is_not_archived(self):
        with self.assertRaises(ValueError):
            f.sanitize(VIEWS, "application/json", b"not json")


if __name__ == "__main__":
    unittest.main()
