# Publish checks

Nothing is published unless the current phase permits it and every check below passes. Run them with:

```bash
python3 -I checks/run_checks.py --city <slug>
```

The command exits 0 only when every gate passes. Add `--content-only` to check a draft before the phase permits publishing; a real publish must run without it. Warnings never fail a run, but read them.

## Gates

| # | Check | What it enforces | Script |
|---|-------|------------------|--------|
| 0 | `phase_gate` | `PAUSE` does not exist, and `permissions.yaml` lists the current phase under `publish.agent_may_publish_in_phases`. | `checks/run_checks.py` |
| 1 | `schema` | `claims.yaml`, `sources.yaml` and `dossier.md` exist, and the two ledgers validate against `schemas/`. Ids are unique. A `measured_condition` claim carries the full `condition_index` block. | `scripts/validate.py` |
| 2 | `provenance` | Every claim has a source URL, a valid retrieval date that is not in the future, and an archive path that sources.yaml lists as fetched. | `checks/run_checks.py` |
| 3 | `archives` | Every archive path exists, and the sha256 of its content equals its filename. | `checks/run_checks.py` |
| 4 | `personal_data` | No data files under `cities/`. No emails, phone numbers or street addresses in published text. Archived CSV and other JSON have no columns that suggest names, addresses, contact details or free text. Dataset descriptions (JSON with a `columns` list) are exempt from the column-name test but must hold no `cachedContents` sample values. Responses from registered portal datasets must have no group under 10 cases and no text field with more than 100 distinct values. | `checks/run_checks.py` |
| 4b | `kind_units` | A `spending` claim has a currency unit, and a `program_output` claim (blocks resurfaced and similar counts of work) does not, so counts of work are never summed or read as money. | `checks/run_checks.py` |
| 5 | `demand_vs_condition` | A `reported_demand` statement counts requests or reports and uses no condition language. A paragraph that cites reported demand does not use condition language without an explicit disclaimer. No ranking language on 311 counts. Demand claims do not sit under condition headings, and the reverse. | `checks/run_checks.py` |
| 6 | `dossier` | Front matter is valid and matches the folder. Every `{{claim:id}}` resolves to a claim that is supported or provisional. A "What could not be found" section exists. | `checks/run_checks.py` |

## Manual items

The scripts cannot decide these, so the supervisor or the Assess behavior confirms them before a publish.

- [ ] Each number was re-derived from the archive during Assess, not copied from the extraction step.
- [ ] Units and periods in the dossier match the claim ledger.
- [ ] Condition indices are not compared across methods unless a published crosswalk is cited.
- [ ] Archived PDFs and other binary files, which the personal-data check reports as unscanned, were reviewed by hand.
- [ ] The dossier says plainly what could not be found, and the list is honest.
- [ ] The bot's user agent was honest and robots.txt was respected for every fetch.

## Known limits

- The personal-data check is heuristic. It catches obvious patterns and column names, not every disclosure.
- Numbers typed by hand in prose are reported as warnings, not failures, because years and small counts are legitimate.
- The checks cannot tell whether a source is the right one for a claim. That is Assess work.
