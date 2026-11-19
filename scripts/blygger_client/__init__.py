"""Blygger client. Phase 0 stub: nothing here talks to the network.

The Studio API contract visible to this project (version 5.10.0) lists read
operations only. There is no documented operation for creating a draft,
publishing, or versioning, so publish() refuses rather than guess an endpoint.
See docs/blygger.md for what exists and what is missing.
"""


class WritePathUnavailable(RuntimeError):
    pass


def publish(*_args, **_kwargs):
    raise WritePathUnavailable(
        "No Blygger write operation is documented yet. See docs/blygger.md; "
        "ask the supervisor for the Studio repo or API contract.")
