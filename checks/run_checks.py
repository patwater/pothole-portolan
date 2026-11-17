#!/usr/bin/env python3
"""Deterministic publish gates for Pothole Portolan. See checks/publish.md.

Usage:
  python3 -I checks/run_checks.py [--root DIR] [--city SLUG ...] [--content-only]

Exit status 0 only if every check passes. Warnings never fail a run but are printed.
--content-only skips the phase and PAUSE gate, so drafts can be checked before the
phase permits publishing. A real publish must run without it.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import fetch_source  # noqa: E402
import validate  # noqa: E402
import yaml  # noqa: E402

MARKER = re.compile(r"\{\{claim:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")
CONDITION_WORDS = re.compile(
    r"\b(conditions?|quality|PCI|deteriorat\w*|state of repair|worse|worst|better|best|"
    r"poor|failing|crumbling|smooth\w*|pavement health|road health)\b", re.I)
RANK_WORDS = re.compile(r"\b(rank\w*|league table|worst|best|highest|lowest|top \d+)\b", re.I)
DISCLAIMER = re.compile(
    r"\b(not|does not|do not|cannot|isn't|never)\b[^.]{0,60}\b"
    r"(measure|indicat\w+|reflect|represent|proxy)\b", re.I)
DEMAND_VOCAB = re.compile(r"\b(requests?|reports?|reported|complaints?|calls?|tickets?|311|cases?)\b", re.I)

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")
STREET = re.compile(
    r"\b\d{1,6}\s+(?:[NSEW]\.?\s+)?[A-Z][\w.]*(?:\s+[A-Z][\w.]*)*\s+"
    r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl)\b")
SENSITIVE_COLUMN = re.compile(
    r"(address|addr\b|house_?(no|number)|apt|(first|last|full|requester|reporter|customer|"
    r"contact|owner|resident)_?name|requester|reporter|customer|resident|caller|phone|email|"
    r"description|comments?|narrative|free_?text|details)", re.I)
RECORD_FILE_SUFFIXES = {".csv", ".tsv", ".jsonl", ".geojson", ".parquet", ".xlsx", ".xls", ".sqlite", ".db"}
TEXT_SUFFIXES = {".txt", ".md", ".html", ".htm", ".xml"}
MAX_SCAN_BYTES = 5_000_000


class Report:
    def __init__(self):
        self.failures = []
        self.warnings = []

    def fail(self, check, city, msg):
        self.failures.append((check, city, msg))

    def warn(self, check, city, msg):
        self.warnings.append((check, city, msg))


def read_yaml(path):
    try:
        return validate.load_yaml(path)
    except Exception:  # unreadable YAML is reported by the schema check
        return None


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def city_dir(root, slug):
    return Path(root) / "cities" / slug


def load_city(root, slug):
    d = city_dir(root, slug)
    claims = read_yaml(d / "claims.yaml") if (d / "claims.yaml").exists() else None
    sources = read_yaml(d / "sources.yaml") if (d / "sources.yaml").exists() else None
    claims = claims if isinstance(claims, list) else []
    sources = sources if isinstance(sources, list) else []
    return ([c for c in claims if isinstance(c, dict)],
            [s for s in sources if isinstance(s, dict)])


# ---- check 0: phase and PAUSE gate -------------------------------------------------

def check_phase_gate(root, rep):
    root = Path(root)
    if (root / "PAUSE").exists():
        rep.fail("phase_gate", "-", "PAUSE exists at the repo root: no outward-facing calls")
    perm_path = root / "permissions.yaml"
    if not perm_path.exists():
        rep.fail("phase_gate", "-", "permissions.yaml is missing")
        return
    perm = read_yaml(perm_path) or {}
    phase = perm.get("phase") if isinstance(perm, dict) else None
    allowed = ((perm.get("publish") or {}).get("agent_may_publish_in_phases") or []) if isinstance(perm, dict) else []
    if phase not in allowed:
        rep.fail("phase_gate", "-", f"phase {phase!r} does not permit the agent to publish (allowed: {allowed})")


# ---- check 1: schema validity ------------------------------------------------------

def check_schema(root, slug, rep):
    d = city_dir(root, slug)
    for name in ("claims.yaml", "sources.yaml", "dossier.md"):
        if not (d / name).exists():
            rep.fail("schema", slug, f"missing {name}")
    for err in validate.validate_city(root, slug):
        rep.fail("schema", slug, err)


# ---- check 2: provenance on every claim -------------------------------------------

def check_provenance(root, slug, rep):
    claims, sources = load_city(root, slug)
    fetched = {s.get("archive") for s in sources if s.get("status") == "fetched"}
    today = datetime.date.today()
    for c in claims:
        cid = c.get("id", "(no id)")
        for field in ("source_url", "retrieved", "archive"):
            if not c.get(field):
                rep.fail("provenance", slug, f"claim {cid}: missing {field}")
        try:
            when = datetime.date.fromisoformat(str(c.get("retrieved", "")))
            if when > today:
                rep.fail("provenance", slug, f"claim {cid}: retrieved date {when} is in the future")
        except ValueError:
            rep.fail("provenance", slug, f"claim {cid}: retrieved is not a valid YYYY-MM-DD date")
        if c.get("archive") and c["archive"] not in fetched:
            rep.fail("provenance", slug,
                     f"claim {cid}: archive {c['archive']} is not listed as a fetched source in sources.yaml")


# ---- check 3: archives exist and match their hash ---------------------------------

def check_archives(root, slug, rep):
    claims, sources = load_city(root, slug)
    refs = {c.get("archive") for c in claims} | {s.get("archive") for s in sources if s.get("status") == "fetched"}
    for ref in sorted(r for r in refs if r):
        path = Path(root) / ref
        if not path.is_file():
            rep.fail("archives", slug, f"archive {ref} does not exist")
            continue
        expected = Path(ref).stem
        actual = sha256_of(path)
        if actual != expected:
            rep.fail("archives", slug, f"archive {ref} has sha256 {actual}, which does not match its name")


def _is_schema_document(data):
    """A dataset description: column definitions, not data. Its keys (description, fieldName...) name things."""
    if isinstance(data, dict) and isinstance(data.get("columns"), list) and data["columns"]:
        return all(isinstance(c, dict) and "fieldName" in c for c in data["columns"])
    if isinstance(data, list) and data:
        return all(isinstance(c, dict) and "fieldName" in c and "dataTypeName" in c for c in data)
    return False


def _portal_dataset(url):
    m = re.match(r"^https?://[^/]+/resource/([a-z0-9]{4}-[a-z0-9]{4})\.json", url or "")
    return m.group(1) if m else None


def _portal_response_problems(raw, rule):
    """Re-apply the fetcher's guards to an archived portal response."""
    try:
        rows = json.loads(raw.decode("utf-8"))
    except ValueError:
        return ["portal response is not valid JSON"]
    if not isinstance(rows, list):
        return ["portal response is not a list of rows"]
    problems = [f"text field {k!r} has {n} distinct values (possible typed text)"
                for k, n in fetch_source.typed_text_fields(raw).items()]
    if rule["aggregate_only"] and rows:
        counts = [r.get("cases", r.get("count")) for r in rows]
        try:
            if any(c is None for c in counts):
                problems.append("aggregate response has a row without a count field named 'cases' or 'count'")
            else:
                small = sum(1 for c in counts if int(c) < fetch_source.MIN_GROUP_SIZE)
                if small:
                    problems.append(f"{small} group(s) smaller than {fetch_source.MIN_GROUP_SIZE} cases")
        except (TypeError, ValueError):
            problems.append("count field is not numeric")
    return problems


