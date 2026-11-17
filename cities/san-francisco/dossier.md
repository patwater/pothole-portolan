---
slug: san-francisco
city: San Francisco
version: 1
drafted: 2026-11-17
ledger: claims.yaml
---
# San Francisco: potholes and pavement condition

## Summary

San Francisco rates the state of its streets with an engineering index, and it separately keeps a public record of the requests residents make about them. The two answer different questions. A Public Works release dated January 2026 states that the citywide Pavement Condition Index rating for 2025 was {{claim:sf-pci-citywide-2025}}, on a scale where zero is a crumbling street and one hundred is a freshly paved road.

The record of resident requests is the city's SF311 service request data. It has no request type labeled as a pothole, so the number of pothole reports cannot be counted from it. The nearest category is pavement defects, which accounted for {{claim:sf311-pavement-defect-cases-2025}} in 2025 and is routed to many agencies, including sewer operations. These counts show how many requests were logged. They do not measure the state of the pavement.

For potholes specifically, the Public Works scorecard reports {{claim:sf-pothole-service-orders-2025}} received in 2025, which is a different measurement from the SF311 count and is much lower than in other years for reasons the data does not give. The city's goal is to respond to pothole service requests within {{claim:sf-pothole-response-target-72h}}, and the scorecard's monthly percentages for 2025 average {{claim:sf-pothole-response-72h-mean-2025}}, an unweighted mean calculated for this dossier.

Every number below carries a footnote with its source address, retrieval date, archived copy, method and caveats, and what the sources do not say is listed near the end.

## Data regime

The pavement index is produced under the Metropolitan Transportation Commission's StreetSaver program and is reported both by the city and by the commission's Vital Signs site. The city's scorecard describes the method as surveys by evaluators in the StreetSaver Rater Program, with each road segment assessed on ride quality, cracking and signs of pavement distress. The scorecard also notes that the commission publishes three-year averages of the scores.

SF311 cases are published by DataSF as an open dataset that covers cases since July 2008, is updated nightly and is released under a public domain dedication and license. The Controller's performance scorecard publishes two pothole measures from Public Works, a monthly count of service orders and the share of requests answered within the goal, through a second DataSF dataset.

The Open311 interface for SF311 is closed to automated access by its robots.txt, so this dossier uses the open dataset's own query interface and requests grouped counts only, never individual records.

## What the pavement survey measures

The index rates pavement on a scale from zero to one hundred. The 2026 release describes zero as a pothole-riddled, crumbling street and one hundred as a newly surfaced one. No source retrieved for this dossier states what share of the network was surveyed in a given year, and the survey method is described only briefly, so both are recorded as not stated.

The city reports {{claim:sf-pci-citywide-2023}} for 2023, in a release dated January 2024, and {{claim:sf-pci-citywide-2025}} for 2025, in a release dated January 2026. Both are statements by the city and not data from the commission.

The commission's Vital Signs site reports a county average of {{claim:sf-pci-county-2024-mtc}} for 2024, up {{claim:sf-pci-county-change-2014-2024-mtc}} since 2014, against a regional average of {{claim:bay-area-pci-2024-mtc}}. The commission computes these as three-year moving averages and estimates the years between surveys from pavement age and treatments, so its figure is not the same kind of number as a single-year survey score. Whether the city's calendar-year scores and the commission's averages measure the same thing is not established by the sources.

Public Works' November 2025 presentation to its commission counts blocks in three groups for each year. The table gives the earliest and latest years in the presentation.

| Year | Very poor blocks | Poor or at-risk blocks | Good or excellent blocks |
|------|------------------|------------------------|--------------------------|
| 2014 | {{claim:sf-blocks-very-poor-2014}} | {{claim:sf-blocks-poor-atrisk-2014}} | {{claim:sf-blocks-good-excellent-2014}} |
| 2024 | {{claim:sf-blocks-very-poor-2024}} | {{claim:sf-blocks-poor-atrisk-2024}} | {{claim:sf-blocks-good-excellent-2024}} |

The presentation draws its rating bands in different places than the commission, the city scorecard and the Prop L program document do, so these groups must not be merged with any other scheme or compared with one.

The sources also disagree about how often the network is rated. Public Works, in a program document from July 2023, says it inspects each block and assigns a score every {{claim:sf-publicworks-pci-interval-years}}. The commission says its survey data set is updated every {{claim:mtc-pavement-survey-update-interval-years}}. The city's January 2026 release describes an annual evaluation with a fixed release date ({{claim:sf-pci-annual-release-date}}). These may describe different things, namely physical inspection, data refresh and publication, but no source says so.

