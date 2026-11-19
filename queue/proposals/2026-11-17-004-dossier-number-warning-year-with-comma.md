---
id: 2026-11-17-004
from: agent (Draft, san-francisco)
needs: supervisor decision (checks/ is supervisor-owned)
problem_relieved: The dossier check warns about years that are followed by a comma, which buries the warnings that matter.
---

# The "number typed by hand" warning does not recognize a year followed by a comma

## What happened

`check_dossier` warns when a number is typed into prose instead of a claim marker, and it skips years. Its number pattern captures a trailing comma, so "in 2025, the city" is read as the token "2025," and is no longer recognized as a year. The first San Francisco draft produced 22 warnings, and 21 of them were years such as "2023," and "2025,". The one real finding (a typed "311") was hard to see among them.

## Proposed change

In `check_dossier`, strip trailing commas and periods from a matched number before the year test. Add a test that "in 2025, the city" produces no warning and that a typed "1,234" still does.

## Effect if not changed

Nothing breaks, since warnings never fail a run. The cost is that real hand-typed numbers are easy to miss, and a dossier writer is tempted to contort sentences to avoid a trailing comma after a year.

I did not change `checks/`.