# ---- check 4: no record-level personal data ---------------------------------------

def _scan_text(text, check_street=True):
    hits = []
    if EMAIL.search(text):
        hits.append("email address")
    if PHONE.search(text):
        hits.append("phone number")
    if check_street and STREET.search(text):
        hits.append("street address")
    return hits


def _json_keys(node, limit=200):
    keys, stack, seen = set(), [node], 0
    while stack and seen < limit:
        cur = stack.pop()
        if isinstance(cur, dict):
            seen += 1
            keys.update(str(k) for k in cur)
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur[:limit])
    return keys


def check_personal_data(root, slug, rep):
    d = city_dir(root, slug)
    # Published and committed text for this city.
    for path in sorted(d.rglob("*")) if d.exists() else []:
        if not path.is_file():
            continue
        if path.suffix.lower() in RECORD_FILE_SUFFIXES:
            rep.fail("personal_data", slug,
                     f"{path.relative_to(root)}: data file under cities/; archives belong in sources/ and must be aggregate")
            continue
        try:
            text = path.read_text(encoding="utf-8")[:MAX_SCAN_BYTES]
        except (UnicodeDecodeError, OSError):
            rep.warn("personal_data", slug, f"{path.relative_to(root)}: unreadable as text, review by hand")
            continue
        for hit in _scan_text(text):
            rep.fail("personal_data", slug, f"{path.relative_to(root)}: contains a {hit}")
    drafts = Path(root) / "queue" / "drafts"
    for path in sorted(drafts.glob(f"{slug}*")) if drafts.is_dir() else []:
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            for hit in _scan_text(path.read_text(encoding="utf-8")[:MAX_SCAN_BYTES]):
                rep.fail("personal_data", slug, f"{path.relative_to(root)}: contains a {hit}")
    # Archived copies this city depends on.
    claims, sources = load_city(root, slug)
    refs = {c.get("archive") for c in claims} | {s.get("archive") for s in sources if s.get("status") == "fetched"}
    src_by_archive = {s.get("archive"): s for s in sources if s.get("archive")}
    for ref in sorted(r for r in refs if r):
        path = Path(root) / ref
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        raw = path.read_bytes()[:MAX_SCAN_BYTES]
        if suffix in {".csv", ".tsv", ".json", ".jsonl", ".geojson"}:
            text = raw.decode("utf-8", errors="replace")
            columns = set()
            try:
                if suffix in {".csv", ".tsv"}:
                    dialect = "excel-tab" if suffix == ".tsv" else "excel"
                    columns = set(next(csv.reader(io.StringIO(text), dialect=dialect), []))
                elif suffix == ".jsonl":
                    for line in text.splitlines()[:200]:
                        if line.strip():
                            columns |= _json_keys(json.loads(line))
                else:
                    data = json.loads(text)
                    rule = fetch_source.DATASET_POLICY.get(_portal_dataset(src_by_archive.get(ref, {}).get("url")))
                    if _is_schema_document(data):
                        # Column definitions carry no data. The real risk is embedded sample values.
                        if "cachedContents" in text:
                            rep.fail("personal_data", slug, f"{ref}: dataset description still contains cachedContents sample values")
                    elif rule is not None:
                        # A registered portal dataset: its column names were vetted when the query was listed.
                        for problem in _portal_response_problems(raw, rule):
                            rep.fail("personal_data", slug, f"{ref}: {problem}")
                    else:
                        columns = _json_keys(data)
            except (ValueError, csv.Error):
                rep.warn("personal_data", slug, f"{ref}: could not parse to inspect columns, review by hand")
            for col in sorted(columns):
                if SENSITIVE_COLUMN.search(col.replace(" ", "_")):
                    rep.fail("personal_data", slug, f"{ref}: column {col!r} suggests record-level personal or free-text data")
            for hit in _scan_text(text):
                rep.fail("personal_data", slug, f"{ref}: contains a {hit}")
        elif suffix in TEXT_SUFFIXES:
            for hit in _scan_text(raw.decode("utf-8", errors="replace"), check_street=False):
                rep.warn("personal_data", slug, f"{ref}: contains a {hit} (public page? confirm by hand)")
        else:
            rep.warn("personal_data", slug, f"{ref}: binary or unscanned format, review by hand")


