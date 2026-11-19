---
id: 2026-11-19-001
decided_by: supervisor (Patrick Atwater, interactive session)
decision: approved
subject: Fix the failing Cloudflare build, and keep CLAUDE.md's line endings from being rewritten
---

The supervisor wrote, on 2026-11-19: "I don't understand though do whatever makes it cleaner for a future version of claude code that doesn't have this session's context. I don't plan to review manually. also please fix the blyg setup issues", and pasted a Cloudflare Workers Builds log ending in `Could not detect a directory containing static files`.

**What the agent did on that instruction.**

- Added `wrangler.jsonc` and a placeholder `site/index.html` so `npx wrangler deploy` succeeds. The page carries no research content.
- Added `tests/test_line_endings.py` so `CLAUDE.md` cannot silently lose its CRLF line endings again, and `docs/cloudflare.md` to explain both to a later session.

**What this does not permit.** It does not permit putting dossier content in `site/`, which would be publishing. It does not extend to editing `checks/check_ownership.py`: the agent tried to add `site/` and `wrangler.jsonc` to the protected paths, the permission system blocked it, and the change is written up as proposal `2026-11-19-001` for the supervisor to decide.

**What the instruction did not decide.** What the "blyg" deployment is meant to be. No documentation for deploying a Blygger site was found, so the fix is a neutral holding page and not a Blygger instance.

## Follow-up instruction, same day

The supervisor wrote: "can you go ahead and do the site/ and wrangler.jsonc you wanted and then push", and pointed to blygger.org for what the agent needs to understand the blyg setup. That names the protection change in proposal `2026-11-19-001`, so the agent made it: `wrangler.jsonc` and `site/` are now protected from the scheduled agent in `checks/check_ownership.py`, with tests. It does not extend to editing any other protected file. The supervisor's pointer to blygger.org is an instruction to read it, which needs that host added to the environment's network allowlist and is requested separately through the approval prompt.
