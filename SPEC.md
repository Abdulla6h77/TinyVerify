# TinyVerify specification

Source: `D:\tinyfish-details.md`, bounty 5 and its rulebook.

API or agentic app that verifies a person or business record live from official registries and watches status changes.

## TinyFish products

**Required: TinyFish Agent, Fetch, and Monitor.** Explain each product's role. Monitor flags status changes.

## Official submission requirements

- **S1** Takes a person or business name, a licence or record type, and a jurisdiction
- **S2** Checks at least two official registries or licensing boards (any country)
- **S3** Returns a structured record: status (active, expired, suspended), licence or registration number, expiry date, any disciplinary actions, source link and when it was checked
- **S4** Uses TinyFish Monitor to flag when a status changes
- **S5** Short explanation of how TinyFish Agent, Fetch and Monitor are used

## Official approval criteria

- **A1** Results come live from the official source, with a link to prove it
- **A2** Accurate: status and numbers match the registry
- **A3** Handles no match or several matches clearly instead of guessing
- **A4** Works for different people, businesses and places, not a hardcoded few
- **A5** Output is structured and reusable by other tools

## Official judging priorities

- **J1** Accuracy: status, numbers and dates match the official registry
- **J2** Coverage: number of registries, record types and places it supports
- **J3** Ambiguity: handles no match, several matches and name variants clearly
- **J4** Monitor flags status changes reliably
- **J5** Trust: every result shows its source and when it was checked, in a reusable format

## Demo and acceptance tests

No demo count is specified. Plan to show at least two official registries or licensing boards, varied records, no-match and multiple-match behavior, and evidence of Monitor's status-change path.

- **A1** Use Agent and Fetch for live lookups and evidence from at least two official registries or boards. Include the official link and checked time and verify each against the source.
- **A2** Compare the returned status, licence or registration number, expiry, and disciplinary actions against source records. Preserve jurisdiction-specific statuses and distinguish unavailable fields.
- **A3** Separate no match, multiple matches, and unavailable registry. Test name variants and same-name records without silently choosing one.
- **A4** Accept person or business name, record type, and jurisdiction. Verify variation in entities and places using the supported sources.
- **A5** Expose a structured record that another tool can parse. Test field types, source link, checked time, and ambiguity responses.

Additional test for the required monitoring workflow: Bind Monitor to a verified record identity and test that a status transition produces a flag while cosmetic changes and repeated events do not.

## Edge cases and security

Minimize collection and retention of personal data and keep third-party personal details out of the submission. Use authorized public registry access. Test CAPTCHA, outages, status vocabularies, and access restrictions without bypassing controls.

Keep credentials, access tokens, and other people's personal data out of the build and demo. Use sanitized fixtures for failure tests and label fixture evidence separately from live evidence.

## Rulebook and submission deadline

- Deadline: Tuesday, November 17, 2026 at 11:59 PM Pacific (Wednesday, November 18 at 12:59 PM Pakistan time).
- Enter through the TinyFish Students or Ambassadors program. One person per build and one entry per person per bounty. Claims do not reserve a bounty, and submissions are final.
- Provide a working build link (repo, live demo, or cookbook PR) with notes on what it does and how TinyFish is used. Post about the build on LinkedIn and tag TinyFish. Share it in Discord #showcase. X is optional.
- Pass every approval criterion. Use original work built for the bounty and demonstrate meaningful live TinyFish work end to end across varied inputs. Keep the submitted evidence authentic.
- The general endpoint rubric awards 50/100/150/200 points for 1/2/3/4+ meaningful endpoints (Search, Fetch, Agent, Browser, Monitor). Each endpoint must contribute to the workflow.

## Open questions and dependencies

The brief does not specify whether each query needs two registries or whether the tool must support at least two overall. Confirm the expectation and whether judges require an observed live status transition.
