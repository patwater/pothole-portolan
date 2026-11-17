#!/usr/bin/env python3
"""Render cities/<slug>/dossier.md to publishable Markdown.

- Each {{claim:id}} marker becomes "<value> <unit>[^n]".
- Each footnote carries the claim's statement, source URL, retrieval date, archive path, method and caveats.
  A method or caveat text that repeats an earlier note is not repeated; it points to that note.
- The "## Sources" section is filled with every source in sources.yaml: fetched sources with their URL,
  retrieval date and archived copy, and sources that were not retrieved, marked as such.
- An unknown claim id stops the render, so unchecked text cannot be published by accident.

Prints to stdout. Usage: python3 -I scripts/render_dossier.py [--root DIR] SLUG
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


def sources_block(sources):
    lines = []
    for s in sources:
        if s.get("status") == "fetched":
            lines.append(f"- {s['name']}. <{s['url']}>, retrieved {s['retrieved']}, archived copy `{s['archive']}`.")
        elif s.get("status") == "unavailable":
            lines.append(f"- {s['name']}. <{s['url']}>, not retrieved (attempted {s.get('retrieved', 'date not recorded')}); see the section on what could not be found.")
        else:
            lines.append(f"- {s['name']}. <{s['url']}>, listed and not yet retrieved.")
    return "\n".join(lines)


def render(root, slug):
    d = Path(root) / "cities" / slug
    claims = {c["id"]: c for c in validate.load_yaml(d / "claims.yaml")}
    sources = validate.load_yaml(d / "sources.yaml")
    text = re.sub(r"<!--.*?-->", "", (d / "dossier.md").read_text(encoding="utf-8"), flags=re.S)
    unknown = sorted({m for m in MARKER.findall(text) if m not in claims})
    if unknown:
        raise SystemExit("unknown claim id(s): " + ", ".join(unknown))
    order = {}

    def sub(m):
        cid = m.group(1)
        c = claims[cid]
        n = order.setdefault(cid, len(order) + 1)
        return f"{fmt_value(c['value'])} {c['unit']}[^{n}]"

    body = MARKER.sub(sub, text)

    block = sources_block(sources)
    if re.search(r"^## Sources\s*$", body, re.M):
        body = re.sub(r"^(## Sources)\s*$", lambda m: m.group(1) + "\n\n" + block, body, count=1, flags=re.M)
    else:
        body = body.rstrip() + "\n\n## Sources\n\n" + block

    notes, seen_method, seen_caveat = [], {}, {}
    for cid, n in order.items():
        c = claims[cid]
        parts = [f"{c['statement']} Source: <{c['source_url']}>, retrieved {c['retrieved']}. Archived copy: `{c['archive']}`."]
        parts.append(f"Method: same as note [^{seen_method[c['method']]}]." if c["method"] in seen_method else f"Method: {c['method']}")
        seen_method.setdefault(c["method"], n)
        if c.get("caveats"):
            parts.append(f"Caveats: same as note [^{seen_caveat[c['caveats']]}]." if c["caveats"] in seen_caveat else f"Caveats: {c['caveats']}")
            seen_caveat.setdefault(c["caveats"], n)
        notes.append(f"[^{n}]: " + " ".join(parts))
    return body.rstrip() + "\n\n" + "\n\n".join(notes) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("slug")
    args = ap.parse_args(argv)
    sys.stdout.write(render(args.root, args.slug))


if __name__ == "__main__":
    main()
