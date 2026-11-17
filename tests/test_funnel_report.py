"""Tests for scripts/funnel_report.py. Run: python3 -I tests/test_funnel_report.py -v"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import funnel_report as fr  # noqa: E402


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        for d in ("queue/drafts", "queue/proposals", "queue/approvals", "cities/a", "cities/b"):
            (self.root / d).mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_nothing_waiting_says_none(self):
        (self.root / "cities/a/status.yaml").write_text("stage: queued\nblocked_on: null\nlast_run: null\n")
        (self.root / "cities/b/status.yaml").write_text("stage: scouted\nblocked_on: null\nlast_run: null\n")
        body = fr.render_body(self.root, {"daily_cap_usd": 5.0, "spend_today_usd": 1.5})
        self.assertEqual(body.count("- none"), 3)
        self.assertIn("Daily cap $5.00; spent so far today $1.50", body)

    def test_drafts_open_proposals_and_blocked_cities_are_listed(self):
        (self.root / "queue/drafts/a-v1.md").write_text("d")
        (self.root / "queue/drafts/.gitkeep").write_text("")
        (self.root / "queue/proposals/p1.md").write_text("---\nid: 2026-01-01-001\n---\n")
        (self.root / "queue/proposals/p2.md").write_text("---\nid: 2026-01-01-002\n---\n")
        (self.root / "queue/approvals/x.md").write_text("---\nid: x\nresolves: [2026-01-01-002]\n---\n")
        (self.root / "cities/a/status.yaml").write_text(
            "stage: assessed\nblocked_on:\n  type: run_failure\n  ref: r1\n  note: tests failed\nlast_run: null\n")
        (self.root / "cities/b/status.yaml").write_text("stage: scouted\nblocked_on: null\nlast_run: null\n")
        w = fr.waiting(self.root)
        self.assertEqual(w["drafts"], ["a-v1.md"])
        self.assertEqual(w["proposals"], ["p1.md"])
        self.assertEqual(w["blocked"], ["a: run_failure r1. tests failed"])

    def test_a_null_cap_is_called_out(self):
        (self.root / "cities/a/status.yaml").write_text("stage: scouted\nblocked_on: null\nlast_run: null\n")
        (self.root / "cities/b/status.yaml").write_text("stage: scouted\nblocked_on: null\nlast_run: null\n")
        self.assertIn("**null**", fr.render_body(self.root, {"daily_cap_usd": None}))

    def test_comment_reports_what_ran_and_what_it_cost(self):
        summary = {"outcome": "failed", "message": "fetch on a: boom", "date": "2026-11-20", "run_id": "42",
                   "run_url": "https://example.org/run/42", "run_cost_usd": 0.75, "spend_today_usd": 0.75,
                   "steps": [{"n": 1, "behavior": "fetch", "city": "a", "outcome": "failed", "stage_before": "discovered",
                              "stage_after": None, "turns": 4, "cost_usd": 0.75, "detail": "tests failed:\nboom"}]}
        text = fr.render_comment(summary)
        for needle in ("run 42", "discovered to discovered", "$0.7500", "tests failed", "Workflow run: https://example.org/run/42"):
            self.assertIn(needle, text)

    def test_a_skipped_run_still_gets_a_comment(self):
        text = fr.render_comment({"outcome": "cap_unset", "message": "m", "steps": [], "run_cost_usd": 0, "spend_today_usd": 0})
        self.assertIn("still null", text)


if __name__ == "__main__":
    unittest.main()
