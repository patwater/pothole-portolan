"""Tests for checks/run_checks.py. Run: python3 -I tests/test_checks.py -v

Every fixture is synthetic and built in a temp directory; nothing here is real city data.
"""
import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "checks"))
sys.path.insert(0, str(REPO / "scripts"))

import run_checks  # noqa: E402

CSV = b"district,requests\nNorth,10\nSouth,12\n"
DIGEST = hashlib.sha256(CSV).hexdigest()
ARCHIVE = f"sources/{DIGEST}.csv"

CLAIMS = f"""
- id: testville-311-volume-2025
  statement: "Testville logged 22 pothole service requests in 2025."
  value: 22
  unit: requests
  period: 2025
  kind: reported_demand
  source_url: https://example.org/data
  retrieved: 2026-11-01
  archive: {ARCHIVE}
  method: "Sum of the requests column across districts."
  confidence: supported
  caveats: "Synthetic test fixture."
- id: testville-pci-2024
  statement: "Testville's network-average PCI was 61 in the 2024 survey."
  value: 61
  unit: PCI points
  period: 2024
  kind: measured_condition
  source_url: https://example.org/pci
  retrieved: 2026-11-01
  archive: {ARCHIVE}
  method: "Network average as stated in the report summary table."
  confidence: supported
  caveats: ""
  condition_index:
    name: PCI
    scale: "0-100"
    survey_year: 2024
    network_share_surveyed: 100
    survey_method: "Visual survey"
"""

SOURCES = f"""
- id: testville-portal
  name: Testville open data
  source_type: open_data_portal
  url: https://example.org/data
  status: fetched
  retrieved: 2026-11-01
  archive: {ARCHIVE}
  robots_checked: true
"""

DOSSIER = """---
slug: testville
city: Testville
version: 1
drafted: 2026-11-02
---
# Testville

## Summary

Testville has a published survey and a request portal.

## What the pavement survey measures

The network-average PCI is {{claim:testville-pci-2024}}.

## What residents reported

Residents filed {{claim:testville-311-volume-2025}}. This count does not measure road condition.

## What could not be found

No spending figures were found.
"""


class ChecksTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        city = self.root / "cities" / "testville"
        city.mkdir(parents=True)
        (self.root / "sources").mkdir()
        (self.root / ARCHIVE).write_bytes(CSV)
        (city / "claims.yaml").write_text(CLAIMS)
        (city / "sources.yaml").write_text(SOURCES)
        (city / "dossier.md").write_text(DOSSIER)

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_checks(self, content_only=True):
        return run_checks.run(self.root, ["testville"], content_only)

    def failed(self, name, rep=None):
        rep = rep or self.run_checks()
        return [m for c, _, m in rep.failures if c == name]

    def edit(self, fname, old, new):
        p = self.root / "cities" / "testville" / fname
        text = p.read_text()
        self.assertIn(old, text)
        p.write_text(text.replace(old, new))

    def test_good_city_passes(self):
        rep = self.run_checks()
        self.assertEqual(rep.failures, [])

    def test_missing_retrieved_fails_schema(self):
        self.edit("claims.yaml", "  retrieved: 2026-11-01\n  archive: " + ARCHIVE + "\n  method: \"Sum", "  archive: " + ARCHIVE + "\n  method: \"Sum")
        self.assertTrue(self.failed("schema"))

    def test_missing_archive_file_fails(self):
        (self.root / ARCHIVE).unlink()
        self.assertTrue(self.failed("archives"))

    def test_hash_mismatch_fails(self):
        (self.root / ARCHIVE).write_bytes(CSV + b"tamper\n")
        self.assertTrue(self.failed("archives"))

    def test_archive_not_in_sources_fails(self):
        self.edit("sources.yaml", "status: fetched", "status: listed")
        self.assertTrue(self.failed("provenance") or self.failed("schema"))

    def test_future_retrieval_date_fails(self):
        self.edit("claims.yaml", "retrieved: 2026-11-01\n  archive: " + ARCHIVE + "\n  method: \"Sum", "retrieved: 2999-01-01\n  archive: " + ARCHIVE + "\n  method: \"Sum")
        self.assertTrue(self.failed("provenance"))

    def test_condition_claim_needs_index_block(self):
        self.edit("claims.yaml", "  condition_index:\n    name: PCI\n", "  xcondition_index:\n    name: PCI\n")
        self.assertTrue(self.failed("schema"))

    def test_email_in_dossier_fails(self):
        self.edit("dossier.md", "No spending figures were found.", "Contact jane@example.com about it.")
        self.assertTrue(self.failed("personal_data"))

    def test_street_address_in_dossier_fails(self):
        self.edit("dossier.md", "No spending figures were found.", "A pothole at 123 Main Street was reported.")
        self.assertTrue(self.failed("personal_data"))

    def test_data_file_under_cities_fails(self):
        (self.root / "cities" / "testville" / "raw.csv").write_text("a,b\n1,2\n")
        self.assertTrue(self.failed("personal_data"))

    def test_sensitive_column_in_archive_fails(self):
        bad = b"address,requests\n1 Elm St,3\n"
        digest = hashlib.sha256(bad).hexdigest()
        ref = f"sources/{digest}.csv"
        (self.root / ref).write_bytes(bad)
        for fname in ("claims.yaml", "sources.yaml"):
            self.edit(fname, ARCHIVE, ref)
        self.assertTrue(self.failed("personal_data"))

    def test_demand_statement_with_condition_language_fails(self):
        self.edit("claims.yaml", "Testville logged 22 pothole service requests in 2025.",
                  "Testville roads are in poor condition, with 22 pothole requests.")
        self.assertTrue(self.failed("demand_vs_condition"))

    def test_demand_paragraph_without_disclaimer_fails(self):
        self.edit("dossier.md", "Residents filed {{claim:testville-311-volume-2025}}. This count does not measure road condition.",
                  "Residents filed {{claim:testville-311-volume-2025}}, showing the road condition is poor.")
        self.assertTrue(self.failed("demand_vs_condition"))

    def test_ranking_on_311_fails(self):
        self.edit("dossier.md", "This count does not measure road condition.", "Testville has the highest 311 count.")
        self.assertTrue(self.failed("demand_vs_condition"))

    def test_demand_claim_under_condition_heading_fails(self):
        self.edit("dossier.md", "The network-average PCI is {{claim:testville-pci-2024}}.",
                  "The network-average PCI is {{claim:testville-pci-2024}}. Requests: {{claim:testville-311-volume-2025}}.")
        self.assertTrue(self.failed("demand_vs_condition"))

    def test_speculative_claim_cannot_ship(self):
        self.edit("claims.yaml", "confidence: supported\n  caveats: \"Synthetic", "confidence: speculative\n  caveats: \"Synthetic")
        self.assertTrue(self.failed("dossier"))

    def test_unknown_claim_marker_fails(self):
        self.edit("dossier.md", "{{claim:testville-pci-2024}}", "{{claim:no-such-claim}}")
        self.assertTrue(self.failed("dossier"))

    def test_missing_not_found_section_fails(self):
        self.edit("dossier.md", "## What could not be found", "## Other notes")
        self.assertTrue(self.failed("dossier"))

    def test_phase_zero_blocks_publish(self):
        (self.root / "permissions.yaml").write_text(
            "phase: 0\npublish:\n  agent_may_publish_in_phases: [3, 4]\n")
        self.assertTrue(self.failed("phase_gate", self.run_checks(content_only=False)))

    def test_pause_blocks_publish(self):
        (self.root / "permissions.yaml").write_text(
            "phase: 3\npublish:\n  agent_may_publish_in_phases: [3, 4]\n")
        self.assertEqual(self.failed("phase_gate", self.run_checks(content_only=False)), [])
        (self.root / "PAUSE").write_text("")
        self.assertTrue(self.failed("phase_gate", self.run_checks(content_only=False)))


if __name__ == "__main__":
    unittest.main()
