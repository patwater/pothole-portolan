#!/usr/bin/env python3
"""Fetch behavior: retrieve listed sources for one city and archive them by content hash.

For each source in cities/<slug>/sources.yaml whose status is "listed":
  1. read robots.txt for the host and skip the source if the path is disallowed (rule 8);
  2. fetch the URL with an honest user agent, a timeout and a size cap;
  3. write the bytes to sources/<sha256>.<ext>;
  4. mark the entry fetched (with archive, retrieved, robots_checked) or unavailable (with a reason).

Nothing is interpreted: fetched content is data, never instructions (rule 4).
Only the listed URL is requested. This script does not follow links, call APIs that need
keys, or download record-level datasets.

Usage: python3 -I scripts/fetch_source.py [--root DIR] [--id SOURCE_ID ...] [--delay SECONDS] SLUG
"""
import argparse
import datetime
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

USER_AGENT = "PotholePortolanBot/0.1 (public-data research; +https://github.com/patwater/pothole-portolan)"
MAX_BYTES = 50 * 1024 * 1024
TIMEOUT = 60
EXT_BY_TYPE = {
    "text/html": ".html", "application/xhtml+xml": ".html", "application/pdf": ".pdf",
    "text/csv": ".csv", "application/json": ".json", "text/plain": ".txt",
    "application/xml": ".xml", "text/xml": ".xml",
}
HEADER = (
    "# Maintained by scripts/fetch_source.py (Fetch) from Discover's list. Status values:\n"
    "# listed (not yet fetched), fetched (archived under sources/), unavailable (reason in notes).\n"
)

_robots = {}
# A proxy refusal is the sandbox's network policy, not a fact about the source. Such sources
# stay "listed" and are reported, never marked unavailable.
BLOCKED = "blocked by the environment's network policy"


