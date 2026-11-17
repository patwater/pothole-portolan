---
id: 2026-11-17-001
from: agent (Fetch, san-francisco)
needs: supervisor decision
problem_relieved: Four San Francisco sources could not be archived, and Extract needs hosts the environment does not yet allow.
---

# Fetch follow-ups for San Francisco

## 1. Sources the bot may not fetch (robots.txt)

- **Budget and Legislative Analyst audit of the resurfacing program (2021).** It now lives on `sfbos.archive.sf.gov`, whose robots.txt disallows every agent except archive.org's. The audit is the main source for the finding that the city has a citywide PCI goal but no breakdown by district.
- **Open311 endpoint.** `mobile311.sfgov.org` disallows all robots.

**Options.** (a) Accept the gap and record both as unavailable in the dossier, which is the current state. (b) You download the audit by hand and add it to `sources/` with a retrieval note, since a human reading a public document is not a robot. (c) Ask the Board of Supervisors clerk whether a robot-friendly copy exists. I recommend (a) now and (b) if the audit's findings turn out to matter for the dossier. I will not work around robots.txt.

## 2. Hosts needed for Extract (new outward-facing reach)

The environment `pothole-portolan` currently allows 12 hosts, all for fetching pages. Extracting a 311 count needs an aggregate query, and the official bulk route is on a host I have not requested:

- `data.sfgov.org` for an aggregate (count by year and type) query against the 311 Cases dataset. Only aggregates would be archived (rule 7).
- The data host for the Scorecards pothole-response dataset, which is probably the same host.

**Ask:** approve adding `data.sfgov.org`. I will request it through the environment prompt when Extract starts, unless you would rather decide here first.

## 3. Gateway problem on support.datasf.org

The gateway returns 502 for `support.datasf.org` although the host is allowed. This looks like an upstream or gateway fault, not policy. I will retry in the next run. If it persists, the 311 FAQ is replaceable by the dataset's own documentation page on the open data portal.

## 4. A supervisor-owned file to review

`scripts/fetch_source.py` is new and sits in `scripts/`, which is agent territory, but it enforces rule 8 (robots.txt on every redirect hop, honest user agent, rate limit). A quick read from you is worthwhile before I run it on a second city.
