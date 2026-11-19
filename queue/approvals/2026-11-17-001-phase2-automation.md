---
id: 2026-11-17-001
decided_by: supervisor (Patrick Atwater, interactive session)
decision: approved
resolves: [2026-11-17-001]
subject: Phase 2 scheduled funnel, and decisions on proposal 2026-11-17-001
---

The supervisor instructed, in an interactive session on 2026-11-17: "For this task only, I authorize you to edit registry.yaml, checks/, schemas/, CLAUDE.md, and to create .github/. Do not edit permissions.yaml beyond what item 1 states. Publish nothing. Work on a new branch and open a PR." The goal is that the funnel runs automatically twice a week in GitHub Actions and stops at `queue/drafts/` (Phase 2).

## Decisions on proposal 2026-11-17-001 (as the supervisor stated them)

- **Section 5, claim kind.** Add `program_output` to the `kind` enum and to CLAUDE.md, and move the four block-count claims to it.
- **Section 1, robots.txt.** Record the Open311 endpoint and the Budget and Legislative Analyst audit as unavailable. This is option (a) in the proposal. Neither is to be fetched by working around robots.txt.
- **Phase.** Set the phase to 2 in `permissions.yaml` and CLAUDE.md. `daily_cap_usd` and `identities.owner` stay null for the supervisor to fill, and every scheduled run exits early while `daily_cap_usd` is null.

## What the instruction implies but does not state

- **Section 2, hosts.** Item 5 tells the agent to confirm that `scripts/fetch_source.py` reaches the `data.sf.gov` and `data.sfgov.org` metadata endpoints, aggregates only. I read this as approving steps 1 and 2 of the proposal's plan for those two hosts, with its stops unchanged: a bulk record-level download, or a request for an app token, ends the run and goes back to the supervisor.
- **Sections 3 and 4.** Not decided. Section 3 is a gateway fault with no decision to make. The supervisor's review of `scripts/fetch_source.py` (section 4) happens on the pull request.

## What this approval does not permit

It does not permit publishing, and `publish.agent_may_publish_in_phases` still lists only phases 3 and 4. It does not permit any change to `permissions.yaml` beyond the phase line. The authorization to edit `registry.yaml`, `checks/`, `schemas/`, `CLAUDE.md` and `.github/` is for this task only and ends with it.
