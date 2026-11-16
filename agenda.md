# Agenda

Agent-maintained. Owner suggestions may reorder this file; public suggestions wait for approval.

## Proposed pilot cities (Phase 1)

These five are a proposal for the supervisor to confirm. The one-line regime descriptions come from general background knowledge, not from fetched sources, so each is a hypothesis that the Scout behavior must verify before anything about it is written into a dossier. None of it is a claim.

| Order | Slug | City | Why its data regime should differ from the others (hypothesis) |
|-------|------|------|------------------------------------------------------------------|
| 1 | san-francisco | San Francisco, US | A city that appears to publish both an engineering pavement condition score and a record-level 311 feed, so it tests how well the two kinds of evidence can be kept apart. |
| 2 | chicago | Chicago, US | A very large open 311 dataset on a standard portal with repair-stage detail, but no obvious network-wide condition index, so it tests a demand-heavy regime where the condition side may be missing. |
| 3 | london | London, UK | A national statistics regime in which the Department for Transport collects road condition indicators by highway authority, and complaints are scattered across 33 boroughs and third-party reporting sites. |
| 4 | bogota | Bogotá, Colombia | A non-English municipal regime where a city institute runs the pavement survey and the open data lives in Spanish, so it tests discovery and translation without losing method detail. |
| 5 | nairobi | Nairobi, Kenya | A sparse-data regime where little may be published beyond budgets, tenders, news and reports, so it tests how the dossier handles "not found" as the main finding. |

## Queue

1. san-francisco: status `discovered` (2026-11-16), 13 sources listed; next behavior is Fetch. See `cities/san-francisco/notes.md`.
2. chicago: status `proposed`
3. london: status `proposed`
4. bogota: status `proposed`
5. nairobi: status `proposed`

## Research questions

- Which cities publish both a condition index and a record-level demand feed, and how do the two relate?
- How many cities publish the share of their network that was actually surveyed?
