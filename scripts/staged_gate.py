#!/usr/bin/env python3
"""Blocking pre-commit gate for archived data. Exit status 1 means: do not commit.

Run before every commit that adds files under sources/, and chain the commit behind it with && so a
failure stops it. It fails on:
  - an archived JSON response from a portal /resource/ query with a text field that has too many
    distinct values (possible typed text), the same guard the fetcher applies;
  - an archived JSON/CSV file that still contains `cachedContents` sample values;
  - an email, phone number or street address anywhere in a staged archive under sources/ that is
    JSON or CSV (HTML and PDF pages are reviewed by hand, as the checklist says).

Usage: python3 -I scripts/staged_gate.py [--root DIR] [paths...]   (default: files staged in git under sources/)
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "checks"))
import fetch_source as f  # noqa: E402
import run_checks  # noqa: E402


def gate(paths):
    problems = []
    for p in map(Path, paths):
        if p.suffix.lower() not in (".json", ".csv") or not p.is_file():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if "cachedContents" in text:
            problems.append(f"{p}: contains cachedContents sample values")
        for hit in run_checks._scan_text(text):
            problems.append(f"{p}: contains a {hit}")
        if p.suffix.lower() == ".json":
            try:
                bad = f.typed_text_fields(text.encode("utf-8"))
            except ValueError:
                bad = {}
            for field, n in bad.items():
                problems.append(f"{p}: text field {field!r} has {n} distinct values (possible typed text)")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args(argv)
    paths = args.paths
    if not paths:
        out = subprocess.run(["git", "-C", args.root, "diff", "--cached", "--name-only", "--diff-filter=AM", "--", "sources/"],
                             capture_output=True, text=True, check=True).stdout.split()
        paths = [str(Path(args.root) / x) for x in out]
    problems = gate(paths)
    for line in problems:
        print("GATE FAIL", line)
    print(f"staged gate: {len(paths)} staged file(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
