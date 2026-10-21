# Fan guides: acquisition channel

## Goal and scope

Build an English-language search entry channel for overseas fans buying Japanese character goods and attending events. The dedicated `/fans/` family is separate from the existing practice materials and Honne Japan journal. Search visitors should complete their immediate task on the guide itself; links to free Japanese practice are optional next steps.

Do not use page count as the success metric. Publish another page only for a distinct reader job with source-backed facts and a useful comparison, worked example or tool. Do not turn this channel into generic culture definitions or duplicate existing practice pages.

## Initial query-to-page map

| Page | Search intent | Distinct value |
|---|---|---|
| ita-bag-inserts | ita bag insert; insert dimensions | Fit an insert into a bag already owned; measured openings and manufacturer examples |
| ita-bag-sizes | ita bag sizes; how many badges fit | Choose a panel from a desired badge layout; bounded browser calculator with explicit geometry |
| can-badge-sizes | can badge sizes; 57mm badge cover | Separate badge size, compatible item size and covered outer size |
| acrylic-stand-vs-keychain | acrylic stand vs keychain; acrysta | Compare uses and included parts; read Japanese listing labels |
| blind-box-vs-complete-set | Japanese random merch BOX complete set | Distinguish range count, unit count and an explicit assortment promise |
| japanese-preorder-labels | Japanese preorder meaning; toriyose | Separate order deadline, release and dispatch; seller-specific conditions |
| cheki-photo-sizes | cheki size; instax mini sleeve size | Compare outer film vs image dimensions; layered fit checks |
| japanese-concert-seat-types | Japanese concert restricted view; seated only | Decode ticket categories through dated official examples |

US/en Google Ads proxy research returned `ita bag` 60,500, `ita bag insert` 1,000 and `ita bag sizes` 40 monthly searches. These are broad planning estimates from the research session, not verified current demand on every article, achievable visits or a forecast. Other pages are test hypotheses; no demand or ranking claims should be made from their existence alone.

## Source and editorial checks

Sources are linked beside material factual claims and listed at the end of each guide. All initial guides were checked on 2026-10-21. The guides use original explanations and schematic drawings, not copied product images. They do not claim first-hand testing, current stock, seller endorsement or personal attendance.

Specific source pitfalls resolved before publication:

- COADE original insert announcement has inconsistent 54–57 / 54–58 mm text: the guide uses the unambiguous 57 mm example only.
- COADE's 2026 mini 75 mm announcement has conflicting supported-diameter fields: that variant is omitted.
- Manufacturer capacities are separate from the calculator's non-overlapping rectangular grid. Do not “correct” one into the other or describe the manufacturer arrangement as verified by our tool.
- A4/A3 labels do not establish pocket or insertion-opening dimensions.
- Good Smile's five-design K-ON BOX example is one specific product's assortment promise. Its preorder period is historical as of the source check. No equal random odds or universal complete-BOX rule is inferred.
- Animate's sourcing and cancellation examples apply to Animate Online Shop; the guide makes no general legal or shop-wide market claim.
- Instax mini dimensions refer to the whole physical film and image separately. They are not attributed to every cheki-style print or every instax format.
- Concert examples are from the 2025 and 2026 events named in the article, not current availability or universal venue rules.

Changing a source-check date requires checking the relevant source claims. Do not advance dates automatically on rebuild. Preserve published URLs when updating pages. Keep the full first-answer content in static HTML; JavaScript adds only the calculator.

## Measurement and iteration

The existing GA4 configuration provides page views. The calculator emits `fan_tool_used` with `tool_name=badge_grid` on a valid submit, without measurements or user-entered text. It is a usage count, not proof of acquisition or purchase conversion. Production tracking configuration is reused; no new service is introduced.

GSC data was not available through the connected SEO operator during this release (rate-limit / invalid-argument failures). Therefore no baseline, indexing status or traffic lift has been verified. Do not infer search impressions from deployment success.

1. At the first accessible GSC review, filter page URLs containing `/fans/`; record indexing, non-brand queries, impressions, clicks, CTR and positions. Separate the query `ita bag insert` from the broader calculator intent.
2. After roughly 4–6 weeks, inspect actual query-to-page matches. If pages are not indexed, investigate discovery/canonical/rendering first. If impressions exist, compare the page's promise with those queries before changing titles. Low exposure alone does not prove the topic is invalid.
3. After roughly 8–12 weeks, deepen the pages with relevant query evidence and actual reader usefulness. Consolidate overlapping insert/size material if the same intent lands on both. Do not expand into dozens of near-identical size pages.
4. Expand only the winning topic cluster. Candidates include tested fit examples with authentic measurements, a carefully sourced goods-size reference, or another tool that solves an observed task. New fashion, slang and meme channels require separate demand/competition evidence.

These are review windows, not automated scheduled jobs. No traffic targets are promised without baseline data. Deployment checks cover routing, canonical/indexing directives, sitemap inclusion, calculator boundary conditions and existing learning URLs; rankings and acquisition effects need later observation.