This dossier does not convert between index schemes and does not compare San Francisco's score with those of other cities.

## What residents reported

SF311 service requests are published as an open dataset of cases since July 2008. Request types are organized in three levels of names, and no type or subtype with ten or more cases is labeled as a pothole: the search returned {{claim:sf311-pothole-labeled-case-type-groups}}, while the same search for the word pavement found the expected groups. The third level of names carries no further split within the pavement defect subtype, since it has {{claim:sf311-pavement-defect-details-distinct-values}} within the pavement defect subtype, and that value repeats the subtype name. A count of SF311 requests can therefore describe pavement defect requests, and potholes are an unknown share of them.

The table sets the SF311 pavement defect cases beside the Public Works scorecard's count of pothole service orders for the same calendar years. They are different measurements and their sizes differ several times over, so no relationship between them should be assumed.

| Year | Pavement defect cases in SF311 | Pothole service orders on the scorecard |
|------|--------------------------------|-----------------------------------------|
| 2013 | {{claim:sf311-pavement-defect-cases-2013}} | {{claim:sf-pothole-service-orders-2013}} |
| 2014 | {{claim:sf311-pavement-defect-cases-2014}} | {{claim:sf-pothole-service-orders-2014}} |
| 2015 | {{claim:sf311-pavement-defect-cases-2015}} | {{claim:sf-pothole-service-orders-2015}} |
| 2016 | {{claim:sf311-pavement-defect-cases-2016}} | {{claim:sf-pothole-service-orders-2016}} |
| 2017 | {{claim:sf311-pavement-defect-cases-2017}} | {{claim:sf-pothole-service-orders-2017}} |
| 2018 | {{claim:sf311-pavement-defect-cases-2018}} | {{claim:sf-pothole-service-orders-2018}} |
| 2019 | {{claim:sf311-pavement-defect-cases-2019}} | {{claim:sf-pothole-service-orders-2019}} |
| 2020 | {{claim:sf311-pavement-defect-cases-2020}} | {{claim:sf-pothole-service-orders-2020}} |
| 2021 | {{claim:sf311-pavement-defect-cases-2021}} | {{claim:sf-pothole-service-orders-2021}} |
| 2022 | {{claim:sf311-pavement-defect-cases-2022}} | {{claim:sf-pothole-service-orders-2022}} |
| 2023 | {{claim:sf311-pavement-defect-cases-2023}} | {{claim:sf-pothole-service-orders-2023}} |
| 2024 | {{claim:sf311-pavement-defect-cases-2024}} | {{claim:sf-pothole-service-orders-2024}} |
| 2025 | {{claim:sf311-pavement-defect-cases-2025}} | {{claim:sf-pothole-service-orders-2025}} |

The service-order total for 2025 is far below the other years, and the data gives no reason. The SF311 count for 2025 shows a much smaller change over 2024 than the service orders do.

Residents and staff reach SF311 through several channels. In 2025, {{claim:sf311-pavement-defect-cases-2025-mobile}} came through the mobile channel, {{claim:sf311-pavement-defect-cases-2025-web}} through the web, {{claim:sf311-pavement-defect-cases-2025-phone}} by phone, {{claim:sf311-pavement-defect-cases-2025-integrated-agency}} through an integrated agency channel, and {{claim:sf311-pavement-defect-cases-2025-no-channel-recorded}} had no channel recorded. The channel mix has changed over time, so shares are not comparable across years without checking.

Pavement defect cases are routed to many places. Of the {{claim:sf311-pavement-defect-agency-cells-total}} in agency groups of ten or more cases, {{claim:sf311-pavement-defect-routed-to-street-sewer-repair}} went to street and sewer repair bureau queues and {{claim:sf311-pavement-defect-routed-to-other-sewer-queues}} to other sewer-named queues. The grouping is by label text and the labels changed over time, so it shows the family is broader than road repair and does not show how many cases were potholes.

Counts of requests reflect how many requests were logged, which depends on how easily residents can report, whether they trust the system and who uses it. They do not measure the state of the pavement, and this dossier does not compare them across cities.

## Spending and repair performance

A Public Works release says that in 2025 crews paved {{claim:sf-blocks-paved-2025}} of City-maintained streets. A November 2025 presentation to the Public Works Commission reports {{claim:sf-blocks-resurfaced-as-of-2025-11}} resurfaced and more than {{claim:sf-blocks-planned-as-of-2025-11}} planned, but its slide gives no period, so the resurfaced figure cannot be read as annual or cumulative.

