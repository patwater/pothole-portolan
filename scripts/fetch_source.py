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
    for entry in sources:
        if entry.get("status") != "listed" or (only_ids and entry["id"] not in only_ids):
            continue
        if not first:
            time.sleep(delay)
        first = False
        url = entry["url"]
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
    return 1 if errors else (2 if blocked else 0)


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
