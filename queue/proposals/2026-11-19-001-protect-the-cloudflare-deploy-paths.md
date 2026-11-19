---
id: 2026-11-19-001
from: agent (interactive session, deploy fix)
needs: supervisor decision (checks/ is supervisor-owned)
problem_relieved: The Cloudflare deploy now serves site/, so a scheduled agent that edits site/ would publish without approval.
---

# Protect `wrangler.jsonc` and `site/` from the scheduled agent

## The problem

To fix the failing Cloudflare build, `wrangler.jsonc` and `site/index.html` were added (see `docs/cloudflare.md`). Anything in `site/` goes live on the next build, which is publishing under CLAUDE.md rule 3. The Phase 2 loop lets the agent write files, and `checks/check_ownership.py` is what stops it from changing paths that decide what is published. `site/` and the deploy config are not on that list yet.

## The change

In `checks/check_ownership.py`, add these entries to `ALSO_PROTECTED`, next to `.gitattributes`:

```
"wrangler.jsonc", "wrangler.json", "wrangler.toml", "site/",
```

In `tests/test_ownership.py`, add these paths to `test_extra_protected_paths_fail`:

```
"wrangler.jsonc", "wrangler.toml", "site/index.html", "site/dossiers/san-francisco.html"
```

Update the docstring list in `check_ownership.py` to mention that `site/` is the Cloudflare deploy.

## Why it is a proposal

The agent attempted this edit in the same session and the permission system blocked it, because it is a change to the guard that restricts the agent. The agent did not try another route. It needs your decision, or an explicit instruction that names this file.

## Risk until it is applied

Low and temporary. Scheduled runs cannot start while `spend.daily_cap_usd` is null and no `ANTHROPIC_API_KEY` secret exists, and the workflow is not on the branch Cloudflare builds unless it has been merged there. It becomes real once the funnel is switched on.

## Status: applied 2026-11-19

The supervisor then wrote: "can you go ahead and do the site/ and wrangler.jsonc you wanted and then push". That names this change, so the agent made it. `wrangler.jsonc`, `wrangler.json`, `wrangler.toml` and `site/` are now in `ALSO_PROTECTED` in `checks/check_ownership.py`, its docstring mentions the Cloudflare deploy, and `tests/test_ownership.py` checks four of those paths. All tests pass. The scheduled agent can no longer change the deploy config or anything in `site/`, so only the supervisor, or an interactive session acting on the supervisor's instruction, can publish through it.
