---
id: 2026-11-17-002
from: agent (Phase 2 automation task)
needs: supervisor decision
problem_relieved: Restricting Fetch to one script does not stop other scheduled behaviors from reaching the network around that script's robots.txt and rate-limit guard.
---

# Narrow shell and web access for the other scheduled behaviors

## The gap

Runners have open egress. The Phase 2 change made `scripts/fetch_source.py` the only network path for Fetch, and I confirmed with the real CLI that a command chained onto the one allowed command, such as `&& curl …`, is denied. But `registry.yaml` still gives several scheduled behaviors a general shell or a web tool:

| Behavior | Tools that reach the network or run arbitrary commands |
|---|---|
| scout | `Bash`, `WebFetch` |
| discover | `Bash`, `WebFetch`, `WebSearch` |
| extract | `Bash` |
| assess | `Bash` |
| monitor, weekly_review (manual today) | `Bash`, `WebFetch` (monitor) |

An unrestricted `Bash` can run `curl` against any host and ignore robots.txt (rule 8). `WebFetch` and `WebSearch` are Anthropic's tools, and I have not verified how they treat robots.txt. The anti-chaining result above also shows what a fix looks like: a scoped rule such as `Bash(python3 -I scripts/*)` denies anything else.

## Options

1. **Narrow Bash only.** Extract and Assess get `Bash(python3 -I scripts/*)` plus `Bash(python3 -I checks/run_checks.py *)`. Scout and Discover lose `Bash`. This removes the shell route and keeps discovery's web tools. I recommend it.
2. **Also route discovery through a script.** Give Discover a `scripts/search_source.py` with the same robots.txt and rate-limit guard as the fetcher and drop `WebFetch`. More work, and the only option that makes rule 8 mechanical for discovery.
3. **Accept the gap** and rely on the ownership guard and review of each commit.

## What I did not change

I changed only Fetch, as instructed. I did not narrow the other behaviors because I cannot test every tool pattern the agent's real extraction and assessment scripts need, and a pattern that is too tight would stall the funnel. After option 1, the first scheduled runs should be watched for denials.
