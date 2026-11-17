# San Francisco: working notes

Behavior: Scout, 2026-11-16. Nothing here is a claim. These are leads seen in web search results only; no page was fetched or archived, and no figure below may be used until Fetch archives its source and Extract writes a claim.

## Data regime (appears to be)

**Both an engineering condition measure and a record-level demand feed are published, from separate bodies.** This is the "dual evidence" regime that the pilot agenda proposed. The hypothesis in `agenda.md` looks right on first read, with the details below still to confirm.

| Strand | What appears to exist | Kind when extracted | Lead |
|--------|-----------------------|---------------------|------|
| Condition | A network Pavement Condition Index on a 0 to 100 scale, with MTC StreetSaver survey as the apparent method, reported by San Francisco Public Works in an end-of-year release and in capital budget presentations | `measured_condition` | https://www.sf.gov/news/san-franciscos-road-conditions-improve-ranked-highest-large-bay-area-cities-annual-roads and https://sfpublicworks.org/node/35600 |
| Demand | DataSF "311 Cases" dataset (id `vw6y-z8j6`), cases since 2008, refreshed about daily, with an Open311 API route | `reported_demand` | https://support.datasf.org/help/311-case-data-faq and https://datasf.gitbook.io/datasf-dataset-explainers/311-cases |
| Response time | A city pothole performance measure, the share of pothole requests addressed within a 72-hour target, drawn from the DataSF Scorecards dataset with roughly a one-month lag | `response_time` | https://www.sf.gov/data/pothole-response |
| Spending and program | Resurfacing program figures in Public Works commission updates, capital budget presentations and a county transportation authority program document | `spending` | https://sfpublicworks.org/sites/default/files/Commissions/Nov%2013%202025/Item%205_PWC%20Street%20Resurfacing%20Capital%20Update%202025-11-13.pdf |

## Things to watch for in later behaviors

- **Method detail for Extract.** The condition strand needs the index name, scale, survey year, share of the network surveyed and survey method. The search snippets say the survey is done by raters in MTC's StreetSaver program, but the share of the network surveyed was not seen.
- **Two authors for one score.** The score appears to be produced under MTC's program and reported by the city. Fetch should archive the primary MTC or city source, not a news release alone, so the claim points to where the number originates.
- **Demand is not condition.** The 311 dataset says each report may not be unique and not every case has coordinates. The count must stay `reported_demand`, with that caveat, and never be set beside the PCI as if it measured the same thing.
- **Free text and addresses.** The 311 dataset is record-level and carries locations. Rule 7 applies: archive only aggregates, and the personal-data check will block any column that looks like an address or free-text field.
- **Pothole definition.** Which 311 case types and categories count as a pothole needs to be read from the dataset's own documentation, not assumed.
- **Ranking language.** A city release describes San Francisco as ranking highest among large Bay Area cities on PCI. That is a condition comparison, which is allowed, but it is the city's framing and a dossier should cite the underlying MTC data if it uses it.
- **Resurfacing is not purely condition-driven.** The city says it weighs transit and bike-lane use and constructability as well as PCI, and also lists resident inquiries as an input. That bears on how spending claims relate to condition claims.

## Open questions

1. Does MTC publish segment-level or jurisdiction-level PCI data that Fetch can archive under its terms of use?
2. What exactly counts as a pothole in the 311 case taxonomy, and has that definition changed over time?
3. Is the 72-hour response measure's methodology documented well enough to extract with a stated method?
4. Does the city publish a pavement management report or a budget and legislative analyst document that states the share of the network surveyed?

## Discover findings (2026-11-16)

Thirteen candidate sources are listed in `sources.yaml`, all with status `listed`. Nothing has been fetched.

**Discrepancies for Assess to resolve from fetched text, not from search snippets:**

1. **Which year is the score of 75?** The city's January 2026 release says 75 in 2025. The MTC Vital Signs page, per the result, says San Francisco County averaged 75 in 2024 and describes a three-year moving average. A January 2024 city release was also reported as giving 75, for 2023. These may be different measures (a calendar-year score against a three-year moving average) or different reporting conventions, and a claim must state the period and averaging method exactly as the source does.
2. **Rating bands differ.** The MTC page reportedly calls 64 to 84 "good" and 85 to 100 "excellent". The city scorecard reportedly calls 70 to 84 "good". The dossier must quote the band from whichever source a claim uses and not mix them.
3. **Response-time target.** The scorecard describes a 72-hour goal, while a 2021 audit gives the departmental goal as 90 percent within 72 hours. Confirm the target and the measured share from the primary documents.

