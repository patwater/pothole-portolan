# Blygger: how a blyg is hosted, and how this project writes to one

Researched on 2026-11-19 from blygger.org and the Blygger Studio repository's own documentation. Nothing was written or published during the research.

**This replaces the Phase 0 version of this page, which said no write operation exists. That was wrong.** The Phase 0 conclusion came from a connector whose grant could only read, so it listed only reads. The Studio has a documented API for creating drafts, publishing and versioning, with separate scopes for each (below).

Sources read:

- https://blygger.org/start/ (how to host a blyg)
- https://blygger.org/spec/0.4/ (the protocol; the "living spec" is the highest-numbered version)
- https://raw.githubusercontent.com/blygger/blygger-studio/main/README.md (the reference client)
- https://raw.githubusercontent.com/blygger/blygger-studio/main/docs/client-access.md (tokens and scopes)
- https://raw.githubusercontent.com/blygger/blygger-studio/main/docs/api.md (the owner API)
- https://raw.githubusercontent.com/blygger/blygger-studio/main/docs/auth-deployment-hardening.md (limits)

## Two layers

**The protocol** is a set of static files plus RSS. The spec requires that "the entire surface MUST be servable as plain static files", so a blyg can live on a plain file host. The required files, relative to the blyg's origin, are `blyg.json` (manifest), `feed.xml` (RSS 2.0), `items/index.json` (archive index), `items/{id}.json` (one document per item, with `content_md`, `content_html`, `content_hash` and a version number), `items/{id}/v{n}.json` (pinned versions) and `media/…`. Item ids are 128 random bits written as 26 lowercase Crockford base32 characters. `content_md` must not contain control characters other than tab, line feed and carriage return, and should be in Unicode Normalization Form C. The spec says nothing about which Markdown features are supported (footnotes, tables), because the publisher renders `content_html` itself.

**Blygger Studio** is the reference client: a Cloudflare Worker that publishes, subscribes and receives mentions, while its published output stays static files. Its install is `git clone` of the Studio repository, then `npm ci`, `npx wrangler login`, `npm run init` and `npm run deploy`. `init` asks for a Cloudflare account and domain, creates a D1 database (binding `DB`) and an R2 bucket (binding `MEDIA`), applies migrations and sets the secrets `OWNER_PASSWORD` and `COOKIE_SECRET`. The blyg is then at a subdomain such as `https://blyg.example.com/`, with the Studio at `/studio`. **A Studio is its own application with its own `wrangler.jsonc`, installed from a clone of the Studio repository. It cannot be deployed from this repository.**

## The write path

Authentication is a bearer token. A Studio owner creates manual tokens, or approves OAuth grants, on the Studio's access page, and each token carries explicit scopes. Scopes do not imply each other.

| Scope | Allows |
|-------|--------|
| `owner:read` | Private reads: drafts, reading material, media, settings and history |
| `owner:draft` | Creating, editing, restoring and deleting drafts, media uploads, preview and configured AI generation |
| `owner:publish` | Publication, withdrawal, refresh, permanent pins, public response display and media deletion |
| `owner:manage` | Settings, subscriptions, signals, collections and response moderation |
| `reading:state` | Marking reading entries read or unread |

The REST routes below are under `{mount}/api`, and the same operations are available over MCP at `{mount}/studio/mcp`. A call without the needed scope gets an HTTP 403 scope challenge. The owner can download the deployed OpenAPI contract at `{mount}/api/openapi.json`.

| Need | Route | Scope |
|------|-------|-------|
| Create a draft | `POST /items` | `owner:draft` |
| Edit a draft | `PATCH /items/{id}` | `owner:draft` |
| Publish (a new version of the same item each time) | `POST /items/{id}/publish`, with an optional publication note | `owner:publish` |
| Withdraw | `POST /items/{id}/withdraw` | `owner:publish` |
| Pin a version permanently | `PUT /items/{id}/versions/{version}/pin` | `owner:publish` |
| Read items and versions | `GET /items`, `GET /items/{id}`, `GET /items/{id}/versions` | `owner:read` |
| Read mentions | `GET /mentions?direction=inbound` or `outbound` | `owner:read` |
| Read capabilities | `GET /capabilities` | any valid grant |

The spec says a publish event increases an item's `version` by exactly one, and that ids never change across versions, which is what makes "publish a new version that says what changed" possible. Writes are rate limited (the hardening document lists defaults such as 120 owner writes and 60 delegated writes per minute).

## What this project's supervisor already has

The supervisor's own blyg is at https://blyg.pioneeringspirit.xyz, with the Studio at `/studio`, the API at `/api`, the MCP endpoint at `/studio/mcp` and the auth issuer at `/studio/auth`. The connector used in Phase 0 reported contract version 5.10.0 with 39 operations, all of them reads. That is what a read-scoped grant shows, and it is not evidence that the write operations are missing. The project's own blyg for Pothole Portolan does not exist yet: nothing in this repository is a Studio, and whether it will be one is the open decision in proposal `2026-11-19-002`.

## How the scopes fit the project