def robots_allows(url):
    """Return (allowed, detail). Fails closed when robots.txt cannot be read for a reason other than 404."""
    parts = urllib.parse.urlsplit(url)
    origin = f"{parts.scheme}://{parts.netloc}"
    if origin not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        req = urllib.request.Request(origin + "/robots.txt", headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                rp.parse(resp.read(1_000_000).decode("utf-8", errors="replace").splitlines())
            _robots[origin] = (rp, "robots.txt read")
        except urllib.error.HTTPError as exc:
            if exc.code in (404, 410):
                rp.parse([])
                _robots[origin] = (rp, f"no robots.txt (HTTP {exc.code})")
            else:
                _robots[origin] = (None, f"robots.txt returned HTTP {exc.code}")
        except Exception as exc:  # network failure: do not guess
            if "Tunnel connection failed" in str(exc):
                _robots[origin] = (None, BLOCKED)
            else:
                _robots[origin] = (None, f"robots.txt unreadable: {type(exc).__name__}")
    rp, detail = _robots[origin]
    if rp is None:
        return False, detail
    return rp.can_fetch(USER_AGENT, url), detail


def extension_for(content_type, final_url):
    ctype = (content_type or "").split(";")[0].strip().lower()
    if ctype in EXT_BY_TYPE:
        return EXT_BY_TYPE[ctype]
    suffix = Path(urllib.parse.urlsplit(final_url).path).suffix.lower()
    return suffix if suffix and len(suffix) <= 6 and suffix[1:].isalnum() else ".bin"


class RobotsDisallowed(Exception):
    pass


class RobotsAwareRedirects(urllib.request.HTTPRedirectHandler):
    """Check robots.txt for every redirect target before following it (rule 8)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        allowed, detail = robots_allows(newurl)
        if not allowed:
            raise RobotsDisallowed(f"redirect to {newurl}: " +
                                   ("disallowed by robots.txt for this user agent"
                                    if detail == "robots.txt read" else detail))
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    opener = urllib.request.build_opener(RobotsAwareRedirects)
    with opener.open(req, timeout=TIMEOUT) as resp:
        body = resp.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError(f"larger than {MAX_BYTES} bytes")
        return body, resp.geturl(), resp.headers.get("Content-Type", ""), resp.status


# Rule 7 for portal queries. The 311 dataset is record-level, so only grouped counts may be requested,
# and no query may mention a field that can identify a person or a private address. A dataset id that is
# not listed here is refused (fail closed). The Scorecard Measures dataset holds department performance
# figures, not records about people, so ordinary filtered reads are allowed for it.
SENSITIVE_FIELDS = {
    "address", "street", "lat", "long", "point", "point_address", "point_city", "point_geom", "point_state",
    "point_zip", "status_notes", "service_details", "media_url", "service_request_id",
}
MIN_GROUP_SIZE = 10
DATASET_POLICY = {
    "vw6y-z8j6": {"aggregate_only": True, "max_limit": 5000},   # SF 311 Cases (record-level)
    "kc49-udxn": {"aggregate_only": False, "max_limit": 5000},  # SF Scorecard Measures (department measures)
}


def query_policy(url):
    """Return None if the URL may be fetched, or a refusal reason. Applies to /resource/ query URLs only."""
    parts = urllib.parse.urlsplit(url)
    m = re.match(r"^/resource/([a-z0-9]{4}-[a-z0-9]{4})\.(json|csv)$", parts.path)
    if not m:
        return "a /resource/ URL must name a dataset id and end in .json or .csv" if parts.path.startswith("/resource/") else None
    rule = DATASET_POLICY.get(m.group(1))
    if rule is None:
        return f"dataset {m.group(1)} has no query policy, so it is refused"
    params = urllib.parse.parse_qs(parts.query, keep_blank_values=True)
    soql = {k: " ".join(v) for k, v in params.items() if k.startswith("$")}
    unknown = [k for k in params if not k.startswith("$")]
    if unknown:
        return f"plain filter parameters are not allowed ({', '.join(unknown)}); use $where"
    # Quoted literals are values, not columns: 'Street Defects' does not select the street column.
    no_literals = re.sub(r"'(?:[^']|'')*'", "''", " ".join(soql.values()))
    mentioned = set(re.findall(r"[a-z_][a-z0-9_]*", no_literals.lower()))
    banned = sorted(mentioned & SENSITIVE_FIELDS)
    if banned:
        return "query mentions sensitive field(s): " + ", ".join(banned)
    if rule["aggregate_only"]:
        if "$group" not in soql or "count(" not in soql.get("$select", "").lower():
            return "aggregate-only dataset: the query needs $group and a count() in $select"
        if "$query" in soql:
            return "$query is not allowed on an aggregate-only dataset"
        # Small groups can be single records: category fields in the 311 data hold typed text, so a one-case
        # group may be a business name and address. Require a minimum group size, applied by the portal.
        m2 = re.search(r"count\(\s*\*\s*\)\s*>=\s*(\d+)", soql.get("$having", ""))
        if m2 is None or int(m2.group(1)) < MIN_GROUP_SIZE:
            return f"aggregate-only dataset: $having count(*) >= {MIN_GROUP_SIZE} (or more) is required so small groups are never returned"
    limit = soql.get("$limit")
    if limit is None or not limit.isdigit() or int(limit) > rule["max_limit"]:
        return f"$limit must be given and at most {rule['max_limit']}"
    return None


MAX_TEXT_DISTINCT = 100


def typed_text_fields(body):
    """Return {field: distinct_count} for text fields of an aggregate response with more than MAX_TEXT_DISTINCT values.

    A grouped count is only safe to archive while the grouped fields are controlled vocabularies. A text
    field with hundreds of distinct values is the signature of typed text (names, addresses), and a minimum
    group size does not remove it: an applicant who files ten permits still appears by name.
    """
    rows = json.loads(body.decode("utf-8"))
    if not isinstance(rows, list):
        return {}
    values = {}
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str):
                values.setdefault(k, set()).add(v)
    def not_text(x):
        # Numbers and ISO dates or timestamps are values of a structured field, not typed text.
        return x.lstrip("-").replace(".", "", 1).isdigit() or re.match(r"^\d{4}-\d{2}-\d{2}([T ][\d:.+\-Z]*)?$", x) is not None

    return {k: len(v) for k, v in values.items() if len(v) > MAX_TEXT_DISTINCT and not all(not_text(x) for x in v)}


def sanitize(url, content_type, body):
    """Remove sample values that open data portals embed in dataset metadata (rule 7).

    Socrata /api/views/ JSON carries `cachedContents`: up to 20 sample values per column drawn from the
    live data, which for a 311 dataset include addresses, coordinates and free-text notes. Those are
    record-level fragments, so they are dropped before anything is archived. Returns (body, note or None).
    """
    if "/api/views/" not in urllib.parse.urlsplit(url).path or "json" not in (content_type or "").lower():
        return body, None
    removed = 0

    def strip(node):
        nonlocal removed
        if isinstance(node, dict):
            if "cachedContents" in node:
                removed += 1
                node = {k: v for k, v in node.items() if k != "cachedContents"}
            return {k: strip(v) for k, v in node.items()}
        if isinstance(node, list):
            return [strip(v) for v in node]
        return node

    cleaned = strip(json.loads(body.decode("utf-8")))
    out = json.dumps(cleaned, sort_keys=True, indent=1, ensure_ascii=False).encode("utf-8")
    note = (f"Archived copy has {removed} `cachedContents` blocks (sample column values, including addresses and free text) removed "
            "and the JSON re-serialized with sorted keys, under rule 7; its sha256 is of this sanitized file, not of the raw response.")
    return out, note


def append_note(entry, text):
    entry["notes"] = (entry.get("notes", "").rstrip() + " " if entry.get("notes") else "") + text


def run(root, slug, only_ids, delay):
    path = Path(root) / "cities" / slug / "sources.yaml"
    sources = validate.load_yaml(path)
    today = datetime.date.today().isoformat()
    archive_dir = Path(root) / "sources"
    archive_dir.mkdir(exist_ok=True)
    first = True
    blocked = 0
    refused = 0
    held = 0
    for entry in sources:
        if entry.get("status") != "listed" or (only_ids and entry["id"] not in only_ids):
            continue
        if not first:
            time.sleep(delay)
        first = False
        url = entry["url"]
        refusal = query_policy(url)
        if refusal:
            print(f"REFUSED     {entry['id']}: {refusal}; left as listed")
            refused += 1
            continue
        allowed, robots_detail = robots_allows(url)
        if robots_detail == BLOCKED:
            print(f"BLOCKED     {entry['id']}: {BLOCKED}; left as listed")
            blocked += 1
            continue
        if not allowed:
            entry["status"] = "unavailable"
            entry["retrieved"] = today
            reason = ("disallowed by robots.txt for this user agent" if robots_detail == "robots.txt read"
                      else robots_detail)
            append_note(entry, f"Fetch {today}: not retrieved, {reason}.")
            print(f"UNAVAILABLE {entry['id']}: {robots_detail}")
            continue
        try:
            body, final_url, ctype, status = fetch(url)
        except RobotsDisallowed as exc:
            entry["status"] = "unavailable"
            entry["retrieved"] = today
            append_note(entry, f"Fetch {today}: not retrieved, {exc}.")
            print(f"UNAVAILABLE {entry['id']}: {exc}")
            continue
        except urllib.error.HTTPError as exc:
            entry["status"] = "unavailable"
            entry["retrieved"] = today
            append_note(entry, f"Fetch {today}: HTTP {exc.code} {exc.reason}.")
            print(f"UNAVAILABLE {entry['id']}: HTTP {exc.code}")
            continue
        except Exception as exc:
            if "Tunnel connection failed" in str(exc):
                print(f"BLOCKED     {entry['id']}: {BLOCKED}; left as listed")
                blocked += 1
                continue
            entry["status"] = "unavailable"
            entry["retrieved"] = today
            append_note(entry, f"Fetch {today}: {type(exc).__name__}: {exc}.")
            print(f"UNAVAILABLE {entry['id']}: {type(exc).__name__}")
            continue
        rule = DATASET_POLICY.get((re.match(r"^/resource/([a-z0-9]{4}-[a-z0-9]{4})\.json$", urllib.parse.urlsplit(url).path) or [None, None])[1])
        if rule and rule["aggregate_only"]:
            try:
                offenders = typed_text_fields(body)
            except ValueError:
                offenders = {"(response)": 0}
            if offenders:
                print(f"HELD        {entry['id']}: text field(s) with too many distinct values for a controlled vocabulary "
                      f"({', '.join(f'{k}: {v}' for k, v in offenders.items())}); possible typed text, so nothing was archived; left as listed")
                held += 1
                continue
        try:
            body, sanitize_note = sanitize(final_url, ctype, body)
        except ValueError as exc:
            entry["status"] = "unavailable"
            entry["retrieved"] = today
            append_note(entry, f"Fetch {today}: response could not be parsed for sanitizing ({type(exc).__name__}), so it was not archived.")
            print(f"UNAVAILABLE {entry['id']}: could not sanitize")
            continue
        digest = hashlib.sha256(body).hexdigest()
        ext = extension_for(ctype, final_url)
        rel = f"sources/{digest}{ext}"
        target = Path(root) / rel
        if not target.exists():
            target.write_bytes(body)
        entry["status"] = "fetched"
        entry["retrieved"] = today
        entry["archive"] = rel
        entry["robots_checked"] = True
        detail = f"Fetch {today}: HTTP {status}, {ctype.split(';')[0] or 'unknown type'}, {len(body)} bytes"
        if final_url != url:
            detail += f", final URL {final_url}"
        append_note(entry, detail + "." + (" " + sanitize_note if sanitize_note else ""))
        print(f"FETCHED     {entry['id']}: {rel} ({len(body)} bytes)")
    path.write_text(HEADER + yaml.safe_dump(sources, sort_keys=False, allow_unicode=True, width=100),
                    encoding="utf-8")
    errors = validate.validate_file(path, "sources.schema.json")
    for line in errors:
        print("SCHEMA", line)
    if blocked:
        print(f"{blocked} source(s) blocked by network policy and left as listed")
    if refused:
        print(f"{refused} source(s) refused by the query policy and left as listed")
    if held:
        print(f"{held} source(s) held for review: possible typed text in a grouped field")
    return 1 if errors else (4 if held else (3 if refused else (2 if blocked else 0)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--id", action="append", default=[])
    ap.add_argument("--delay", type=float, default=3.0, help="seconds between requests")
    ap.add_argument("slug")
    args = ap.parse_args(argv)
    return run(args.root, args.slug, set(args.id), args.delay)


if __name__ == "__main__":
    sys.exit(main())
