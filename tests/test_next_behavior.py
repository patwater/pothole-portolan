"""Tests for scripts/next_behavior.py. Run: python3 -I tests/test_next_behavior.py -v

Fixtures are synthetic and built in a temp directory.
"""
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import next_behavior  # noqa: E402

AGENDA = """# Agenda

## Proposed pilot cities (Phase 1)

| Order | Slug |
|---|---|
| 1 | not-this-one |

## Queue

1. alpha: status `assessed`
2. beta: status `proposed`
3. gamma: status `proposed`

## Research questions

1. delta: not a queue entry
"""


class NextBehaviorTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "agenda.md").write_text(AGENDA)
        (self.root / "cities").mkdir()
        (self.root / "queue" / "approvals").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.root)

    def status(self, slug, stage, blocked=None):
        d = self.root / "cities" / slug
        d.mkdir(parents=True, exist_ok=True)
        block = "null" if blocked is None else (
            f"\n  type: {blocked[0]}\n  ref: {blocked[1]}\n  note: waiting")
        (d / "status.yaml").write_text(
            f"stage: {stage}\nblocked_on: {block}\nlast_run: null\n")

    def approval(self, name, resolves):
        (self.root / "queue" / "approvals" / name).write_text(
            f"---\nid: x\nresolves: {json.dumps(resolves)}\n---\nbody\n")

    def pick(self):
        return next_behavior.pick(self.root)[0]

    def test_agenda_reads_only_the_queue_section(self):
        self.assertEqual(next_behavior.agenda_cities(self.root), ["alpha", "beta", "gamma"])

    def test_each_stage_maps_to_its_behavior(self):
        for stage, behavior in next_behavior.BEHAVIOR_FOR_STAGE.items():
            self.status("alpha", stage)
            self.assertEqual(self.pick(), {"city": "alpha", "behavior": behavior, "stage": stage})

    def test_city_without_folder_starts_with_scout(self):
        self.status("alpha", "queued")
        self.assertEqual(self.pick()["city"], "beta")
        self.assertEqual(self.pick()["behavior"], "scout")

    def test_first_city_with_work_wins_in_agenda_order(self):
        self.status("alpha", "fetched")
        self.status("beta", "assessed")
        self.assertEqual(self.pick()["city"], "alpha")

    def test_queued_and_published_have_no_work(self):
        self.status("alpha", "queued")
        self.status("beta", "published")
        self.status("gamma", "published")
        choice, skipped = next_behavior.pick(self.root)
        self.assertIsNone(choice)
        self.assertEqual(len(skipped), 3)

    def test_city_blocked_on_proposal_is_skipped(self):
        self.status("alpha", "assessed", ("proposal", "2026-01-01-001"))
        self.assertEqual(self.pick()["city"], "beta")

    def test_proposal_block_clears_when_an_approval_resolves_it(self):
        self.status("alpha", "assessed", ("proposal", "2026-01-01-001"))
        self.approval("a.md", ["2026-01-01-001"])
        self.assertEqual(self.pick()["city"], "alpha")
        self.assertEqual(self.pick()["behavior"], "draft")

    def test_an_approval_for_a_different_proposal_does_not_clear_it(self):
        self.status("alpha", "assessed", ("proposal", "2026-01-01-001"))
        self.approval("a.md", ["2026-01-01-002"])
        self.assertEqual(self.pick()["city"], "beta")

    def test_other_block_types_are_never_cleared_by_an_approval(self):
        self.status("alpha", "assessed", ("supervisor", "2026-01-01-001"))
        self.approval("a.md", ["2026-01-01-001"])
        self.assertEqual(self.pick()["city"], "beta")

    def test_nothing_to_do_prints_the_phrase(self):
        for slug in ("alpha", "beta", "gamma"):
            self.status(slug, "queued")
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(next_behavior.main(["--root", str(self.root)]), 0)
        self.assertEqual(out.getvalue().strip(), "nothing to do")

    def test_cli_prints_city_and_behavior(self):
        self.status("alpha", "extracted")
        out = io.StringIO()
        with redirect_stdout(out):
            next_behavior.main(["--root", str(self.root)])
        self.assertEqual(out.getvalue().strip(), "alpha assess")

    def test_folder_without_status_is_an_error_not_a_guess(self):
        (self.root / "cities" / "alpha").mkdir()
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(next_behavior.main(["--root", str(self.root)]), 2)
        self.assertIn("no status.yaml", err.getvalue())

    def test_invalid_status_is_an_error(self):
        d = self.root / "cities" / "alpha"
        d.mkdir()
        (d / "status.yaml").write_text("stage: nonsense\nblocked_on: null\nlast_run: null\n")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(next_behavior.main(["--root", str(self.root)]), 2)

    def test_every_city_folder_in_the_repository_has_a_valid_status_file(self):
        for slug in (p.name for p in (REPO / "cities").iterdir() if p.is_dir()):
            self.assertIsNotNone(next_behavior.load_status(REPO, slug), slug)


if __name__ == "__main__":
    unittest.main()