- **Reader intake** needs mentions and interactions, which need `owner:read`. That scope also reads drafts, settings and history, which is broader than intake needs, but it has no write power. It satisfies "read-only token, no publish credential".
- **Phase 2** (drafts only) could use an `owner:draft` token to put a draft in the Studio without making it public. It does not need `owner:publish`.
- **Phase 3** (gated publishing) is the first phase that needs `owner:publish`, and it should be a separate token from the draft token, so that a run that only drafts cannot publish.
- `registry.yaml` currently names two credentials, `BLYGGER_READ_TOKEN` and `BLYGGER_WRITE_TOKEN`. A cleaner split is `BLYGGER_READ_TOKEN`, `BLYGGER_DRAFT_TOKEN` and `BLYGGER_PUBLISH_TOKEN`. `registry.yaml` is supervisor-owned, so that change is in the proposal and not made.

## Still unknown or unverified

- The exact request body for `POST /items` (see "Create an item" in `docs/api.md`) and the content limits.
- Whether the Studio's Markdown renderer supports footnotes and tables. The rendered Pothole Portolan drafts use both.
- Whether a token can be restricted to one resource beyond its scopes (the client-access document mentions "resource-bound" tokens).
- Whether `verifiedAt` on a mention is strong enough to map a mention to the owner, trusted or public tier in `permissions.yaml`.
- How a scheduled run authenticates in practice: tokens would be stored as GitHub Actions secrets, which the supervisor must create.
- The Studio API is called private and its contract changes with releases (the project's own blyg announced contract 5.13.0 on 2026-11-19, while the supervisor's Studio reported 5.10.0). A client has to be tested against the supervisor's deployed version.

## Paging and cost

`listItems` called without a limit returned about 194,000 characters in one response. Every client call must pass a limit and follow cursors where the operation supports them.

## A working example: how the World Machines blyg is automated

Researched on 2026-11-19 at the supervisor's request, from https://blyg.worldmachines.org/ (its `blyg.json`, `items/index.json` and 26 item documents) and from the public repository `worldmachines/worldmachines` on GitHub (files `blyg-shell/README.md`, `.github/workflows/blyg-sync.yml`, `.github/workflows/blyg-front.yml`, `website/scripts/blyg_sync.py`, `website/scripts/blyg_series.py`). Nothing was written to either site, and no code was copied, because that repository has no license file.

**It is a stock Blygger Studio driven by GitHub Actions.** The manifest names `blygger-studio/0.64.1` as the generator and declares a `webmention` endpoint, `/studio` redirects to a sign-in, and `/api/capabilities` answers 401 without a token. The shell README says the Studio is deployed from a separate private checkout, unforked, and that a small second Worker sits in front of it only to add the site's navigation bar.

**Publishing is a script, not a person.** Two scheduled workflows in the public repository run stdlib Python scripts that call the Studio REST API with a bearer token held as a GitHub Actions secret:

- `blyg-sync.yml`, at 06:00 and 18:00 UTC, collects posts that members file into their own hoppers, files them into the World Machines `members` hopper, and publishes a digest of them.
- `blyg-front.yml`, at 06:30 and 18:30 UTC, writes one series post a day (a weekday rotation of six formats) and republishes the front-page thread. Its only git write is `tools/blyg-front/history.json`, which records what was featured so that a subject is not reused within 90 days.

Each post follows the same sequence of calls: `POST /items` with `kind: thread` and the Markdown creates a draft, `POST /items/{id}/generate` asks the Studio to fill each `[TK]` scope, and `POST /items/{id}/publish` publishes it, after which the item is filed into a hopper. Item writes carry `expectedRevision`, and a 409 revision conflict is re-read and retried once. The item documents agree with this: each recent post was created and then published about ten seconds later, as version 1.

**The AI writes only inside marked scopes.** The script assembles everything deterministic itself: headings, links, the list of source posts, and quotes as partial transclusions whose text the Studio checks is a verbatim substring of the target. Only the `[TK]` scopes are written by a model, which is the Studio's own configured model (`@cf/google/gemma-4-26b-a4b-it` on Cloudflare Workers AI). Each published item then carries a `generated` field naming the model, the time, and every source item and version the scope drew on. The front-page thread is at version 26, and every version has a changelog note such as "minor: today's featured note is Legibility".

**Operational limits the scripts work around:**

- Studio REST tokens expire after at most 30 days, so a person has to mint a new one and update the secret each month. The scripts fail with renewal instructions on a 401 or 403.
- Studio AI generation has a daily budget per grant (the scripts cite 10 calls a grant and 40 for the whole blyg, and 20 for the digest token). A 429 from `generate` is that budget, is never retried, and leaves the draft for the next run to resume.
- The scripts say they speak Studio 0.51's private API (contract 5.2.0), while the live Studio reports 0.64.1, so the contract has moved under them and they still work. A client should be tested against the deployed version anyway.

**What carries over to Pothole Portolan.** The pattern fits the existing funnel workflow: a protected script in `scripts/blygger_client/` that creates a draft, publishes it with a changelog note, files it into a hopper, and writes the item id, version and `content_hash` to a publish log in git, so git still records exactly what went public. The main difference is that Pothole Portolan's prose is written by Claude in the funnel, with numbers filled from the claim ledger, rather than by the Studio's model inside `[TK]` scopes. Whether the Studio lets a client record its own `generated` provenance for text it wrote outside a `generate` call is not yet verified; `docs/api.md` mentions "client-recorded generation provenance" without saying more here.
