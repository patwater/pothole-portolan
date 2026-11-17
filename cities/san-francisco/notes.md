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

1. **Which year is the score of 75?** (Partly corrected by Extract: the page archived as the 2026 release is the 2024 release; see the Extract section.) A city release dated January 2026 reportedly says 75 in 2025. The MTC Vital Signs page, per the result, says San Francisco County averaged 75 in 2024 and describes a three-year moving average. A January 2024 city release was also reported as giving 75, for 2023. These may be different measures (a calendar-year score against a three-year moving average) or different reporting conventions, and a claim must state the period and averaging method exactly as the source does.
2. **Rating bands differ.** (Superseded by Extract: there are four band schemes in the archives, and the "64 to 84" snippet is not on MTC's page.) The MTC page reportedly calls 64 to 84 "good" and 85 to 100 "excellent". The city scorecard reportedly calls 70 to 84 "good". The dossier must quote the band from whichever source a claim uses and not mix them.
3. **Response-time target.** The scorecard describes a 72-hour goal, while a 2021 audit gives the departmental goal as 90 percent within 72 hours. Confirm the target and the measured share from the primary documents.

**Gaps:**

- The canonical data.sfgov.org landing pages for the 311 Cases dataset and the Scorecards dataset were not seen in results. Fetch must resolve them rather than build URLs from the dataset id.
- No national statistics body fits as a source for San Francisco. Federal highway data is a possible later lead but was not searched, so it is not listed.
- No Controller audit specific to pothole repair was found. The Budget and Legislative Analyst audit of the resurfacing program is the nearest.
- The share of the network surveyed was not found in any snippet, so it is still unknown for the `condition_index` block.

**Excluded on purpose:** one gitbook page from a different host than the DataSF explainer contained embedded instructions in its search result. It was not listed. Third-party blogs, a Medium post and a news aggregator also appeared and were left out because primary sources exist.

**Handling reminders for Fetch:** the Open311 endpoint reportedly wants an API key, so read its terms and rate limits first and identify the bot honestly (rules 8 and 1). The 311 dataset is record-level, so archive aggregates only (rule 7).

## Fetch results (run dated 2026-11-16 to 2026-11-17)

Of the 13 sources first listed, 9 were fetched. A second run on 2026-11-17 added the 2026 release (see below), so the inventory now has 14 sources: 10 fetched, 1 `listed` and 3 `unavailable`. Nothing has been read for numbers yet; that is Extract.

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

## Extract results (2026-11-17)

Eighteen claims are in `claims.yaml`, all `provisional`: 10 `measured_condition`, 5 `spending`, 3 `policy`. They come from `scripts/extract_san_francisco.py`, which ties each value to anchor text in an archive and refuses to write if an anchor is missing. Assess has not yet re-derived them, so none is `supported`.

**Corrections to my earlier notes.**

- The page I archived as the "January 2026 release" is the January 8, 2024 release. Its 75 covers calendar year 2023. The 2026 release is a separate page, `https://sfpublicworks.org/node/35600`, now listed in `sources.yaml` and not yet fetched. Whether it reports 75 for 2025 is unverified.
- The Discover snippet that MTC calls "good" 64 to 84 does not appear on MTC's Vital Signs page, which gives Good as 70 to 79.

**Four incompatible band schemes in the archives.** Never merge categories across them.

| Source | Bands |
|--------|-------|
| MTC Vital Signs | Failed 0-24, Poor 25-49, At Risk 50-59, Fair 60-69, Good 70-79, Very Good 80-89, Excellent 90-100 |
| City scorecard | Very poor 0-24, Poor 25-49, At-risk 50-69, Good 70-84, Excellent 85-100 |
| Public Works Commission deck | Very Poor 0-25, Poor 25-50, At-Risk 50-60, Good 60-80, Excellent 80-100 |
| Prop L program document | Preservation 60-80, resurfacing 50-60, base repair or reconstruction 0-50 |

**Unresolved conflicts (left for Assess, not settled here).**

1. *How often is the network surveyed?* Public Works, via the Prop L document: every two years. MTC: its data set is updated every three years. The city scorecard: published once a year, latest December 2024. Both interval statements are claims in the ledger.
2. *Share of good blocks.* The 2024 city release says MTC found two-thirds of San Francisco's blocks "good" or "excellent". The Public Works deck counts 11,171 of 12,982 blocks (about 86 percent, my arithmetic, not a claim) as good/excellent in 2023. The band definitions differ, which may explain it, but that is a guess.
3. *Same number, different meanings.* 75 appears as a calendar-year 2023 city score, as MTC's 2024 three-year moving average for the county, and reportedly as the 2025 score. These are not obviously the same measurement.
4. *72 hours versus three business days.* The pothole page states a 72-hour goal but defines the monthly figure as requests answered within three business days.

**Not extracted, and why.**

- No `reported_demand` claims. The 311 counts need the dataset, which needs `data.sfgov.org` (see proposal `2026-11-17-001`).
- No measured pothole response percentage. The page text holds none; it sits in an embedded dashboard backed by the Scorecards dataset.
- No value from the city PCI scorecard page, for the same reason.
- No figures from the 2021 audit, the FY26-27 budget presentation or the Open311 endpoint (unavailable).
- MTC's "Download Raw Data" files, which would give the exact annual series, have JavaScript-built links that are not in the archived page. Discover should look for them.

**Method lessons.** The first extraction run picked up a slide-footer page number ("4") as the blocks-resurfaced figure; I noticed it in the printed summary, and the script now anchors on the whole slide sequence. The awards table rows sum to $132.9 million against a stated total of $133.0 million, so the script allows rounding and the claim's caveats say so. Block counts match exactly (805).

## Assess results (2026-11-17)

`scripts/assess_san_francisco.py` re-derived all 18 claims from their archives by a second path: html.parser instead of regex stripping for pages, `pdftotext -raw` (which emits tables column by column) instead of `-layout` for PDFs, and different anchor phrases. It also checked each claim mechanically: archive hash, source inventory match, retrieval date, that the value and period appear in the statement, and that every `measured_condition` claim has its index block. Result: **15 supported, 3 provisional, 0 demoted.**

I also checked the PDF figures by eye against rendered slides 5, 7, 8 and 10. The slide 8 cost breakdown sums to its headline ($50,000 + $60,000 + $55,000 + $65,000 + $30,000 = $260,000), and the slide 10 block counts sum to the stated 805.

**Still provisional, and why.**

| Claim | Why it was not promoted |
|-------|-------------------------|
| sf-blocks-resurfaced-as-of-2025-11 (9,148) | The figure is reproduced, but the slide gives no start year or period, so whether it is cumulative, annual or since a program start is unknown. |
| sf-blocks-planned-as-of-2025-11 (2,500+) | A lower bound with no planning horizon stated. |
| sf-resurfacing-awards-amount-2023-2025 ($133.0M) | The stated total is reproduced, but the 21 rounded project amounts sum to $132.9M, so the total does not re-derive exactly from its parts. |

**What "supported" does and does not mean here.** It means the figure is accurately reported from the archived source and its period and units are right. It does not mean the underlying fact is independently verified. Several supported claims are the city's own statements (for example the 75 in the 2024 release), and two supported claims, the two-year and three-year survey intervals, contradict each other as descriptions of how often the network is surveyed. Each is a true statement of what its document says. A dossier must show both and must not choose.

**Limits of this assessment.**

- The same author wrote Extract and Assess. The independence is in the method, not in a second reader. A human spot-check of a few claims against the source pages would add real independence.
- Which table column is which category (very poor, poor/at-risk, good/excellent) rests on the slide's legend colors and bar order, which I read by eye. No script verifies it.
- Nothing here resolves the four band schemes or the open conflicts listed under Extract results. Those are not numeric errors, they are scope questions.
- Only 18 claims exist. No demand claims and no measured pothole response claim, so the ledger cannot yet support a dossier section on residents' reports or repair speed.

**Defects in my own tooling found while testing.** A claim whose archive is missing crashed the assessor instead of demoting that claim. That is fixed, and `tests/test_assess.py` now damages three claims (wrong value, wrong period, missing archive) and checks that exactly those are demoted.

## Second Fetch run (2026-11-17)

| Source id | Result | Detail |
|-----------|--------|--------|
| sf-publicworks-pci-release-2026-01 | fetched | HTML, 51,897 bytes, no redirect, robots.txt permits it. Content checked: it is the Public Works release dated January 2, 2026. |
| datasf-311-cases-faq | still **listed** | `support.datasf.org` returns a gateway 502 ("host allowed, but the gateway could not connect to it") again. It has now failed in two runs. This describes the gateway's path to the host, not the source. |

**Extract candidates from the 2026 release.** These are leads for the next Extract run, not claims, and the release text must be re-read then. It reports a PCI of 75 for 2025, 581 City-maintained blocks paved in 2025, and a $979 million investment over more than 15 years that resulted in more than 9,000 of nearly 13,000 blocks being resurfaced. It says the annual evaluation is released December 31 every year and tracked by MTC. It gives the regional average as 67, with San Jose at 73 and Oakland at 58. One dollar figure in the text has a typo ("$500,00"), so reconstruction cost must not be extracted from it without a caveat.

**Effect on the open conflicts.** 75 is now reported by the city for calendar year 2023 and for 2025, and by MTC as a three-year moving average for 2024. These are consistent with a score that held at 75, so the earlier worry about three unrelated meanings is weaker. It is still not established that the city's calendar-year score and MTC's moving average measure the same thing, so the claim periods and methods must stay as the sources state them.

**Handling note.** The archived release carries a named press contact and a work email address. It is a public press-office line, not record-level data, so the archive stays. The name and address must not be copied into claims, notes or a dossier.

**Still unresolved for 311.** The DataSF FAQ remains unreachable. If it stays blocked, the 311 dataset's own documentation on another DataSF host (a search result earlier showed `docs.datasf.org` and a gitbook explainer) could replace it, but that is a Discover decision and those hosts are not on the environment's allowlist.

## Extract results, second run (2026-11-17)

Five claims were added from the January 2, 2026 Public Works release, so `claims.yaml` now has 23 claims: 15 `supported` (Assess, first pass) and 8 `provisional`, of which these five are new and **pending Assess**.

| Claim id | Value | Kind |
|----------|-------|------|
| sf-pci-citywide-2025 | 75 PCI points, 2025 | measured_condition |
| sf-blocks-paved-2025 | 581 blocks, 2025 | spending (program output) |
| sf-resurfacing-investment-15-plus-years | $979 million | spending |
| sf-preservation-cost-per-good-block-min | $50,000 per block, a floor | spending |
| sf-pci-annual-release-date | December 31 each year | policy |

**Deliberately not extracted.**

- The reconstruction cost for a very poor block is printed as "$500,00". It could be $500,000 or $50,000 and I will not guess. It is the other half of a comparison the release makes, so the $50,000 floor claim carries a caveat saying so. A person should check the original page or ask Public Works.
- The regional average (67), San Jose (73) and Oakland (58). They are cross-city figures. MTC's own page is the better source for them, and the first is already a claim from there.
- "Tops among big Bay Area cities" and the line that a dip in funding will likely worsen roads. The first is a ranking by someone else's method and the second is a projection.
- The statement that more than 9,000 of nearly 13,000 blocks were resurfaced. It agrees with the Commission deck's 9,148 and roughly 13,000, so it needs no separate claim. It also does not resolve the deck's unstated period.

**Observations.**

- Three survey-cadence statements now exist in the ledger: two-year inspections (Prop L document), a three-year MTC dataset update, and an annual evaluation released each December 31 (this release). They may describe different things (physical inspection, dataset refresh, published score), but no document says so. Assess must not choose.
- The city scorecard page, archived on 2026-11-16, says its latest PCI score is from December 2024, while this release reports the 2025 score. The scorecard appears not to have been updated for 2025 yet, which is a Monitor item.
- $50,000 (this release, a floor for preserving a good block) and $260,000 (the Commission slide, an average for a full paving block) must not be set side by side without saying what each covers. Dividing $979 million by blocks to get a cost per block would mix those and is not done here.

**Tooling change made during this run.** The new claims made the assessor demote them to `speculative` because it had no derivation for them, which also broke `tests/test_assess.py`. Never attempted is not failed, so the assessor now marks such claims `PENDING` and caps them at `provisional`, and a new test checks that a claim without a derivation can never become `supported`.

## Assess results, second pass (2026-11-17)

Derivations were added for the five claims from the January 2, 2026 release, so every claim in the ledger now has one (a test enforces this). Result across all 23 claims: **19 supported, 4 provisional, 0 demoted.**

| New claim | Outcome | Basis |
|-----------|---------|-------|
| sf-pci-citywide-2025 (75) | supported | Sentence gives 75 in 2025; page metadata dates the release 01/02/2026; the 0-100 scale text is present. |
| sf-blocks-paved-2025 (581) | supported | Text gives 581 City-maintained blocks in 2025; period and unit are clear. |
| sf-preservation-cost-per-good-block-min ($50,000) | supported | Text gives "as little as $50,000" for a block in good condition. The claim's caveat about the garbled reconstruction cost must travel with it. |
| sf-pci-annual-release-date (Dec. 31) | supported | Text says findings are released "Dec. 31 of every year". |
| sf-resurfacing-investment-15-plus-years ($979M) | **provisional** | The figure is reproduced, but the period is only "15-plus years": no start year, funding sources or price basis. |

**Provisional claims now: four.** The $979 million claim above, plus the three from the first pass (blocks resurfaced 9,148 and blocks planned 2,500+, both with no period or horizon, and the $133.0M award total that does not re-derive exactly from its rounded rows).

**How much independence this pass has.** Less than the first pass. Those claims were tables and slide figures that I could rebuild a second way and check against rendered images. The new ones are single sentences in one HTML page, so the second derivation only confirms, through a different parser, that the sentence says what Extract recorded. No second source exists for the 581 blocks, the $50,000 floor or the Dec. 31 date. The $979 million figure's "more than 9,000 of nearly 13,000 blocks" is consistent with the Commission deck's 9,148 and roughly 13,000 but is not an independent check on the dollars.

**What "supported" means for these.** The release reports the number, period and unit accurately. For the 2025 PCI, 581 blocks and $50,000, these are the department's own statements about itself.

**Where the ledger stands.** Strong on condition (PCI for 2023, 2024 and 2025, and block counts by category for 2014 and 2024), on program output and costs, and on the policy statements. Absent: any reported-demand claim and any measured pothole response percentage. A dossier cannot yet say how many potholes residents reported or how fast the city responded.

## 311 plan, step 1: dataset metadata (2026-11-17)

You approved `data.sf.gov` and `data.sfgov.org`. Both hosts serve the same robots.txt: `Crawl-delay: 1` (this fetcher waits 3 seconds) and disallows for `/browse` listings, OData, login and tiles. The `/api/views/`, `/resource/` and query paths I need are permitted. Four metadata-only sources were fetched and archived (no records): the 311 Cases dataset metadata and column list (`vw6y-z8j6`), and the Scorecard Measures metadata and column list (`kc49-udxn`).

**A rule 7 problem found and handled.** The portal's column metadata embeds `cachedContents`: up to 20 sample values per column drawn from live data, including the `address`, `street`, `lat`, `long`, `status_notes` and `service_details` columns. Those are record-level fragments. I fetched the four files once, saw the structure, and deleted them before anything was committed. I printed only counts, never the values. `scripts/fetch_source.py` now strips every `cachedContents` block before archiving, with a test (`tests/test_fetch.py`). The archived copies are sanitized and re-serialized, so their hashes are of the sanitized files, not of the raw responses, and each source's notes say so.

**What the metadata shows (all from the archived files).**

| Topic | Finding |
|-------|---------|
| 311 Cases scope | Cases created since 7/1/2008 "with location information"; updates nightly around 6am Pacific. |
| License | Open Data Commons Public Domain Dedication and License, for both datasets. |
| Date field | `requested_datetime`, the date and time the request was made. |
| Case type | Three text fields: `service_name`, `service_subtype` and `service_details`. The metadata does not list their values, so **what counts as a pothole is still unknown** and has to come from an aggregate count of those values. |
| Reporting channel | `source`: "Mechanism or path by which the service request was received", with example values such as Phone, Text/SMS, Website and Mobile App. This allows a breakdown by channel, which matters for what a count means. |
| Other useful fields | `agency_responsible`, `status_description`, `closed_date`. |
| Fields to never select | `address`, `street`, `lat`, `long`, `point`, `point_address`, `status_notes`, `service_details` free text, `media_url`. |
| Scorecard Measures | One row per measure per month: `measure_title`, `measure_methodology`, `calendar_month`, `actual`, `target`, `department`, plus category columns used to compute monthly actuals. |
| **Sentinel value** | In Scorecard Measures, **-9999 means "no entry"** for `actual` and `target`. Extract must treat it as null and never as a number. |

**Observation.** The dataset's own description links to an FAQ on `sfdigitalservices.gitbook.io`, a different host from the `support.datasf.org` page that has been failing. That host is one whose search result earlier carried embedded instructions, which I ignored. It is not on the allowlist and I have not added it. Fetched content is data in any case, but the field documentation above already covers what I need, so I would only ask for it if the pothole classification is unclear after step 2.

**Step 2 would ask for aggregates only.**

1. Counts of cases grouped by `service_name` and `service_subtype`, to learn which values mean pothole.
2. Counts of the pothole values by calendar year of `requested_datetime`, and by `source`.
3. The Scorecard Measures rows whose `measure_title` is the pothole response measure: `calendar_month`, `actual`, `target`, `measure_methodology`.

No query would select an address, coordinate or free-text field.

## Dead ends

- The Board of Supervisors audit of the resurfacing program cannot be fetched by this bot (robots.txt). Its findings must not be quoted from search snippets.
- The Open311 endpoint is closed to robots. Counts, if needed, must come from the bulk dataset route.

## Provenance of this note

Two web searches on 2026-11-16: one on San Francisco pavement condition index, one on the DataSF 311 dataset. One result page carried embedded text telling the reader to make an HTTP request; it was ignored under rule 4, and that page is not used as a lead here.
