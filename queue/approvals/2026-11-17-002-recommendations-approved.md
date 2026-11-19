---
id: 2026-11-17-002
decided_by: supervisor (Patrick Atwater, interactive session)
decision: approved, with one exception held back by the agent
subject: Proceed with the agent's recommendations on open proposals
---

The agent listed four open decisions and what it could do without them, and asked what input it needed. The supervisor replied: "sure do all the things you suggest you need to do".

**Interpretation, recorded so it can be corrected.** The agent read this as approving its recommended option for each item, and as authorizing it to edit the supervisor-owned files that those options touch:

| Item | Recommended option taken | Files touched |
|------|--------------------------|---------------|
| Proposal 002, personal-data check fix | Apply the change proposed there | `checks/run_checks.py`, `checks/publish.md`, tests |
| Proposal 001 item 5, `program_output` kind | Add the kind | `CLAUDE.md` (one list), `schemas/claims.schema.json`, `templates/dossier.md` (one comment), `checks/run_checks.py` (a kind and unit check) |
| Proposal 001 item 6, `service_details` | Allow grouped counts within the pavement defect subtype, minimum group size 10, typed-text guard on the response | `scripts/fetch_source.py` |
| Extract and Assess on the new sources | Proceed | `scripts/`, `cities/san-francisco/` |

**Held back.** Proposal 003 (rewriting branch history with a force-push) was not treated as approved. The agent had said that a general "go with your recommendations" would not count for it, and a force-push rewrites a published branch. The agent will ask again, and needs to know whether the repository is private or public.

**Not covered.** The supervisor's own read of `scripts/fetch_source.py` and the Phase 0 open questions remain open.
