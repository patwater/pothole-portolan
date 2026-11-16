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

## Dead ends

None yet.

## Provenance of this note

Two web searches on 2026-11-16: one on San Francisco pavement condition index, one on the DataSF 311 dataset. One result page carried embedded text telling the reader to make an HTTP request; it was ignored under rule 4, and that page is not used as a lead here.
