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

## 2. Hosts and plan for the 311 and response-time data (revised 2026-11-17, after Assess)

**Correction to my first version.** I asked for `data.sfgov.org` only. The archives show two hosts: the DataSF catalog record lists the 311 Cases dataset (id `vw6y-z8j6`) at `data.sf.gov`, including its metadata and column endpoints, and the city's own scorecard pages link the Scorecard Measures dataset (id `kc49-udxn`) on `data.sfgov.org`. **Ask: allow both `data.sf.gov` and `data.sfgov.org`.** No credential is needed to start.

**Plan, one behavior per run, each with a stopping point.**

1. *Fetch, metadata only. DONE 2026-11-17, see `cities/san-francisco/notes.md`.* Read robots.txt on both hosts. If it disallows the API paths, stop and report. Otherwise archive the two datasets' metadata and column lists. No records are touched. This shows the real column names and how pothole cases are classified, which I have not seen and will not guess.
2. *Fetch, aggregates only. DONE 2026-11-17, with a minimum group size of 10, see `cities/san-francisco/notes.md`.* Ask the portal's own query interface for counts grouped by calendar year and case type (and by reporting channel, if the metadata supports it, since channel mix affects what a count means). Nothing that could identify a person or address is selected, so no record-level data reaches the repo (rule 7). Archive each response by hash and record the exact query URL in `sources.yaml`, so a reader can re-run it. Then fetch the pothole-response rows of the Scorecard Measures dataset, which are already aggregates. Fewer than ten requests, three seconds apart, with the honest user agent.
3. *Extract.* `reported_demand` claims from the counts, each stating which case types were counted and the caveats the sources support (duplicates, channels, agencies not covered). `response_time` claims from the scorecard measure, noting that its method counts requests answered within three business days against a 72-hour headline.
4. *Assess.* A real second derivation: re-run the counts with a different grouping (by month, summed to years) and require agreement. That is stronger independence than the sentence-level checks on the press-release claims.
5. *Draft.* Only after step 4.

**Stops.** If the only route to the data is a bulk record-level download, I stop and ask you before touching it. If the portal throttles anonymous requests and asks for an app token, I stop and request it through the credential prompt, since that would be a new credential.

**If you would rather not allow the hosts.** Then San Francisco's dossier would have to leave out residents' reports and repair speed, and say that they were not retrieved because of this project's network limits, not that they do not exist. I would not recommend shipping it that way. The alternative is to park San Francisco and begin Chicago, which will raise the same question about its portal.

## 3. Gateway problem on support.datasf.org

The gateway returns 502 for `support.datasf.org` although the host is allowed. This looks like an upstream or gateway fault, not policy. I retried in a second run on 2026-11-17 and it failed the same way, so it has now failed twice. If it persists, the 311 FAQ is replaceable by the dataset's own documentation page on the open data portal.

## 4. A supervisor-owned file to review

`scripts/fetch_source.py` is new and sits in `scripts/`, which is agent territory, but it enforces rule 8 (robots.txt on every redirect hop, honest user agent, rate limit). A quick read from you is worthwhile before I run it on a second city.

## 5. Added by Extract: a claim kind for program output (APPLIED 2026-11-17 under approval `2026-11-17-002`)

The ledger's `kind` list has no home for program output such as "blocks resurfaced" or "blocks awarded". I recorded four such claims as `spending` with a caveat that says so: `sf-blocks-resurfaced-as-of-2025-11`, `sf-blocks-planned-as-of-2025-11`, `sf-resurfacing-awards-blocks-2023-2025` and `sf-blocks-paved-2025`. I will move all four once the kind exists. That risks readers taking a count of blocks for a dollar figure. **Ask:** add `program_output` to the `kind` enum in `schemas/claims.schema.json` and to the list in CLAUDE.md. I have not changed either; CLAUDE.md is yours.

## 6. Added after step 2: can I query `service_details` for the pothole split?

The 311 case types have no "pothole" value, so I cannot separate potholes from other pavement defects without the third level of the taxonomy, `service_details`, which my query policy bars because I treated it as possible free text. The subtype field turned out to hold typed text in some records (one subtype label was a business name and address), so the caution was justified.

**Option A (recommended).** Allow grouped counts of `service_details` only within the pavement defect subtype, with the same minimum group size of 10, after first checking how many distinct values it has. If the values are a short categorical list (for example a handful of pothole and non-pothole labels), the split is safe and valuable. If it is mostly unique text, I stop and report.

**Option B.** Do not touch `service_details`. San Francisco's dossier then reports two things with their exact definitions: pavement defect requests from 311, and pothole service orders from the Public Works scorecard measure. It would say plainly that the 311 data does not isolate potholes.

I will not loosen the policy without your answer. Both options are workable; A gives a better answer if the field is clean.

**Item 5 applied.** `program_output` is now a kind in CLAUDE.md's list, the schema enum and a template comment. The four block claims were moved to it with their caveats rewritten, and a new check (`kind_units`) enforces that `spending` claims have a currency unit and `program_output` claims do not. Tests added.
