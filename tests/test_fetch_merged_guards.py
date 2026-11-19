"""The two fetch guards together. Run: python3 -I -m unittest discover -s tests -p "test_*.py"

The scheduled-funnel branch added a host-level aggregate-only guard (aggregate_violation, reduce_body). The
pilot branch added a per-dataset policy (query_policy: minimum group size, scoped fields), a typed-text
response guard and a generic metadata sanitizer. These tests cover how the merged module combines them.
All network access is stubbed and every fixture is synthetic.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import fetch_source as f  # noqa: E402

SF = "https://data.sf.gov/resource/vw6y-z8j6.json?"
SCORE = "https://data.sfgov.org/resource/kc49-udxn.json?"
GOOD = "$select=service_name,count(*)%20as%20cases&$where=lower(service_subtype)%3D'pavement_defect'&$group=service_name&$having=count(*)%3E%3D10&$limit=5000"


def both(url):
    """What run() applies to a URL on a restricted host."""
    return f.aggregate_violation(url) or f.query_policy(url)


class GuardsTogether(unittest.TestCase):
    def test_a_grouped_query_with_the_group_size_minimum_passes_both(self):
        self.assertIsNone(both(SF + GOOD))

    def test_the_host_guard_alone_would_accept_a_query_without_the_minimum_so_the_policy_must_refuse_it(self):
        q = "$select=service_name,count(*)&$group=service_name&$limit=100"
        self.assertIsNone(f.aggregate_violation(SF + q))
        self.assertIn("count(*) >=", f.query_policy(SF + q))
        self.assertIn("count(*) >=", both(SF + q))

    def test_having_is_an_allowed_parameter_on_the_host_guard(self):
        self.assertNotIn("not allowed", f.aggregate_violation(SF + GOOD) or "")

    def test_registered_datasets_may_use_their_policys_limit_and_unregistered_ones_may_not(self):
        q = "$select=service_name,count(*)&$group=service_name&$limit=5000"
        self.assertIsNone(f.aggregate_violation(SF + q))
        other = "https://data.sf.gov/resource/zzzz-9999.json?" + q
        self.assertIn("$limit", f.aggregate_violation(other))
        self.assertIn("no query policy", both("https://data.sf.gov/resource/zzzz-9999.json?$select=count(*)&$group=a&$limit=5"))

    def test_the_scorecard_dataset_allows_plain_row_reads_but_the_311_dataset_does_not(self):
        rows = "$select=measure_code,calendar_month,actual&$where=measure_code='7075'&$limit=500"
        self.assertIsNone(both(SCORE + rows))
        self.assertIn("aggregate query needs", both(SF + rows))

    def test_the_scorecard_dataset_is_still_capped_at_its_policys_limit(self):
        self.assertIn("$limit", both(SCORE + "$select=actual&$limit=999999"))

    def test_metadata_endpoints_are_the_same_with_or_without_the_json_suffix(self):
        for u in ("https://data.sf.gov/api/views/vw6y-z8j6", "https://data.sf.gov/api/views/vw6y-z8j6.json",
                  "https://data.sf.gov/api/views/vw6y-z8j6/columns.json"):
            self.assertIsNone(both(u), u)

    def test_row_downloads_are_still_refused(self):
        for u in ("https://data.sf.gov/api/views/vw6y-z8j6/rows.csv", "https://data.sf.gov/api/v3/views/vw6y-z8j6/export.csv",
                  "https://data.sf.gov/resource/vw6y-z8j6.csv"):
            self.assertTrue(both(u), u)

    def test_service_details_needs_the_subtype_scope_through_the_whole_stack(self):
        q = "$select=service_details,count(*)&$group=service_details&$having=count(*)%3E%3D10&$limit=100"
        self.assertIn("service_details may only", both(SF + q))
        self.assertIsNone(both(SF + q + "&$where=lower(service_subtype)%3D'pavement_defect'"))

    def test_every_recorded_san_francisco_source_passes_both_guards(self):
        path = REPO / "cities" / "san-francisco" / "sources.yaml"
        if not path.is_file():
            self.skipTest("no San Francisco sources")
        for s in yaml.safe_load(path.read_text()):
            host = f.urllib.parse.urlsplit(s["url"]).hostname
            if host in f.AGGREGATE_ONLY_HOSTS:
                self.assertIsNone(both(s["url"]), s["id"])


class RunEndToEnd(unittest.TestCase):
    """run() with the network stubbed."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "cities" / "testcity").mkdir(parents=True)

    def list_source(self, url, sid="q1"):
        (self.root / "cities" / "testcity" / "sources.yaml").write_text(yaml.safe_dump([
            {"id": sid, "name": "Synthetic query", "source_type": "open_data_portal", "url": url, "status": "listed"}]))

    def run_with(self, body, url, ctype="application/json"):
        self.list_source(url)
        with mock.patch.object(f, "fetch", return_value=(body, url, ctype, 200)), \
                mock.patch.object(f, "robots_allows", return_value=(True, "robots.txt read")), \
                mock.patch.object(f.time, "sleep"):
            f.run(self.root, "testcity", set(), 0, 20)
        entry = yaml.safe_load((self.root / "cities" / "testcity" / "sources.yaml").read_text())[0]
        archive = [p.name for p in (self.root / "sources").glob("*")] if (self.root / "sources").exists() else []
        return entry, archive

    def test_a_typed_text_response_is_held_and_never_written_to_disk(self):
        rows = [{"service_subtype": f"Permits for Applicant {i}", "cases": "12"} for i in range(f.MAX_TEXT_DISTINCT + 5)]
        entry, archive = self.run_with(json.dumps(rows).encode(), SF + GOOD)
        self.assertEqual(entry["status"], "unavailable")
        self.assertIn("typed text", entry["notes"])
        self.assertEqual(archive, [])

    def test_a_clean_aggregate_is_archived(self):
        rows = [{"service_name": "Street Defects", "cases": "86753"}, {"service_name": "Sidewalk and Curb", "cases": "6960"}]
        entry, archive = self.run_with(json.dumps(rows).encode(), SF + GOOD)
        self.assertEqual(entry["status"], "fetched")
        self.assertEqual(len(archive), 1)
        self.assertEqual(entry["archive"], "sources/" + archive[0])

    def test_a_query_the_policy_refuses_is_recorded_as_unavailable_with_the_reason_and_not_fetched(self):
        q = SF + "$select=service_name,count(*)&$group=service_name&$limit=100"
        self.list_source(q)
        with mock.patch.object(f, "fetch") as fetch, mock.patch.object(f, "robots_allows", return_value=(True, "")), mock.patch.object(f.time, "sleep"):
            f.run(self.root, "testcity", set(), 0, 20)
        fetch.assert_not_called()
        entry = yaml.safe_load((self.root / "cities" / "testcity" / "sources.yaml").read_text())[0]
        self.assertEqual(entry["status"], "unavailable")
        self.assertIn("count(*) >=", entry["notes"])

    def test_metadata_with_value_samples_is_archived_without_them(self):
        meta = {"name": "Dataset", "columns": [{"fieldName": "address", "cachedContents": {"top": [{"item": "1 Example St"}]}}]}
        entry, archive = self.run_with(json.dumps(meta).encode(), "https://data.sf.gov/api/views/vw6y-z8j6")
        self.assertEqual(entry["status"], "fetched")
        text = (self.root / entry["archive"]).read_text()
        self.assertNotIn("cachedContents", text)
        self.assertNotIn("Example St", text)

    def test_metadata_samples_are_also_removed_on_a_host_the_funnel_does_not_restrict(self):
        meta = {"columns": [{"fieldName": "a", "cachedContents": {"top": [{"item": "secret value"}]}}]}
        entry, _ = self.run_with(json.dumps(meta).encode(), "https://data.example.org/api/views/abcd-1234")
        self.assertEqual(entry["status"], "fetched")
        self.assertNotIn("secret value", (self.root / entry["archive"]).read_text())


if __name__ == "__main__":
    unittest.main()
