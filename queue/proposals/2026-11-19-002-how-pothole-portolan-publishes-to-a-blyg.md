---
id: 2026-11-19-002
from: agent (interactive session, reading blygger.org)
needs: supervisor decision
problem_relieved: The project has no blyg to publish to, and the Cloudflare project connected to this repository cannot host one as set up.
---

# How should Pothole Portolan publish to a blyg?

## What was learned (details and sources in `docs/blygger.md`)

- A blyg is, at the protocol level, plain static files plus RSS (`blyg.json`, `feed.xml`, `items/index.json`, `items/{id}.json`, `media/…`). The spec says the whole surface must be servable as static files.
- Blygger Studio is the reference client. It is a separate Cloudflare Worker application with its own D1 database and R2 bucket, installed from a clone of its own repository. It cannot be deployed from this repository.
- The Studio has a documented owner API for creating drafts, editing them and publishing new versions, with separate bearer-token scopes: `owner:read`, `owner:draft`, `owner:publish`, `owner:manage` and `reading:state`. The same operations are on MCP. This corrects the Phase 0 note that no write path exists.
- The Cloudflare build that was failing was connected to this repository and ran `npx wrangler deploy`. It now succeeds by serving a placeholder page from `site/`.

## The choice

**Option A: this repository emits a static blyg into `site/`.** The existing Cloudflare project serves it as static assets. Publishing is a commit to `site/`, which is already protected from the scheduled agent. Nothing new needs hosting, no token or Cloudflare credential is involved, and git remains the audit trail. The cost is building an emitter for the spec's item documents (ids, versions, content hashes, pins, feed and manifest). A static blyg cannot receive mentions, so CLAUDE.md's reader intake (mentions, quotes, forks, stubs, thumbs) would have nothing to read.

**Option B: a Blygger Studio of its own, in its own repository and Cloudflare project.** This repository then writes to it through the documented API with scoped tokens: a draft token in Phase 2 and a separate publish token only from Phase 3. It gets mention reception and versioned publishing for free, which the reader intake and Monitor behaviors assume. The supervisor has to create it: a Cloudflare account with D1 and R2, a subdomain, `npx wrangler login`, `npm run init`, an owner password, and then tokens stored as GitHub Actions secrets. The agent cannot do these steps. This repository would still need a client (`scripts/blygger_client`) written against the deployed Studio's OpenAPI contract, which changes between releases.

## Recommendation

Option B. CLAUDE.md's design (reader intake, monitoring with "what changed" versions, replies that need approval) is a Studio design, and its scopes map directly onto the phases. Option A is the lighter route if the project only needs to publish and does not need reader feedback; third-party tooling for moving a static blyg into a Studio later exists (`static-to-studio`, seen in search results and not examined), so starting static does not close the door.

## What I need from the supervisor

1. A decision: A or B.
2. For B: whether the Pothole Portolan blyg gets its own subdomain, which host name to allow on the agent's network, and when the Studio and tokens exist.
3. For B: approval to change `registry.yaml` credentials from `BLYGGER_READ_TOKEN` and `BLYGGER_WRITE_TOKEN` to `BLYGGER_READ_TOKEN`, `BLYGGER_DRAFT_TOKEN` and `BLYGGER_PUBLISH_TOKEN`.

## What is not blocked

Phase 2 stops at `queue/drafts/`, so nothing needs this decision to keep running. The placeholder page stays up. If the supervisor chooses B, the Cloudflare project connected to this repository can be disconnected, or left serving the placeholder.

## Not yet verified

The request body of `POST /items`, whether the Studio's Markdown renderer supports the footnotes and tables in the rendered dossiers, and whether tokens can be limited to one resource. They are listed in `docs/blygger.md`.
