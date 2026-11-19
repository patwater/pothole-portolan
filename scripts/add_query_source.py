#!/usr/bin/env python3
"""List one Socrata (SoQL) query as a source in cities/<slug>/sources.yaml, status "listed".

The URL is built here so every query is reproducible by a reader, and it must pass the same
policy the fetcher enforces (scripts/fetch_source.py: query_policy) or it is not listed.

Usage: python3 -I scripts/add_query_source.py SLUG --id ID --name NAME --host HOST --dataset XXXX-XXXX
         [--select S] [--where W] [--group G] [--having H] [--order O] [--limit N] --purpose TEXT
"""
import argparse
import sys
import urllib.parse
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_source as f  # noqa: E402
import validate  # noqa: E402


def build_url(host, dataset, select=None, where=None, group=None, having=None, order=None, limit=None, fmt="json"):
    pairs = [("$select", select), ("$where", where), ("$group", group), ("$having", having), ("$order", order), ("$limit", limit)]
    safe = "(),*'"
    query = "&".join(k + "=" + urllib.parse.quote(str(v), safe=safe) for k, v in pairs if v not in (None, ""))
    return f"https://{host}/resource/{dataset}.{fmt}?{query}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    for a in ("id", "name", "host", "dataset", "purpose"):
        ap.add_argument(f"--{a}", required=True)
    for a in ("select", "where", "group", "having", "order", "limit"):
        ap.add_argument(f"--{a}")
    ap.add_argument("--publisher", default="DataSF")
    args = ap.parse_args(argv)
    url = build_url(args.host, args.dataset, args.select, args.where, args.group, args.having, args.order, args.limit)
    refusal = f.query_policy(url)
    if refusal:
        print(f"NOT LISTED: {refusal}")
        return 1
    path = Path(args.root) / "cities" / args.slug / "sources.yaml"
    sources = validate.load_yaml(path)
    if any(s["id"] == args.id for s in sources):
        print(f"NOT LISTED: id {args.id} already exists")
        return 1
    sources.append({"id": args.id, "name": args.name, "publisher": args.publisher, "source_type": "open_data_portal",
                    "url": url, "status": "listed",
                    "notes": f"Aggregate query, no records. Purpose: {args.purpose}"})
    path.write_text(f.HEADER + yaml.safe_dump(sources, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    errors = validate.validate_file(path, "sources.schema.json")
    print(url)
    for e in errors:
        print("SCHEMA", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
