---
id: 2026-11-17-002
from: agent (Fetch, san-francisco, 311 plan step 1)
needs: supervisor decision (checks/ is supervisor-owned)
problem_relieved: The personal-data check fails on harmless dataset metadata, which would block every dataset-backed dossier at publish time.
---

# The personal-data check misreads dataset metadata as record-level data

## What happened

`checks/run_checks.py` reads the keys of an archived JSON file as if they were the columns of a data table, and fails any key that looks like a person, address or free-text column. The four metadata files archived in step 1 are dataset descriptions, not data, and contain keys such as `description`, `submissionDetails`, `numberOfComments` and `Publishing Details`. The check reports 11 failures for them, and a twelfth for `measure_description` in the Scorecard Measures rows archived in step 2 (the department's own description of a measure, not free text about a person). It found no email, phone or street-address pattern in any of them.

I checked the content by hand. Column definitions are included because the fetcher now strips the sample values (`cachedContents`) that were the real rule 7 risk. The files hold dataset names, descriptions, column names, types and descriptions, license and update information.

## Why it matters

A real publish runs this check without `--content-only`. As things stand, any city whose evidence includes open-data metadata could not pass it, even though the metadata is the safe kind. I did not edit the check, since `checks/` is yours (rule 5).

## Proposed change

1. In `check_personal_data`, apply the sensitive-column-name heuristic only to record-shaped data: CSV and TSV headers, JSONL rows, and JSON arrays of flat records. Skip it for schema documents, meaning a JSON object with a top-level `columns` list whose entries have a `fieldName`. A column *named* `address` in a schema is not an address.
2. For those schema documents, add the check that matters: fail if any `cachedContents` key remains, since that is where sample values hide. Keep the email, phone and street-address scans.
3. Add tests for both directions: a schema document with sensitive column names passes, and one that still contains `cachedContents` fails.

## Until you decide

`--content-only` runs for San Francisco will keep reporting these 11 failures. They cannot affect publishing in Phase 1 (you publish by hand), and I will not suppress them in the meantime.

## Related suggestion from step 2: a minimum-group-size check

The check did one thing very well in step 2: it flagged a street address inside a case-type label and led me to a real rule 7 problem (see the 311 notes). The cause was a record-level dataset returning groups of one. The fetcher now prevents this at the source, but the check could also confirm it. For archives whose source URL is a `/resource/` query on a record-level dataset, fail if any row has a count field (`cases`, `count`) below 10. That would catch an unthresholded query that reached the archive by another route.

I did not change `checks/`.
