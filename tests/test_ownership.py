"""Tests for checks/check_ownership.py. Run: python3 -I tests/test_ownership.py -v

Builds a throwaway git repository for each test.
"""
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "checks"))

import check_ownership  # noqa: E402


def run_main(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = check_ownership.main(list(argv))
    return code, out.getvalue()


class OwnershipTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.org")
        self.git("config", "user.name", "t")
        for name in ("CLAUDE.md", "checks/run_checks.py", "cities/x/notes.md", "ledger/costs.csv"):
            self.write(name, "start\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def tearDown(self):
        shutil.rmtree(self.root)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True, text=True).stdout

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def worktree(self, *extra):
        return run_main("--root", str(self.root), "--worktree", *extra)

    def test_agent_owned_changes_pass(self):
        self.write("cities/x/notes.md", "changed\n")
        self.write("cities/x/claims.yaml", "[]\n")
        self.write("sources/abc.html", "x")
        self.assertEqual(self.worktree()[0], 0)

    def test_each_supervisor_path_fails_in_the_working_tree(self):
        for name in ("CLAUDE.md", "permissions.yaml", "registry.yaml", "checks/new_check.py",
                     "schemas/status.schema.json", ".github/workflows/funnel.yml"):
            with self.subTest(name):
                self.write(name, "changed\n")
                code, out = self.worktree()
                self.assertEqual(code, 1)
                self.assertIn(name, out)
                self.git("add", "-A")
                self.git("reset", "-q", "--hard")
                subprocess.run(["git", "-C", str(self.root), "clean", "-fdq"], check=True)

    def test_a_deleted_protected_file_fails(self):
        (self.root / "CLAUDE.md").unlink()
        self.assertEqual(self.worktree()[0], 1)

    def test_a_rename_out_of_a_protected_directory_fails(self):
        self.git("mv", "checks/run_checks.py", "cities/x/run_checks.py")
        code, out = self.worktree()
        self.assertEqual(code, 1)
        self.assertIn("checks/run_checks.py", out)

    def test_extra_protected_paths_fail(self):
        for name in ("queue/approvals/forged.md", "scripts/fetch_source.py", "PAUSE", ".gitattributes",
                     "templates/dossier.md", "tests/test_ownership.py"):
            with self.subTest(name):
                self.assertEqual(len(check_ownership.violations([name])), 1)

    def test_other_scripts_and_tests_stay_agent_owned(self):
        for name in ("scripts/extract_chicago.py", "tests/test_assess.py", "queue/proposals/p.md",
                     "queue/drafts/x.md", "notebook/2026-11-17.md", "cities/x/status.yaml", "agenda.md"):
            self.assertEqual(check_ownership.violations([name]), [], name)

    def test_the_ledger_is_off_limits_only_to_the_agent(self):
        self.write("ledger/costs.csv", "changed\n")
        self.assertEqual(self.worktree()[0], 0)
        self.assertEqual(self.worktree("--agent-run")[0], 1)

    def test_range_mode_catches_a_committed_change(self):
        self.write("cities/x/notes.md", "ok\n")
        self.write("registry.yaml", "behaviors: {}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "agent")
        code, out = run_main("--root", str(self.root), "--range", self.base, "HEAD")
        self.assertEqual(code, 1)
        self.assertIn("registry.yaml", out)

    def test_range_mode_passes_agent_commits_including_the_ledger(self):
        self.write("cities/x/notes.md", "ok\n")
        self.write("ledger/costs.csv", "row\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "agent")
        self.assertEqual(run_main("--root", str(self.root), "--range", self.base, "HEAD")[0], 0)

    def test_unreadable_repository_is_an_error(self):
        self.assertEqual(run_main("--root", str(self.root / "nope"), "--worktree")[0], 2)


if __name__ == "__main__":
    unittest.main()
