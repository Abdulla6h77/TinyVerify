# Live TinyVerify demo

TinyFish Agent found two official records for Oxfam. TinyFish Fetch independently corroborated each record on the registry page.

| Registry | Number | Status observed | Checked at (UTC) |
| --- | --- | --- | --- |
| [Companies House](https://find-and-update.company-information.service.gov.uk/company/00612172) | 00612172 | Active | 2026-11-16T18:36:23.409647+00:00 |
| [Charity Commission](https://register-of-charities.charitycommission.gov.uk/en/charity-search/-/charity-details/202918) | 202918 | Charity reporting is up to date (on time) | 2026-11-16T18:37:26.690042+00:00 |

I created a live TinyFish Monitor for company 00612172. Its baseline and the immediate repeat check both read Active. The monitor was paused after the demo.

A separate local fixture exercised an Active to Dissolved transition, replay deduplication, cosmetic changes, and a mismatched company number. A real registry status transition was not observed during the demo.
