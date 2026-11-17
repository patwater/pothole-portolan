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


class QueryPolicyTest(unittest.TestCase):
    base = "https://data.example.org/resource/vw6y-z8j6.json?"

    def refused(self, query):
        return f.query_policy(self.base + query)

    def test_grouped_count_is_allowed(self):
        q = "$select=service_name,count(*)&$group=service_name&$having=count(*)>=10&$limit=5000"
        self.assertIsNone(self.refused(q))

    def test_non_resource_urls_are_not_affected(self):
        self.assertIsNone(f.query_policy("https://data.example.org/api/views/vw6y-z8j6"))
        self.assertIsNone(f.query_policy("https://www.example.org/page?x=1"))

    def test_sensitive_fields_are_refused_anywhere_in_the_query(self):
        for q in ("$select=address,count(*)&$group=address&$having=count(*)>=10&$limit=10",
                  "$select=count(*)&$group=service_name&$having=count(*)>=10&$where=street='X'&$limit=10",
                  "$select=service_details,count(*)&$group=service_details&$having=count(*)>=10&$limit=10",
                  "$select=lat,long,count(*)&$group=lat,long&$having=count(*)>=10&$limit=10"):
            self.assertIn("sensitive", self.refused(q), q)

    def test_ungrouped_record_query_is_refused(self):
        self.assertIn("aggregate-only", self.refused("$select=service_name&$limit=10"))
        self.assertIn("aggregate-only", self.refused("$select=service_name,count(*)&$limit=10"))

    def test_limit_is_required_and_capped(self):
        self.assertIn("$limit", self.refused("$select=service_name,count(*)&$group=service_name&$having=count(*)>=10"))
        self.assertIn("$limit", self.refused("$select=service_name,count(*)&$group=service_name&$having=count(*)>=10&$limit=999999"))

    def test_plain_filter_parameters_are_refused(self):
        self.assertIn("plain filter", self.refused("service_name=Pothole&$select=count(*)&$group=service_name&$having=count(*)>=10&$limit=5"))

    def test_sensitive_word_inside_a_quoted_literal_is_allowed(self):
        q = "$select=service_name,count(*)&$group=service_name&$having=count(*)>=10&$where=service_name in ('Street Defects','Sidewalk and Curb')&$limit=50"
        self.assertIsNone(self.refused(q))

    def test_sensitive_column_outside_a_literal_is_still_refused(self):
        q = "$select=service_name,count(*)&$group=service_name&$having=count(*)>=10&$where=street='Street Defects'&$limit=50"
        self.assertIn("sensitive", self.refused(q))

    def test_minimum_group_size_is_required(self):
        base = "$select=service_name,count(*)&$group=service_name&$limit=5000"
        self.assertIn("count(*) >=", self.refused(base))
        self.assertIn("count(*) >=", self.refused(base + "&$having=count(*)>=3"))
        self.assertIsNone(self.refused(base + "&$having=count(*)>=10"))
        self.assertIsNone(self.refused(base + "&$having=count(*) >= 25"))

    def test_unknown_dataset_is_refused(self):
        self.assertIn("no query policy", f.query_policy("https://data.example.org/resource/zzzz-9999.json?$limit=5"))

    def test_scorecard_dataset_allows_filtered_reads(self):
        self.assertIsNone(f.query_policy("https://data.example.org/resource/kc49-udxn.json?$select=calendar_month,actual&$where=measure_title like '%25othole%25'&$limit=500"))


class TypedTextGuardTest(unittest.TestCase):
    def body(self, rows):
        return json.dumps(rows).encode()

    def test_controlled_vocabulary_passes(self):
        rows = [{"source": s, "cases": str(i + 10)} for i, s in enumerate(["Phone", "Web", "Mobile"])]
        self.assertEqual(f.typed_text_fields(self.body(rows)), {})

    def test_many_distinct_text_values_are_flagged(self):
        rows = [{"service_subtype": f"Permits for Applicant {i}", "cases": "12"} for i in range(f.MAX_TEXT_DISTINCT + 1)]
        self.assertEqual(f.typed_text_fields(self.body(rows)), {"service_subtype": f.MAX_TEXT_DISTINCT + 1})

    def test_numeric_strings_are_not_text(self):
        rows = [{"year": str(2000 + i), "cases": str(1000 + i)} for i in range(150)]
        self.assertEqual(f.typed_text_fields(self.body(rows)), {})

    def test_exactly_at_the_limit_passes(self):
        rows = [{"agency": f"Queue {i}", "cases": "10"} for i in range(f.MAX_TEXT_DISTINCT)]
        self.assertEqual(f.typed_text_fields(self.body(rows)), {})


class StagedGateTest(unittest.TestCase):
    def write(self, name, content):
        import tempfile
        d = Path(tempfile.mkdtemp())
        p = d / name
        p.write_text(content)
        return p

    def test_typed_text_response_blocks_the_commit(self):
        import staged_gate
        rows = [{"service_subtype": f"Permits for Applicant {i}", "cases": "12"} for i in range(f.MAX_TEXT_DISTINCT + 5)]
        p = self.write("agg.json", json.dumps(rows))
        self.assertTrue(any("typed text" in x for x in staged_gate.gate([p])))

    def test_cached_contents_blocks_the_commit(self):
        import staged_gate
        p = self.write("meta.json", json.dumps({"columns": [{"cachedContents": {"top": []}}]}))
        self.assertTrue(any("cachedContents" in x for x in staged_gate.gate([p])))

    def test_clean_aggregate_passes_and_html_is_skipped(self):
        import staged_gate
        ok = self.write("ok.json", json.dumps([{"source": "Phone", "cases": "30"}, {"source": "Web", "cases": "20"}]))
        html = self.write("page.html", "<p>write to a@b.org</p>")
        self.assertEqual(staged_gate.gate([ok, html]), [])


if __name__ == "__main__":
    unittest.main()
