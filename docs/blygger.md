# Blygger Studio: what the write path looks like today

Investigated in Phase 0 on 2026-11-16. Nothing was written or published during this investigation.

## Where this came from

The only contract available to this project is the one the session's Blyg connector exposes. No Studio repository or written API specification was found in this repo. The facts below come from two calls the connector allows: `getCapabilities` and `getSettings`. Anything not listed there is unknown, not absent from Blygger.

## Endpoints

| Role | URL |
|------|-----|
| Public base | https://blyg.pioneeringspirit.xyz |
| Studio | https://blyg.pioneeringspirit.xyz/studio |
| API | https://blyg.pioneeringspirit.xyz/api |
| Auth issuer | https://blyg.pioneeringspirit.xyz/studio/auth |
| MCP | https://blyg.pioneeringspirit.xyz/studio/mcp |
| Media | https://blyg.pioneeringspirit.xyz/media |

Contract version reported: `5.10.0`.

## Operations in the contract

`getCapabilities` lists 39 operations. All of them are reads:

`batchRead`, `classifyLinks`, `getAiModels`, `getCapabilities`, `getChanges`, `getForkOptions`, `getHopper`, `getImportedHistory`, `getImportedItem`, `getImportedVersion`, `getItem`, `getItemFreshness`, `getItemSummary`, `getMentionSource`, `getMentionSummary`, `getReadingSummary`, `getSettings`, `getShelf`, `getSignalSummary`, `getSubscription`, `getUpdateState`, `getVersion`, `listBrowse`, `listContacts`, `listHopperMemberships`, `listHoppers`, `listImportedReading`, `listInteractions`, `listItemVersions`, `listItems`, `listMentionGroups`, `listMentions`, `listReading`, `listSignals`, `listStaleThreads`, `listSubscriptions`, `listThumbs`, `peekItem`, `search`.

## Scopes seen

Only two scope labels appear in the connector's descriptions.

- `any authenticated identity`: `getCapabilities`.
- `owner:read`: every other operation that was inspected (`getSettings`, `listMentions`, `listInteractions`, `listItemVersions`, `listThumbs`, and `listItems` by behavior).

No write scope, such as `owner:write` or `items:publish`, is named anywhere.

## What each project need maps to

| Need | Operation(s) available | Status |
|------|------------------------|--------|
| Create a draft | none | **Missing** |
| Publish | none | **Missing** |
| Publish a new version of an item | none; `listItemVersions` and `getVersion` read versions only | **Missing** |
| Retract or delete | none | Missing, and needs supervisor approval anyway |
| Read mentions | `listMentions`, `listMentionGroups`, `getMentionSummary`, `getMentionSource` | Available, scope `owner:read` |
| Read quotes, forks, stubs | `listInteractions` with `kind` of `quote`, `fork` or `stub` | Available, scope `owner:read` |
| Read thumbs | `listThumbs`, `listInteractions` with `kind` of `thumb_up`, `thumb_down`, `thumb_clear` | Available, scope `owner:read` |
| Read a published item or its versions | `getItem`, `peekItem`, `listItemVersions`, `getVersion` | Available, scope `owner:read` |

## Problems for the design

1. **There is no documented write path.** Phase 2 and Phase 3 both depend on creating drafts and publishing. `scripts/blygger_client` is a stub that refuses to run until a contract exists. It does not guess an endpoint.
2. **A read-only token is not narrow.** Reader intake needs mentions, interactions and thumbs, and those require `owner:read`. The same scope also reads settings, subscriptions, contacts and the whole item list, which is more than intake needs. CLAUDE.md asks for a read-only token with no publish credential; `owner:read` satisfies the second half but not the spirit of the first. A narrower scope, for example mentions and interactions only, would fit better.
3. **No separate publish credential is visible.** The contract does not say whether publishing is a distinct scope from drafting, which the Phase 3 gating relies on.
4. **Paging matters.** `listItems` called without a limit returned about 194,000 characters in one response. Every client call must pass `limit` and follow `cursor` where the operation supports them.
5. **Mentions mix trust tiers.** `listMentions` returns receipts with `direction` of inbound or outbound and a `verifiedAt` field. Whether `verifiedAt` establishes identity strongly enough to map a mention to the owner, trusted or public tier is not documented, and the tier rules in `permissions.yaml` depend on it.
6. **The connector in this session is not a scheduler credential.** CLAUDE.md says credentials are injected as environment variables. This session reached Blygger through an attached connector, so how a scheduled headless run authenticates is undecided. The `registry.yaml` placeholders `BLYGGER_READ_TOKEN` and `BLYGGER_WRITE_TOKEN` assume a token model that has not been confirmed.

## What is needed from the supervisor

- The Studio repository, or the API contract document, that defines draft creation, publishing and versioning.
- The intended scope names for a read-only intake token and a publish token.
- Whether `verifiedAt` on a mention can be treated as an identity check for tiering.
- How scheduled runs should authenticate.
