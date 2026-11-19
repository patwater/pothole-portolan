"""Blygger client. A stub on purpose: nothing here talks to the network, and nothing may publish.

The Studio's owner API does have the write operations (POST /items to create a draft, PATCH
/items/{id} to edit it, POST /items/{id}/publish to publish a new version), each behind its own
scope (owner:draft, owner:publish). They are written up in docs/blygger.md. publish() still
refuses, for two reasons that are decisions and not missing information: this project has no
blyg to write to yet (proposal 2026-11-19-002 asks how it will be hosted), and publishing is
irreversible, so it stays off until the supervisor enables it (CLAUDE.md rule 3 and the phases).
"""


class WritePathUnavailable(RuntimeError):
    pass


def publish(*_args, **_kwargs):
    raise WritePathUnavailable(
        "Publishing is not enabled. The Studio API has the operations (see docs/blygger.md), but this "
        "project has no blyg to write to yet (proposal 2026-11-19-002) and the phase does not permit it.")
