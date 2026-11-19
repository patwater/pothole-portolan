#!/usr/bin/env python3
"""Validate cities/<slug>/claims.yaml and sources.yaml against schemas/.

Usage: python3 -I scripts/validate.py [--root DIR] [city-slug ...]
Exit status 0 when every present file is valid, 1 otherwise.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "schemas"
FILES = {"claims.yaml": "claims.schema.json", "sources.yaml": "sources.schema.json"}


def load_yaml(path):
    """Load YAML; dates become ISO strings and an empty file becomes []."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return []
    return json.loads(json.dumps(data, default=str))


def list_cities(root):
    cities = Path(root) / "cities"
    if not cities.is_dir():
        return []
    return sorted(p.name for p in cities.iterdir()
                  if p.is_dir() and not p.name.startswith((".", "_")))


def validate_file(path, schema_name):
    """Return a list of human-readable error strings for one file."""
    try:
        data = load_yaml(path)
    except yaml.YAMLError as exc:
        return [f"{path}: not valid YAML: {exc}"]
    schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(map(str, e.absolute_path))):
        where = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{path}: {where}: {err.message}")
    if isinstance(data, list):
        seen = set()
        for i, item in enumerate(data):
            item_id = item.get("id") if isinstance(item, dict) else None
            if item_id in seen:
                errors.append(f"{path}: {i}/id: duplicate id {item_id!r}")
            seen.add(item_id)
    return errors


def validate_city(root, slug):
    errors = []
    for fname, schema_name in FILES.items():
        path = Path(root) / "cities" / slug / fname
        if path.exists():
            errors.extend(validate_file(path, schema_name))
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("cities", nargs="*")
    args = ap.parse_args(argv)
    cities = args.cities or list_cities(args.root)
    errors = []
    for slug in cities:
        errors.extend(validate_city(args.root, slug))
    for line in errors:
        print(line)
    print(f"validate: {len(cities)} city folder(s), {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
