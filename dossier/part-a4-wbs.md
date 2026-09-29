# Part A.4 — Work Breakdown Structure

Team (Assumption 6): 3 backend/platform engineers, 1 DBA, 1 integrations engineer, 1 QA — six including the author. No package exceeds two engineer-weeks; two related sub-week tasks are merged into one row only where doing so does not push that row past the two-week cap — this table stays a little over the brief's two-page target as a result, on the view that an honestly-capped WBS is worth more than a shorter one built by quietly exceeding the cap. Role/estimate abbreviated: BE=backend, FE=frontend, INT=integrations, DBA, QA, Auth=author.

## R0 — Foundation (months 1–3)

| # | Deliverable | Deps | Role·Est |
|---|---|---|---|
| 1 | Data model schema + partitioning design | — | BE+DBA·2w |
| 2 | Legacy archive extract tooling | 1 | BE·2w |
| 3 | Legacy transform/validate | 2 | DBA·2w |
| 4 | Legacy load + reconcile | 3 | DBA·2w |
| 5 | Results ingestion service | 1 | BE·2w |
| 6 | Amendment write service | 1,5 | BE·2w |
| 7 | Officer identity integration | — | BE·1w |
| 8 | Partial-surname search (trigram) | 1,7 | BE+DBA·2w |
| 9 | Candidate/school ref data loader | 1 | BE·1w |
| 10 | Certificate entity, issuance & response format | 1,5 | BE·2w |
| 11 | Certificate status endpoint, supersession flag & verifier-notification dispatch (FR-405/406/505) | 6,10 | BE·2w |
| 12 | Employer verification API | 1,10 | BE·2w |
| 13 | DPO allow-list sign-off & verification audit logging | 12 | BE·2w |
| 14 | Admin console: search+amend UI | 6,8 | FE·2w |
| 15 | API gateway/v1 scaffold & CI/CD pipeline | — | BE·2w |
| 16 | Auth credential issuance: mTLS (employers) + OAuth2 (schools) | — | INT·2w |
| 17 | Staging + prod provisioning | — | BE·2w |
| 18 | Observability baseline | 17 | BE·2w |
| 19 | Read replicas + lag monitoring | 1 | DBA·1w |
| 20 | Backup / DR strategy | 1 | DBA·2w |
| | **R0 subtotal** | | **39w** |

## R1 — Results-day critical path (months 4–7)

| # | Deliverable | Deps | Role·Est |
|---|---|---|---|
| 21 | PIN reserve/confirm service | 1 | BE·2w |
| 22 | Payment partner integration | 21 | INT·2w |
| 23 | Payment partner contract tests | 22 | INT·1w |
| 24 | Reconciliation job | 21 | INT·2w |
| 25 | Double-charge detect+refund | 24 | INT·2w |
| 26 | Candidate check API (browser) | 5,21 | BE·2w |
| 27 | USSD gateway integration | 26 | INT·2w |
| 28 | SMS channel integration | 26 | INT·1w |
| 29 | USSD/SMS session handling & content review | 27,28 | BE·2w |
| 30 | Read-model: candidate payloads | 5 | BE+DBA·2w |
| 31 | Read-model: school exports | 5,9 | BE+DBA·2w |
| 32 | Object storage + CDN wiring | 30,31 | BE·1w |
| 33 | Cache refresh on amendment | 6,32 | BE·2w |
| 34 | Rate limiting, public endpoints | 26,12 | BE·1w |
| 35 | Candidate browser check page | 26 | FE·2w |
| 36 | School portal (login+download) | 16,31 | FE·2w |
| 37 | School account provisioning | 16 | INT·2w |
| 38 | School onboarding rollout | 37 | Auth·1w |
| 39 | Employer assoc. integration test | 12,16 | INT·2w |
| 40 | QA: FRD test suite | 21–33 | QA·2w |
| 41 | QA: DPO leakage test suite | 12 | QA·1w |
| 42 | End-to-end integration testing | 40,41 | QA·2w |
| | **R1 subtotal** | | **38w** |

## R2 — Hardening (months 8–9)

| # | Deliverable | Deps | Role·Est |
|---|---|---|---|
| 43 | Load-test harness (930->2,900/s) | 32 | QA+BE·2w |
| 44 | Load-test execution + tuning | 43 | BE+DBA·2w |
| 45 | Reconciliation hardening & amendment-refresh runbook | 24,25,33 | INT+BE·2w |
| 46 | Legacy migration verification | 4 | DBA·2w |
| 47 | Security review (TLS/mTLS) | 16 | INT+QA·2w |
| 48 | Final FRD regression pass | 42 | QA·2w |
| 49 | Cutover runbook & officer training/UAT | 42,44,14 | Auth·2w |
| 50 | Legacy dual-run support | 46 | BE·2w |
| 51 | Documentation handover | all | Auth·1w |
| | **R2 subtotal** | | **17w** |

## Capacity check

- **Identified work:** 39 + 38 + 17 = **94 engineer-weeks**.
- **Raw capacity:** 6 engineers × 39 weeks (9 months) = **234 engineer-weeks**.
- **Effective capacity (estimate):** raw less ~20% for meetings, review, onboarding, leave = **~187 engineer-weeks**. Labelled estimate — no figure for this exists in the brief.
- **Headroom:** ~187 - 94 ~ **93 engineer-weeks**.

This totals to something a team of six can finish before the May sitting, with headroom to spare — but the headroom is not slack for new scope. It is reserved because packages 22/23, 27/28, 39 depend on organisations Takarda does not control: the payment partner, the telecom aggregator, the employers' association. One of those running long is absorbed by the reserve; two running long at once is not. If that happens, **what gets cut first is scope already marked deferred in Part B.6** — none of the packages above are cuttable without breaking a Regulator, Finance Director, or results-day commitment already made in the BRD.
