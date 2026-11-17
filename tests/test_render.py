"""Tests for scripts/render_dossier.py. Run: python3 -I tests/test_render.py -v

Fixtures are synthetic and built in a temp directory.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import render_dossier  # noqa: E402

REF = "sources/" + "a" * 64 + ".csv"
CLAIM = """
- id: {id}
  statement: "Testville logged {n} requests in {year}."
  value: {n}
  unit: requests
  period: {year}
  kind: reported_demand
  source_url: https://example.org/data
  retrieved: 2026-11-01
  archive: {ref}
  method: "Count of rows for the year."
  confidence: supported
  caveats: "Counts reports, not road condition."
"""
SOURCES = f"""
- id: portal
  name: Testville open data
  source_type: open_data_portal
  url: https://example.org/data
  status: fetched
  retrieved: 2026-11-01
  archive: {REF}
  robots_checked: true
- id: audit
  name: Testville audit
  source_type: audit
  url: https://example.org/audit.pdf
  status: unavailable
  retrieved: 2026-11-02
  notes: "Disallowed by robots.txt."
- id: faq
  name: Testville FAQ
  source_type: agency_page
  url: https://example.org/faq
  status: listed
"""
DOSSIER = """---
slug: testville
city: Testville
version: 1
drafted: 2026-11-02
---
# Testville

## What residents reported

Residents filed {{claim:tv-2024}} in 2024 and {{claim:tv-2025}} in 2025. Again {{claim:tv-2024}}.

## What could not be found

The audit.

## Sources

<!-- generated -->
"""


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        city = self.root / "cities" / "testville"
        city.mkdir(parents=True)
        (city / "claims.yaml").write_text(CLAIM.format(id="tv-2024", n=1200, year=2024, ref=REF) + CLAIM.format(id="tv-2025", n=1350, year=2025, ref=REF))
        (city / "sources.yaml").write_text(SOURCES)
        (city / "dossier.md").write_text(DOSSIER)

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_markers_become_values_with_footnotes(self):
        out = render_dossier.render(self.root, "testville")
        self.assertIn("1,200 requests[^1]", out)
        self.assertIn("1,350 requests[^2]", out)
        self.assertEqual(out.count("1,200 requests[^1]"), 2, "a repeated claim reuses its footnote number")
        self.assertNotIn("{{claim", out)

    def test_footnote_carries_source_date_archive_method_and_caveats(self):
        out = render_dossier.render(self.root, "testville")
        note = next(line for line in out.splitlines() if line.startswith("[^1]:"))
        for piece in ("https://example.org/data", "retrieved 2026-11-01", REF, "Method: Count of rows for the year.", "Caveats: Counts reports, not road condition."):
            self.assertIn(piece, note)

    def test_repeated_method_and_caveats_point_to_the_first_note(self):
        out = render_dossier.render(self.root, "testville")
        note2 = next(line for line in out.splitlines() if line.startswith("[^2]:"))
        self.assertIn("Method: same as note [^1].", note2)
        self.assertIn("Caveats: same as note [^1].", note2)
        self.assertNotIn("Counts reports", note2)

    def test_sources_section_lists_fetched_unavailable_and_listed(self):
        out = render_dossier.render(self.root, "testville")
        section = out.split("## Sources", 1)[1]
        self.assertIn(f"Testville open data. <https://example.org/data>, retrieved 2026-11-01, archived copy `{REF}`", section)
        self.assertIn("Testville audit. <https://example.org/audit.pdf>, not retrieved", section)
        self.assertIn("Testville FAQ. <https://example.org/faq>, listed and not yet retrieved", section)
        self.assertNotIn("generated", out)

    def test_unknown_claim_id_stops_the_render(self):
        p = self.root / "cities" / "testville" / "dossier.md"
        p.write_text(DOSSIER.replace("tv-2025", "no-such-claim"))
        with self.assertRaises(SystemExit) as cm:
            render_dossier.render(self.root, "testville")
        self.assertIn("no-such-claim", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