**Gaps:**

- The canonical data.sfgov.org landing pages for the 311 Cases dataset and the Scorecards dataset were not seen in results. Fetch must resolve them rather than build URLs from the dataset id.
- No national statistics body fits as a source for San Francisco. Federal highway data is a possible later lead but was not searched, so it is not listed.
- No Controller audit specific to pothole repair was found. The Budget and Legislative Analyst audit of the resurfacing program is the nearest.
- The share of the network surveyed was not found in any snippet, so it is still unknown for the `condition_index` block.

**Excluded on purpose:** one gitbook page from a different host than the DataSF explainer contained embedded instructions in its search result. It was not listed. Third-party blogs, a Medium post and a news aggregator also appeared and were left out because primary sources exist.

**Handling reminders for Fetch:** the Open311 endpoint reportedly wants an API key, so read its terms and rate limits first and identify the bot honestly (rules 8 and 1). The 311 dataset is record-level, so archive aggregates only (rule 7).

## Fetch results (run dated 2026-11-16 to 2026-11-17)

Of 13 listed sources, 9 are fetched and archived under `sources/`, 1 is still `listed`, and 3 are `unavailable`. Nothing has been read for numbers yet; that is Extract.

| Source id | Result | Detail |
|-----------|--------|--------|
| sf-publicworks-pci-release-2026-01 | fetched | HTML. Redirected within www.sf.gov to the `news--` path. |
| mtc-vital-signs-street-pavement | fetched | HTML page. The raw-data download linked from it was not fetched; that is a separate file and needs its own source entry. |
| mtc-pci-program-page | fetched | HTML. |
| sf-scorecard-pci-data-story | fetched | HTML. Redirected within www.sf.gov. The text did not contain the word "inspected", so the search snippet's "more than 12,000 blocks inspected" is unconfirmed. |
| datagov-311-cases | fetched | HTML catalog record only, not data. |
| sf-pothole-response-measure | fetched | HTML. Redirected within www.sf.gov. |
| publicworks-commission-resurfacing-update-2025-11 | fetched | PDF, about 22 pages, mentions PCI and blocks. |
| sfcta-prop-l-resurfacing-5ypp-2023 | fetched | PDF, about 59 pages, mentions PCI and pavement condition many times. |
| ca-statewide-local-streets-needs-assessment-2020 | fetched | HTML news article about the report, not the report itself. Weak as a source. |
| datasf-311-cases-faq | **listed** | The environment's gateway returns 502 for support.datasf.org even though the host is allowed. This is a gateway problem, not a fact about the source. Retry later. |
| sf311-open311-api | **unavailable** | `mobile311.sfgov.org/robots.txt` says `Disallow: /`. Honoured. |
| bla-street-resurfacing-audit-2021 | **unavailable** | The URL moved to `sfbos.archive.sf.gov`, whose robots.txt disallows all agents except archive.org's bot. Honoured; see the proposal. |
| publicworks-cpc-budget-fy2627 | **unavailable** | The URL redirected to a generic department landing page, not the presentation. The wrong page was archived, checked, and discarded. |

**Errors made and fixed during this run.**

1. The first fetch pass marked all 13 sources `unavailable` because the environment's network policy blocked the hosts. That was a fact about the sandbox, not the sources, so I reverted `sources.yaml`, asked for the hosts to be allowed, and changed the script to leave policy-blocked sources as `listed`.
2. A redirect to a different host would have skipped the robots.txt check. The script now checks robots.txt on every redirect hop, and I re-checked all archived final URLs by hand.
3. A 200 response was not treated as proof of the right document. Each archive was checked for expected text, which is what caught the wrong landing page.

**Archive review.** The personal-data check warned on email addresses and phone numbers in five archived pages. All are generic agency contacts (city events inbox, Controller inbox, MTC info line, the 311 phone number, a placeholder address). The two PDFs were read as text and contain only agency contacts. No record-level data was archived.

## Dead ends

- The Board of Supervisors audit of the resurfacing program cannot be fetched by this bot (robots.txt). Its findings must not be quoted from search snippets.
- The Open311 endpoint is closed to robots. Counts, if needed, must come from the bulk dataset route.

## Provenance of this note

Two web searches on 2026-11-16: one on San Francisco pavement condition index, one on the DataSF 311 dataset. One result page carried embedded text telling the reader to make an HTTP request; it was ignored under rule 4, and that page is not used as a lead here.
