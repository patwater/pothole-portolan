---
id: 2026-11-19-003
from: agent (interactive session, building the Studio client)
needs: supervisor decision
problem_relieved: Two new files that decide what goes to the Studio are not yet protected from the scheduled agent.
---

# Protect the Studio item ledger and the client's tests from the scheduled agent

## What is already protected

`scripts/blygger_client/` is on the ownership guard's list, so the client, the renderer and `push_drafts.py` cannot be changed by a scheduled run. `.github/` is supervisor-owned, which covers `blyg-drafts.yml`.

## What is not, and why it matters

- `ledger/blyg_items.yaml` maps each city to its Studio item. A scheduled run that edited it could point a city's next draft at a different item, so that `push_drafts.py` overwrote that item's working copy. The draft token cannot publish, so the harm is limited to drafts, but the file is written by a workflow and should be treated like `ledger/costs.csv`.
- `tests/test_blygger_client.py` is the test the workflow runs before sending anything. An agent that could weaken it could hide a broken renderer.

## The change

In `checks/check_ownership.py`, add `ledger/blyg_items.yaml` to `AGENT_RUN_ONLY` and `tests/test_blygger_client.py` to `ALSO_PROTECTED`, and add matching cases to `tests/test_ownership.py`. I tried to make this edit in the interactive session, and the permission system blocked it as a change to the agent's own guard, so it is written up here instead.