The same presentation puts the average cost of a block of paving at {{claim:sf-avg-cost-per-paved-block-2025-11}}, a figure that includes staff time, curb ramps and base repair. A release says that extending the life of a block in good condition can cost as little as {{claim:sf-preservation-cost-per-good-block-min}}. These describe different things, a full paving project block and a preservation floor, and they are not averaged or compared here. The release's matching figure for reconstructing a block in very poor condition is printed with a missing digit, so it is not used.

Between July 2023 and November 2025 the commission awarded {{claim:sf-resurfacing-awards-amount-2023-2025}} in street resurfacing contracts covering {{claim:sf-resurfacing-awards-blocks-2023-2025}}. These are award amounts and not spending to date, and the rounded project amounts sum to slightly less than the stated total. Public Works also cites {{claim:sf-resurfacing-investment-15-plus-years}} invested over more than fifteen years, without giving a start year.

The city's goal is to respond to pothole service requests within {{claim:sf-pothole-response-target-72h}}, although the scorecard defines each month's figure as the share answered within three business days. The table gives, for each calendar year, the unweighted mean of the scorecard's twelve monthly percentages. It was calculated for this dossier, so it is not the city's published fiscal-year figure and not the share of all requests in the year.

| Year | Mean of the monthly shares of requests answered within the goal |
|------|-------------------------------------------------------------------|
| 2013 | {{claim:sf-pothole-response-72h-mean-2013}} |
| 2014 | {{claim:sf-pothole-response-72h-mean-2014}} |
| 2015 | {{claim:sf-pothole-response-72h-mean-2015}} |
| 2016 | {{claim:sf-pothole-response-72h-mean-2016}} |
| 2017 | {{claim:sf-pothole-response-72h-mean-2017}} |
| 2018 | {{claim:sf-pothole-response-72h-mean-2018}} |
| 2019 | {{claim:sf-pothole-response-72h-mean-2019}} |
| 2020 | {{claim:sf-pothole-response-72h-mean-2020}} |
| 2021 | {{claim:sf-pothole-response-72h-mean-2021}} |
| 2022 | {{claim:sf-pothole-response-72h-mean-2022}} |
| 2023 | {{claim:sf-pothole-response-72h-mean-2023}} |
| 2024 | {{claim:sf-pothole-response-72h-mean-2024}} |
| 2025 | {{claim:sf-pothole-response-72h-mean-2025}} |

The mean was {{claim:sf-pothole-response-72h-mean-2013}} in 2013 and {{claim:sf-pothole-response-72h-mean-2025}} in 2025, with ups and downs in between. The scorecard reports {{claim:sf-pothole-response-72h-2026-07}} for July 2026 and {{claim:sf-pothole-response-72h-2026-08}} for August 2026. The page states about a one-month data lag, so recent months may be provisional and these values should not be read as settled.

## What could not be found

The number of pothole reports in SF311 could not be found, because the request types have no pothole value and the third level of names adds no split. The search covers only groups of ten or more cases, so it shows that no pothole-labeled type is that large, not that none exists.

The share of the network surveyed in any year could not be found in any retrieved source, and the survey method is described only briefly.

The city scorecard page for the index keeps its values in an embedded dashboard that was not part of the archived page, so the scorecard's own index values were not read. At the time of retrieval the page said its latest score was from December 2024, while the January 2026 release reports 2025, which suggests the scorecard had not yet been updated.

The commission's downloadable raw data for the index could not be retrieved, because the download links are built by script and are not in the archived page. The exact annual county series is therefore not available here.

A 2021 performance audit of the street resurfacing program by the Board of Supervisors' Budget and Legislative Analyst was not retrieved, because the document's host disallows automated access in its robots.txt. Its findings are not quoted from secondary sources.

The Public Works presentation of its fiscal year 2026 to 2027 capital budget could not be retrieved, because its address leads to a general department page. The SF311 case data FAQ could not be retrieved, because the gateway used for this research could not connect to its host in two attempts.

The reason the 2025 pothole service-order total is far below the other years could not be found. Whether the resurfaced-blocks figure in the November 2025 presentation is annual or cumulative could not be found. A cost for reconstructing a block in very poor condition could not be used, because the release prints it with a missing digit.

## Sources

<!-- The renderer fills this section from sources.yaml. -->

## Version history

Version 1 is the first draft, written on 2026-11-17 for the supervisor's review. It has not been published.
