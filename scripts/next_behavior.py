#!/usr/bin/env python3
"""Pick the next (city, behavior) for the funnel, deterministically.

Reads the "## Queue" list in agenda.md for city order and cities/<slug>/status.yaml for
each city's stage. The first city in agenda order that has work and is not blocked wins.
A city with no folder is at stage "proposed" and gets Scout. Nothing here calls a model
or the network.

Stage -> behavior: proposed scout, scouted discover, discovered fetch, fetched extract,
extracted assess, assessed draft, drafted publish. queued and published have no funnel
work: a draft is waiting on the supervisor, or the dossier is out.

A blocked city is skipped. A block of type "proposal" stops applying once a file in
queue/approvals/ lists the proposal id under `resolves:` in its front matter; every
other block type stays until the supervisor edits status.yaml.

Usage: python3 -I scripts/next_behavior.py [--root DIR] [--json] [--explain]
Prints "<city> <behavior>" or "nothing to do". Exit 0 for both, 2 when a status file
is missing or invalid (the script refuses to guess).
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
STAGES = ["proposed", "scouted", "discovered", "fetched", "extracted", "assessed",
          "drafted", "queued", "published"]
BEHAVIOR_FOR_STAGE = {
    "proposed": "scout", "scouted": "discover", "discovered": "fetch", "fetched": "extract",
    "extracted": "assess", "assessed": "draft", "drafted": "publish",
}
QUEUE_ITEM = re.compile(r"^\s*\d+\.\s+\**([a-z0-9][a-z0-9-]*)\**\s*:")


class StatusError(Exception):
    pass


def agenda_cities(root):
    """City slugs from the numbered list under '## Queue', in order."""
    path = Path(root) / "agenda.md"
    if not path.is_file():
        return []
    cities, in_queue = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            in_queue = line.strip().lower() == "## queue"
            continue
        m = QUEUE_ITEM.match(line) if in_queue else None
        if m and m.group(1) not in cities:
            cities.append(m.group(1))
    return cities


def resolved_proposals(root):
    """Proposal ids that a supervisor decision in queue/approvals/ lists under resolves."""
    resolved = set()
    folder = Path(root) / "queue" / "approvals"
    for path in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        m = re.match(r"\A---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        try:
            front = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            continue
        if isinstance(front, dict) and isinstance(front.get("resolves"), list):
            resolved.update(str(x) for x in front["resolves"])
    return resolved


def load_status(root, slug):
    """Return the city's status dict, or None when it has no folder (stage proposed)."""
    folder = Path(root) / "cities" / slug
    path = folder / "status.yaml"
    if not folder.is_dir():
        return None
    if not path.is_file():
        raise StatusError(f"{slug}: cities/{slug}/ exists but has no status.yaml")
    errors = validate.validate_file(path, "status.schema.json")
    if errors:
        raise StatusError("; ".join(errors))
    return validate.load_yaml(path)


def pick(root):
    """Return (choice, skipped). choice is {"city","behavior","stage"} or None."""
    resolved = resolved_proposals(root)
    skipped = []
    for slug in agenda_cities(root):
        status = load_status(root, slug)
        stage = status["stage"] if status else "proposed"
        block = status["blocked_on"] if status else None
        if block and not (block["type"] == "proposal" and block["ref"] in resolved):
            skipped.append(f"{slug}: blocked on {block['type']} {block['ref']}")
            continue
        behavior = BEHAVIOR_FOR_STAGE.get(stage)
        if behavior is None:
            skipped.append(f"{slug}: stage {stage}, no funnel work")
            continue
        return {"city": slug, "behavior": behavior, "stage": stage}, skipped
    return None, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--explain", action="store_true", help="also print skipped cities to stderr")
    args = ap.parse_args(argv)
    try:
        choice, skipped = pick(args.root)
    except StatusError as exc:
        print(f"next_behavior: {exc}", file=sys.stderr)
        return 2
    if args.explain:
        for line in skipped:
            print(f"skipped {line}", file=sys.stderr)
    if args.json:
        print(json.dumps({"next": choice, "skipped": skipped}))
    else:
        print(f"{choice['city']} {choice['behavior']}" if choice else "nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main())
