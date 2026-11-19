---
slug: <city-slug>
city: <City name>
version: 1
drafted: YYYY-MM-DD
ledger: claims.yaml
---
# <City name>: potholes and pavement condition

<!--
Drafting rules (comments are stripped by the checks and the renderer):
- Every number is written as a claim marker, {{claim:<id>}}, never typed by hand.
  The renderer replaces the marker with the value, unit and a footnote carrying
  the source URL, retrieval date and archive path.
- Use supported and provisional claims only. Never cite a speculative claim.
- Reported demand (311 counts) goes under "What residents reported". Measured
  condition (PCI or equivalent) goes under "What the pavement survey measures".
  Never present one as the other, and never rank cities on 311 counts.
- Do not convert between condition indices unless a published crosswalk is cited.
- Say plainly what could not be found.
-->

## Summary

<!-- Two or three sentences. Describe what exists and what does not. -->

## Data regime

<!-- What kind of regime this city has: open portal, Open311 endpoint, published
     survey, audit-only, or sparse. Link each statement to a source. -->

## What the pavement survey measures

<!-- Measured condition. Name the index, the scale, the survey year, the share of
     the network surveyed, and the survey method, using {{claim:<id>}} markers. -->

## What residents reported

<!-- Reported demand. State plainly that these counts measure how much residents
     report, which depends on app adoption, trust and demographics, and that they
     are not a measure of road condition. Use {{claim:<id>}} markers. -->

## Spending and repair performance

<!-- Spending (dollars), program output (such as blocks resurfaced, which is not a dollar figure), response times and backlog claims, each as a {{claim:<id>}} marker. -->

## What could not be found

<!-- Required. List each source or figure that was sought and not found, with the
     reason (not published, behind a login, unreachable, ambiguous). -->

## Sources

<!-- The renderer appends the full source list from sources.yaml. -->

## Version history

<!-- Version 1: first publication. Later versions say what changed and why. -->
