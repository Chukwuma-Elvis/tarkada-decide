# Part A.2 — Product Requirements Document

Takarda has one product-level tension that every feature below inherits: it must feel instant to seven very different users at once (a candidate on a feature phone, a school pulling hundreds of rows, an employer's automated system) while costing the same every month regardless of how many of them show up on the same day. Nothing in this document should be read as satisfying every user's first-choice request — Part B.0 names where that isn't possible and what was chosen instead. What follows is what actually ships, for whom, and in what order.

## Users and their jobs

| User | Job to be done | Good outcome |
|---|---|---|
| Candidate (browser) | Check my result the moment it is released | Result appears in one attempt, in seconds, without losing a PIN use to a failed attempt |
| Candidate (feature phone, 2G, USSD/SMS) | Check my result without a smartphone or good signal | Same result, same PIN, over USSD/SMS, without needing a data connection |
| Candidate (any channel) | Buy a PIN without being charged twice | One PIN, one charge, confirmed or safely retried |
| School administrator | Get every result for my school's candidates at noon on results day | A complete, correct file for my ~400 candidates, ready at noon |
| Employer / university (via the employers' association) | Confirm a certificate is genuine | A yes/no plus the minimal data needed to confirm it, nothing else about the candidate |
| Employer / university (recurring) | Find out if a certificate I verified before still stands | A status check they can run any time, and a notification if one they checked recently is superseded, without Takarda needing to have their contact details in advance |
| Council officer | Find a candidate from a partial surname; record an amendment with evidence | Search returns in an interactive time; amendment is recorded with officer and evidence attached, permanently |
| Regulator (Council board, via the officer/audit path) | Prove what a result said on any past date | Point-in-time reconstruction available for any released result, for 50 years |

## Scope — Release 1 (the May sitting)

**In scope:**

- Candidate result check: browser (HTTPS) and USSD/SMS (via telecom aggregator).
- PIN purchase with the reserve/confirm idempotency fix (Part C.4) — the double-charge problem is fixed in Release 1, not deferred.
- Results-day pre-materialized read path for candidates and schools (Part B, ADR-001).
- School bulk export for one sitting.
- Employer/university certificate verification, DPO-filtered.
- Certificate status check and supersession notification (Part B.0, Conflict C's resolution).
- Amendment workflow with officer attribution and evidence reference.
- Officer partial-surname search.
- Core data model supporting 50-year point-in-time reproducibility.

**Explicitly out of scope for Release 1** (see Part B.6, "What you are not building," for the full reasoning):

- Real-time push notification of amendments to candidates/schools/employers.
- Self-service live analytics dashboards for the Council beyond the existing per-sitting report.
- Any identity check beyond PIN + exam number for candidate access.
- A self-service dispute/complaints portal beyond the automated double-charge refund.

## Release plan and reasoning

| Release | Content | Why this order |
|---|---|---|
| R0 (months 1–3) | Data model, core write path (results ingestion, amendments), officer search, employer verification API | These have no results-day timing pressure and de-risk the hardest, least reversible decision first — the append-only result model (ADR-002) must be right before real data accumulates under it. |
| R1 (months 4–7) | PIN purchase + reserve/confirm fix, candidate check (browser + USSD/SMS), results-day read-model builder and cache tier, school bulk export | This is the results-day-critical path and the largest single risk to the May deadline; it is sequenced once the underlying data model (R0) is stable, so the read-model builder has a fixed shape to read from. |
| R2 (months 8–9) | Load testing against results-day volumes, reconciliation job hardening, cutover runbook, legacy archive migration completion | Final hardening before the May sitting; nothing new is built here — this window exists because the brief's own numbers (150x traffic spike, once a year, no second chance) make a dress rehearsal non-optional. |

## Metrics that say whether Release 1 worked

- Result-check success rate >= 99.95% measured over the results-day peak hour (matches the BRD figure).
- Zero manually-detected double charges; automated detection/refund rate = 100% of true duplicates found in the nightly reconciliation job (measured against the payment partner's settlement file).
- School export files available to all 21,000 schools by 12:00 on results day (not "eventually" — the pre-materialization step must complete before the announced release time).
- 100% of amendments in the sitting carry an officer ID and evidence reference — zero exceptions, since this is a regulatory requirement, not a target.
- Employer verification response contains only Data-Protection-Officer-permitted fields on every response, verified by a fixed test suite of field-leakage checks (out of scope to build, but the FRD specifies exactly what "permitted fields" means so this is testable once built).