# ---- check 4b: spending is dollars, program output is not --------------------------

CURRENCY_UNIT = re.compile(r"(USD|\$|dollar)", re.I)


def check_kind_units(root, slug, rep):
    """A `spending` claim must have a currency unit, and a `program_output` claim must not.

    The point is to keep counts of work done (blocks resurfaced) from being summed or read as money.
    """
    claims, _ = load_city(root, slug)
    for c in claims:
        unit = str(c.get("unit", ""))
        if c.get("kind") == "spending" and not CURRENCY_UNIT.search(unit):
            rep.fail("kind_units", slug, f"claim {c.get('id')}: kind spending but unit {unit!r} is not a currency; use program_output for counts of work")
        if c.get("kind") == "program_output" and CURRENCY_UNIT.search(unit):
            rep.fail("kind_units", slug, f"claim {c.get('id')}: kind program_output but unit {unit!r} is a currency; use spending")


# ---- check 5: reported demand is never described as condition ---------------------

def _strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def parse_dossier(text):
    """Return (front_matter, [(heading, paragraph)])."""
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    front = None
    if m:
        try:
            front = yaml.safe_load(m.group(1))
        except yaml.YAMLError:
            front = None
    body = _strip_comments(text[m.end():] if m else text)
    blocks, heading, para = [], "", []

    def flush():
        if para:
            blocks.append((heading, " ".join(para)))
            para.clear()

    for line in body.splitlines():
        if line.startswith("#"):
            flush()
            heading = line.lstrip("#").strip()
        elif not line.strip():
            flush()
        else:
            para.append(line.strip())
    flush()
    return front, blocks


