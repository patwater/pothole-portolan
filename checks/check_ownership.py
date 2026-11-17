#!/usr/bin/env python3
"""Fail when a diff touches a path the scheduled agent may not change.

Supervisor-owned (CLAUDE.md rule 5 and the Phase 2 instruction, approval 2026-11-17-001):
  CLAUDE.md, permissions.yaml, registry.yaml, checks/, schemas/, .github/

Also protected, because the loop runs them or they decide what the loop trusts. Each is a
deliberate addition to the supervisor's list, and the reason is in docs/automation.md:
  templates/ (changing the dossier template needs the supervisor, CLAUDE.md),
  queue/approvals/ (supervisor decisions; a forged one could unblock a city), PAUSE,
  .gitattributes (Git LFS rules), the fetcher, selector, validator, loop, report and
  Blygger client, scripts/requirements.txt, and the tests for all of those.

With --agent-run, ledger/costs.csv is also off limits, because the workflow appends it.

Modes:
  --worktree          changes in the working tree against HEAD, untracked files included
  --range A B         files changed between commits A and B (git diff A B)

Run it from a snapshot taken before any agent ran, so an agent cannot edit the guard
and then be judged by the edited copy.

Usage: python3 -I checks/check_ownership.py [--root DIR] [--agent-run] (--worktree | --range A B)
Exit 0 when clean, 1 on violations, 2 when git cannot be read.
"""
import argparse
import subprocess
import sys

SUPERVISOR_OWNED = [
    "CLAUDE.md", "permissions.yaml", "registry.yaml", "checks/", "schemas/", ".github/",
]
ALSO_PROTECTED = [
    "templates/", "queue/approvals/", "PAUSE", ".gitattributes",
    "scripts/fetch_source.py", "scripts/next_behavior.py", "scripts/validate.py",
    "scripts/funnel_loop.py", "scripts/funnel_report.py", "scripts/requirements.txt",
    "scripts/blygger_client/",
    "tests/test_checks.py", "tests/test_next_behavior.py", "tests/test_fetch_source.py",
    "tests/test_funnel_loop.py", "tests/test_funnel_report.py", "tests/test_ownership.py",
    "tests/test_registry.py",
]
AGENT_RUN_ONLY = ["ledger/costs.csv"]


def normalize(path):
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def violations(paths, agent_run=False):
    """Return [(path, rule)] for every path under a protected entry."""
    rules = SUPERVISOR_OWNED + ALSO_PROTECTED + (AGENT_RUN_ONLY if agent_run else [])
    found = []
    for raw in paths:
        path = normalize(raw)
        for rule in rules:
            if path == rule or (rule.endswith("/") and path.startswith(rule)):
                found.append((path, rule))
                break
    return found


def git(root, *args):
    done = subprocess.run(["git", "-C", root, *args], capture_output=True)
    if done.returncode != 0:
        raise RuntimeError(done.stderr.decode(errors="replace").strip() or f"git {args[0]} failed")
    return done.stdout


def worktree_paths(root):
    """Every path with a staged, unstaged or untracked change, both sides of a rename."""
    out = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").decode("utf-8", "replace")
    parts = out.split("\0")
    paths, i = [], 0
    while i < len(parts):
        entry = parts[i]
        i += 1
        if len(entry) < 4:
            continue
        status, path = entry[:2], entry[3:]
        paths.append(path)
        if "R" in status or "C" in status:  # the original path follows as its own token
            if i < len(parts) and parts[i]:
                paths.append(parts[i])
            i += 1
    return paths


def range_paths(root, a, b):
    out = git(root, "diff", "--name-only", "--no-renames", "-z", a, b).decode("utf-8", "replace")
    return [p for p in out.split("\0") if p]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--agent-run", action="store_true")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--worktree", action="store_true")
    mode.add_argument("--range", nargs=2, metavar=("A", "B"))
    args = ap.parse_args(argv)
    try:
        paths = worktree_paths(args.root) if args.worktree else range_paths(args.root, *args.range)
    except RuntimeError as exc:
        print(f"ownership: cannot read git state: {exc}")
        return 2
    bad = violations(paths, args.agent_run)
    for path, rule in bad:
        print(f"OWNERSHIP  {path} is protected ({rule})")
    print(f"ownership: {len(paths)} changed path(s), {len(bad)} violation(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
