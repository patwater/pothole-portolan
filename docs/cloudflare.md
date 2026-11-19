# Cloudflare deploy and one file-format rule

This page is for a future session that has none of the context in which these were set up.

## What is deployed, and why `wrangler.jsonc` exists

A Cloudflare Workers Builds project is connected to this repository and runs `npx wrangler deploy` on a build. The repository has no website, so the first builds failed with `Could not detect a directory containing static files`: Wrangler found no config file, tried to configure itself, and found nothing to serve.

`wrangler.jsonc` fixes that by telling Wrangler to serve the static files in `site/`. `site/index.html` is a placeholder holding page. It describes the project in two sentences and says that no dossiers have been published. It holds no research content on purpose.

Checked on 2026-11-19: `npx wrangler deploy --dry-run` with Wrangler 4.165.0, the version of the failed build, reads the one file in `site/` and exits cleanly. Not checked: the Cloudflare dashboard itself, which this repository cannot see. If a build still fails, look at these in the dashboard under the Worker's Settings, then Builds:

- **Worker name.** `name` in `wrangler.jsonc` is `pothole-portolan`, the repository name and the dashboard default. It must match the Worker's name in the dashboard, or Workers Builds rejects the build. If the Worker has another name, change `name` here.
- **Branch.** Builds run for the branch the project is set to track, normally `main`. Changes on another branch do not affect it until they reach that branch.
- **Root directory.** It should be the repository root, where `wrangler.jsonc` is.

## This repository is not a Blygger Studio

A Blygger Studio is its own Cloudflare Worker application, with a D1 database and an R2 bucket, installed from a clone of the Studio's repository (https://blygger.org/start/). It cannot be deployed from this repository, and `site/` is not one. A blyg is, at the protocol level, only static files plus RSS, so a static blyg could in principle be served from `site/`; whether the project's blyg will be a static export or a Studio is proposal `2026-11-19-002`. See `docs/blygger.md`.

## Publishing rule

Everything in `site/` goes public on the next build. That makes it **publishing** under CLAUDE.md rule 3. The current phase stops at `queue/drafts/`, so do not put dossier content in `site/`. Publishing dossiers on this site is a decision for the supervisor, and it would be added as a deliberate step, for example a build that copies approved, rendered dossiers into `site/`. That step does not exist.

`wrangler.jsonc` and `site/` are protected from the scheduled agent in `checks/check_ownership.py`, like the other publishing paths (proposal `2026-11-19-001`, applied on the supervisor's instruction). Only the supervisor, or an interactive session acting on the supervisor's instruction, changes them.

## `CLAUDE.md` keeps CRLF line endings

`CLAUDE.md` was supplied with Windows (CRLF) line endings and must keep them. A script that opens and rewrites it in Python's text mode converts every line to LF. In version control that looks like the whole file changed, and it conflicts with any real edit made at the same time. That happened once and cost a merge to untangle.

`tests/test_line_endings.py` fails if any line is not CRLF, and its message gives the exact repair command. To edit the file, use the Edit tool, or in Python read and write with `open(path, newline='')`. Other files in the repository use LF.