def check_demand_vs_condition(root, slug, rep):
    claims, _ = load_city(root, slug)
    by_id = {c.get("id"): c for c in claims}
    for c in claims:
        if c.get("kind") != "reported_demand":
            continue
        statement = str(c.get("statement", ""))
        if CONDITION_WORDS.search(statement) and not DISCLAIMER.search(statement):
            rep.fail("demand_vs_condition", slug,
                     f"claim {c.get('id')}: reported_demand statement uses condition language")
        if not DEMAND_VOCAB.search(statement):
            rep.fail("demand_vs_condition", slug,
                     f"claim {c.get('id')}: reported_demand statement does not say that it counts requests or reports")
    dossier = city_dir(root, slug) / "dossier.md"
    if not dossier.exists():
        return
    _, blocks = parse_dossier(dossier.read_text(encoding="utf-8"))
    for heading, para in blocks:
        ids = MARKER.findall(para)
        kinds = {by_id[i].get("kind") for i in ids if i in by_id}
        has_demand = "reported_demand" in kinds or re.search(r"\b311\b|service requests?", para, re.I)
        if has_demand and CONDITION_WORDS.search(para) and not DISCLAIMER.search(para):
            rep.fail("demand_vs_condition", slug,
                     f"under {heading!r}: paragraph pairs reported demand with condition language without a disclaimer")
        if has_demand and RANK_WORDS.search(para):
            rep.fail("demand_vs_condition", slug, f"under {heading!r}: paragraph ranks or superlatives on 311 counts")
        in_condition = re.search(r"condition|survey|index|pci", heading, re.I) and not re.search(r"report|demand", heading, re.I)
        in_demand = re.search(r"report|demand", heading, re.I) and not re.search(r"condition|survey|index|pci", heading, re.I)
        if "reported_demand" in kinds and in_condition:
            rep.fail("demand_vs_condition", slug, f"reported_demand claim placed under condition heading {heading!r}")
        if "measured_condition" in kinds and in_demand:
            rep.fail("demand_vs_condition", slug, f"measured_condition claim placed under demand heading {heading!r}")


# ---- check 6: dossier structure and claim references ------------------------------

def check_dossier(root, slug, rep):
    path = city_dir(root, slug) / "dossier.md"
    if not path.exists():
        return
    claims, _ = load_city(root, slug)
    by_id = {c.get("id"): c for c in claims}
    front, blocks = parse_dossier(path.read_text(encoding="utf-8"))
    if not isinstance(front, dict):
        rep.fail("dossier", slug, "front matter missing or not valid YAML")
    else:
        for key in ("slug", "city", "version", "drafted"):
            if key not in front:
                rep.fail("dossier", slug, f"front matter missing {key}")
        if front.get("slug") != slug:
            rep.fail("dossier", slug, f"front matter slug {front.get('slug')!r} does not match folder {slug!r}")
    if not any(re.search(r"could not be found|not found", h, re.I) for h, _ in blocks) and \
       not re.search(r"^#+\s.*(could not be found|not found)", path.read_text(encoding="utf-8"), re.I | re.M):
        rep.fail("dossier", slug, "missing a 'What could not be found' section")
    for heading, para in blocks:
        for cid in MARKER.findall(para):
            claim = by_id.get(cid)
            if claim is None:
                rep.fail("dossier", slug, f"under {heading!r}: unknown claim id {cid}")
            elif claim.get("confidence") not in ("supported", "provisional"):
                rep.fail("dossier", slug, f"claim {cid} has confidence {claim.get('confidence')!r}; only supported or provisional may ship")
        stripped = MARKER.sub("", para)
        if heading.lower() not in ("sources", "version history"):
            for m in re.finditer(r"(?<![\w.])\d[\d,]*(?:\.\d+)?%?", stripped):
                tok = m.group(0)
                bare = tok.rstrip("%").replace(",", "")
                if bare.isdigit() and 1900 <= int(bare) <= 2100 and "," not in tok and "%" not in tok:
                    continue
                if bare.isdigit() and int(bare) < 10 and "%" not in tok:
                    continue
                rep.warn("dossier", slug, f"under {heading!r}: number {tok!r} typed by hand; use a claim marker")


CHECKS = [check_schema, check_provenance, check_archives, check_personal_data, check_kind_units,
          check_demand_vs_condition, check_dossier]


def run(root, cities, content_only):
    rep = Report()
    if not content_only:
        check_phase_gate(root, rep)
    for slug in cities:
        for check in CHECKS:
            check(root, slug, rep)
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--city", action="append", default=[])
    ap.add_argument("--content-only", action="store_true")
    args = ap.parse_args(argv)
    cities = args.city or validate.list_cities(args.root)
    rep = run(args.root, cities, args.content_only)
    for check, city, msg in rep.warnings:
        print(f"WARN  [{check}] {city}: {msg}")
    for check, city, msg in rep.failures:
        print(f"FAIL  [{check}] {city}: {msg}")
    print(f"checks: {len(cities)} city folder(s), {len(rep.failures)} failure(s), {len(rep.warnings)} warning(s)")
    return 1 if rep.failures else 0


if __name__ == "__main__":
    sys.exit(main())
