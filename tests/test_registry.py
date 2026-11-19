"""Invariants of registry.yaml and .github/workflows/funnel.yml. Run: python3 -I tests/test_registry.py -v

These pin what the Phase 2 instruction (approval 2026-11-17-001) requires, so a later edit that
quietly breaks one of them fails the loop's own test step.
"""
import re
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import funnel_report  # noqa: E402
import next_behavior  # noqa: E402

REGISTRY = yaml.safe_load((REPO / "registry.yaml").read_text())
WORKFLOW_TEXT = (REPO / ".github" / "workflows" / "funnel.yml").read_text()
WORKFLOW = yaml.safe_load(WORKFLOW_TEXT)
FUNNEL = sorted(set(next_behavior.BEHAVIOR_FOR_STAGE.values()))


class RegistryTest(unittest.TestCase):
    def test_every_funnel_behavior_has_tools_a_turn_limit_a_tier_and_a_prompt(self):
        for name in FUNNEL:
            spec = REGISTRY["behaviors"][name]
            self.assertEqual(spec["trigger"], "funnel", name)
            self.assertTrue(spec["tools"], name)
            self.assertIsInstance(spec["max_turns"], int, name)
            self.assertGreater(spec["max_turns"], 0, name)
            self.assertIn(spec["model_tier"], REGISTRY["model_tiers"], name)
            self.assertTrue(spec["prompt"].strip(), name)

    def test_fetch_may_only_run_the_fetch_script_and_has_no_web_tool(self):
        spec = REGISTRY["behaviors"]["fetch"]
        self.assertEqual(spec["tools"], ["Read", "Bash(python3 -I scripts/fetch_source.py *)"])
        for tool in ("WebFetch", "WebSearch", "Write", "Edit"):
            self.assertNotIn(tool, spec["tools"])
            self.assertIn(tool, spec["deny_tools"])

    def test_no_funnel_behavior_holds_a_write_credential(self):
        for name in FUNNEL:
            self.assertEqual(REGISTRY["behaviors"][name]["credentials"], [], name)
        for name, spec in REGISTRY["behaviors"].items():
            self.assertFalse([c for c in spec["credentials"] if "WRITE" in c], name)

    def test_publish_cannot_call_blygger_in_phase_two(self):
        tools = " ".join(REGISTRY["behaviors"]["publish"]["tools"])
        self.assertNotIn("blygger", tools.lower())
        self.assertNotIn("WebFetch", tools)

    def test_every_stage_behavior_is_in_the_registry(self):
        for name in FUNNEL:
            self.assertIn(name, REGISTRY["behaviors"])

    def test_the_run_limit_is_eight(self):
        self.assertEqual(REGISTRY["funnel"]["max_behaviors_per_run"], 8)

    def test_permissions_are_phase_two_and_keep_the_cap_key(self):
        perm = yaml.safe_load((REPO / "permissions.yaml").read_text())
        self.assertEqual(perm["phase"], 2)
        self.assertIn("daily_cap_usd", perm["spend"])
        self.assertEqual(perm["publish"]["agent_may_publish_in_phases"], [3, 4])


class WorkflowTest(unittest.TestCase):
    def test_it_runs_on_a_schedule_twice_a_week_and_on_demand(self):
        on = WORKFLOW[True]  # YAML reads the key `on` as True
        crons = [item["cron"] for item in on["schedule"]]
        self.assertEqual(crons, REGISTRY["funnel"]["cron"])
        for cron in crons:
            self.assertRegex(cron, r"^\d+ \d+ \* \* [0-6]$")
            self.assertNotEqual(cron.split()[0], "0")
        self.assertIn("workflow_dispatch", on)
        self.assertNotIn("pull_request", on)
        self.assertNotIn("push", on)

    def test_runs_never_overlap_and_a_running_one_is_not_cancelled(self):
        self.assertEqual(WORKFLOW["concurrency"], {"group": "funnel", "cancel-in-progress": False})

    def test_pause_is_checked_right_after_checkout_and_gates_every_later_step(self):
        steps = WORKFLOW["jobs"]["funnel"]["steps"]
        self.assertEqual(steps[1]["id"], "pause")
        for step in steps[2:]:
            if step.get("name") == "Fail the run if the loop failed":
                self.assertIn("steps.loop.outcome == 'failure'", step["if"])  # a skipped loop is never a failure
                continue
            self.assertIn("steps.pause.outputs.paused", step.get("if", ""), step.get("name", step.get("uses")))

    def test_checkout_uses_lfs_and_leaves_no_credentials_for_the_agent(self):
        with_ = WORKFLOW["jobs"]["funnel"]["steps"][0]["with"]
        self.assertIs(with_["lfs"], True)
        self.assertIs(with_["persist-credentials"], False)

    def test_the_token_is_only_in_the_push_and_issue_steps(self):
        for step in WORKFLOW["jobs"]["funnel"]["steps"]:
            env = step.get("env", {})
            has_token = any("github.token" in str(v) for v in env.values())
            self.assertEqual(has_token, step.get("name") in ("Guard file ownership, then push", "Update the summary issue"),
                             step.get("name"))
        loop = next(s for s in WORKFLOW["jobs"]["funnel"]["steps"] if s.get("id") == "loop")
        self.assertEqual(list(loop["env"]), ["ANTHROPIC_API_KEY"])
        self.assertIn("secrets.ANTHROPIC_API_KEY", loop["env"]["ANTHROPIC_API_KEY"])

    def test_the_ownership_guard_runs_before_the_push_from_the_trusted_snapshot(self):
        push = next(s for s in WORKFLOW["jobs"]["funnel"]["steps"] if s.get("id") == "push")["run"]
        self.assertLess(push.index("check_ownership.py"), push.index("git push"))
        self.assertIn("$TRUSTED/checks/check_ownership.py", push)
        self.assertLess(push.index("git rebase"), push.index("check_ownership.py"))
        for path in ("CLAUDE.md", "permissions.yaml", "registry.yaml", "checks/", "schemas/", ".github/"):
            self.assertIn(path, WORKFLOW_TEXT)

    def test_the_loop_is_not_the_only_thing_that_runs_after_it_fails(self):
        steps = {s.get("name"): s for s in WORKFLOW["jobs"]["funnel"]["steps"]}
        self.assertIs(steps["Run the funnel loop"]["continue-on-error"], True)
        for name in ("Guard file ownership, then push", "Update the summary issue", "Fail the run if the loop failed"):
            self.assertIn("always()", steps[name]["if"])

    def test_actions_are_pinned_to_the_majors_in_their_documentation_and_the_cli_to_a_version(self):
        for use in re.findall(r"uses: (\S+)", WORKFLOW_TEXT):
            self.assertRegex(use, r"^actions/[a-z-]+@v7$")
        self.assertRegex(WORKFLOW["env"]["CLAUDE_CODE_VERSION"], r"^\d+\.\d+\.\d+$")

    def test_it_asks_for_no_more_than_contents_and_issues_write(self):
        self.assertEqual(WORKFLOW["permissions"], {"contents": "write", "issues": "write"})

    def test_the_issue_title_matches_the_report_script(self):
        self.assertIn(f'--title "{funnel_report.TITLE}"', WORKFLOW_TEXT)
        self.assertIn(funnel_report.LABEL, WORKFLOW_TEXT)


if __name__ == "__main__":
    unittest.main()
