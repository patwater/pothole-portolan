#!/usr/bin/env python3
"""Render cities/<slug>/dossier.md to publishable Markdown.

Each {{claim:id}} marker becomes "<value> <unit>[^n]" and a footnote carrying the
source URL, retrieval date, archive path and method. Prints to stdout.

Usage: python3 -I scripts/render_dossier.py [--root DIR] SLUG
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

MARKER = re.compile(r"\{\{claim:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")


def fmt_value(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"{v:,}"
    return str(v)


def render(root, slug):
    d = Path(root) / "cities" / slug
    claims = {c["id"]: c for c in validate.load_yaml(d / "claims.yaml")}
    text = re.sub(r"<!--.*?-->", "", (d / "dossier.md").read_text(encoding="utf-8"), flags=re.S)
    order = {}

    def sub(m):
        cid = m.group(1)
        c = claims[cid]  # KeyError here means the checks were skipped
        n = order.setdefault(cid, len(order) + 1)
        return f"{fmt_value(c['value'])} {c['unit']}[^{n}]"

    body = MARKER.sub(sub, text)
    notes = []
    for cid, n in order.items():
        c = claims[cid]
        notes.append(
            f"[^{n}]: {c['statement']} Source: <{c['source_url']}>, retrieved {c['retrieved']}. "
            f"Archived copy: `{c['archive']}`. Method: {c['method']}")
    return body.rstrip() + "\n\n" + "\n".join(notes) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("slug")
    args = ap.parse_args(argv)
    sys.stdout.write(render(args.root, args.slug))


if __name__ == "__main__":
    main()
