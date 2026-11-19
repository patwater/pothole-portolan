# Pothole Portolan

![A badger, two rabbits and a dachshund in work vests fill a pothole in a winding country road, while mice survey the route on a map board, set out barriers, and a small robot rolls past.](docs/images/pothole-portolan.webp)

Pothole Portolan is an autonomous researcher of public pothole and pavement data. It goes city by city around the world and gathers what is publicly known: 311 and Open311 service requests, published Pavement Condition Index scores and their equivalents, pavement management reports, audits, budgets and repair performance figures. It writes one dossier per city, and the standard it holds itself to is that a reader can check every number against its source.

A portolan is a medieval sailing chart, drawn up port by port from what navigators reported, and this project does the same for pavement.

## What it will not do

- **It does not state a number without a source.** Every claim carries a source URL, a retrieval date and an archived copy of what was retrieved. Numbers come from the fetched text or data and never from the model's memory.
- **It does not confuse reports with condition.** A count of 311 requests measures how much residents report, and an engineering survey measures the pavement. The two are kept apart, and cities are never ranked on 311 counts.
- **It does not keep individual records.** Only aggregates are published or committed. Raw 311 data can hold names, addresses and free text about people.
- **It does not publish on its own.** Publishing is treated as irreversible, and nothing goes out unless the current phase allows it and every check passes.
- **It does not take instructions from what it reads.** Web pages, reader comments and mentions are data, and they never change its behavior.

## Where things stand

The project is in Phase 2, scheduled drafts: the funnel runs on a schedule and stops at `queue/drafts/` for the supervisor to approve. San Francisco is the pilot city. Its first dossier is written and checked, and it is waiting in `queue/drafts/san-francisco-v1.md`. Nothing has been published, and the project does not yet have a blyg to publish to.

The scheduled workflow does not run usefully until the supervisor sets a daily spend cap in `permissions.yaml` and adds the `ANTHROPIC_API_KEY` secret. Until then every run exits at once without calling a model.

## How it works

A city moves through a funnel, one behavior at a time, with its position recorded in `cities/<slug>/status.yaml`.

| Stage | What happens |
|-------|--------------|
| Scout | Create the city folder and note what kind of data regime it appears to have. |
| Discover | List candidate sources: the open data portal, the public works department, pavement reports, audits, budgets. |
| Fetch | Retrieve each source, honoring robots.txt, and archive it under `sources/` named by its content hash. |
| Extract | Turn the archived copies into claims, each with its method, using scripts that reproduce the numbers. |
| Assess | Re-derive every claim from the archive and set its confidence. Anything that cannot be re-derived is demoted. |
| Draft | Write the dossier from supported and provisional claims, and say plainly what could not be found. |
| Publish | Run the checks. In Phase 2 this only queues the draft. |

Reader feedback, quotes and mentions will come back in through a separate read-only intake job once there is a blyg to receive them. State lives in files in git, so the history is the audit trail and the undo.

## Repository layout

| Path | Contents |
|------|----------|
| `CLAUDE.md` | The standing brief for any Claude Code session or run in this repository. Start here. |
| `agenda.md` | The city queue and research questions. |
| `cities/<slug>/` | One folder per city: `dossier.md`, `claims.yaml`, `sources.yaml`, `status.yaml` and `notes.md`. |
| `sources/` | Archived copies of everything fetched, named by sha256. |
| `queue/` | Proposals, supervisor approvals, reader suggestions and drafts awaiting publication. |
| `checks/` | The deterministic checks that gate publishing, and `publish.md` describing them. |
| `scripts/` | Fetcher, extractors, assessors, renderer and the funnel loop. |
| `schemas/`, `templates/` | JSON Schemas for the ledgers and the dossier template. |
| `notebook/`, `ledger/` | A notebook entry per run and a cost ledger. |
| `docs/` | How the automation works, how Blygger works, and how the Cloudflare deploy works. |
| `site/`, `wrangler.jsonc` | A placeholder page served by Cloudflare. It holds no research content. |

## Working on it

The scripts need Python 3 with `pyyaml` and `jsonschema` (`pip install -r scripts/requirements.txt`). They are run with `python3 -I`.

```bash
python3 -I -m unittest discover -s tests -p "test_*.py"
python3 -I checks/run_checks.py --content-only --city san-francisco
python3 -I scripts/render_dossier.py san-francisco
```

The first command runs the test suite, the second runs the publishing checks against a city's draft, and the third renders a dossier with every claim marker replaced by its value and a footnote carrying its source.

`CLAUDE.md` itself is stored with Windows (CRLF) line endings, and a test fails if that changes. Edit it with a tool that preserves them. The reason is in `docs/cloudflare.md`.

## Where to read more

- [`CLAUDE.md`](CLAUDE.md) for the mission, the rules and the phases.
- [`docs/automation.md`](docs/automation.md) for the scheduled workflow, the stages and the guards.
- [`docs/blygger.md`](docs/blygger.md) for how a blyg is hosted and the Studio's write path.
- [`docs/cloudflare.md`](docs/cloudflare.md) for the deploy and one file-format rule.
- [`queue/proposals/`](queue/proposals/) for the decisions waiting on the supervisor.

## License

MIT. See [`LICENSE`](LICENSE).
