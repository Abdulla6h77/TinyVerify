# TinyVerify tasks

Criterion and requirement IDs refer to [SPEC.md](SPEC.md). This checklist plans implementation and validation.

## Prerequisites

- [x] Record the official submission requirements, approval criteria, and judging priorities.
- [ ] Confirm product access, endpoint contracts, live test authorization, and sufficient quota. Resolve or document the open decisions in SPEC.md.
- [ ] Keep setup, configuration, dependencies, and verification project-local.

## Implementation and approval checks

- [x] **A1** Use Agent and Fetch for live lookups and evidence from at least two official registries or boards. Include the official link and checked time and verify each against the source.
- [ ] **A2** Compare the returned status, licence or registration number, expiry, and disciplinary actions against source records. Preserve jurisdiction-specific statuses and distinguish unavailable fields.
- [ ] **A3** Separate no match, multiple matches, and unavailable registry. Test name variants and same-name records without silently choosing one.
- [ ] **A4** Accept person or business name, record type, and jurisdiction. Verify variation in entities and places using the supported sources.
- [x] **A5** Expose a structured record that another tool can parse. Test field types, source link, checked time, and ambiguity responses.
- [ ] Bind Monitor to a verified record identity and test that a status transition produces a flag while cosmetic changes and repeated events do not.

## Verified in the local demo

- Agent and Fetch corroborated organization records in Companies House and the Charity Commission.
- The Companies House Monitor returned a live baseline and repeat observation for the same organization. Both showed Active. The provider confirmed the monitor is paused.
- A status transition, duplicate replay, a mismatched identity, and cosmetic changes were exercised with fixtures.
- See [DEMO.md](DEMO.md). Additional live targets and an actual registry transition remain unobserved.

## Demo and submission

- [ ] No demo count is specified. Plan to show at least two official registries or licensing boards, varied records, no-match and multiple-match behavior, and evidence of Monitor's status-change path.
- [ ] Run the edge-case and security checks in SPEC.md. Capture reproducible live evidence separately from fixture results.
- [ ] Review every submission requirement (S1, S2, S3, S4, S5) and approval criterion before marking the build ready.
- [ ] Prepare setup instructions, the working build link, notes explaining TinyFish's role, the required LinkedIn post tagging TinyFish, and the Discord #showcase share. Obtain publication authorization before posting.
- [ ] Verify the evidence and submit by Tuesday, November 17, 2026 at 11:59 PM Pacific (Wednesday, November 18 at 12:59 PM Pakistan time).
