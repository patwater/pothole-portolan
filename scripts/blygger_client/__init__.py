"""Blygger Studio client for Pothole Portolan.

- client.py: the owner API calls (read, draft, and a phase-gated publish). See docs/blygger.md.
- render.py: queued dossier draft to Studio-ready Markdown (footnotes become numbered notes).
- push_drafts.py: the Phase 2 job. It puts each queued dossier into the Studio as a private draft
  and never publishes; the supervisor publishes in the Studio.

Supervisor-owned and protected from the scheduled agent (checks/check_ownership.py). The token
comes from the environment of the workflow that runs push_drafts.py, never from a file.
"""
from .client import (  # noqa: F401
    USER_AGENT, StudioClient, StudioError, WritePathUnavailable, load_permissions, publish_allowed,
)
from .render import RenderError, to_blyg_markdown  # noqa: F401


def publish(*_args, **_kwargs):
    """Kept for older callers: there is no publish path outside StudioClient.publish, which checks
    the phase. Phase 2 never publishes from this repository."""
    raise WritePathUnavailable(
        "Publishing is not enabled from this repository in Phase 2. The supervisor publishes Studio "
        "drafts by hand; see docs/blygger.md.")
