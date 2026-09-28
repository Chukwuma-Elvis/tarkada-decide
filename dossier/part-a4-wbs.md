# Part A.4 — Work Breakdown Structure

Team (Assumption 6): 3 backend/platform engineers, 1 DBA, 1 integrations engineer, 1 QA — six including the author. No package exceeds two engineer-weeks. Role/estimate abbreviated: BE=backend, FE=frontend, INT=integrations, DBA, QA, Auth=author.

## R0 — Foundation (months 1–3)

| # | Deliverable | Deps | Role·Est |
|---|---|---|---|
| 1 | Data model schema design | — | BE+DBA·2w |
| 2 | Sitting partition + index design | 1 | DBA·2w |
| 3 | Legacy archive extract tooling | 1 | BE·2w |
| 4 | Legacy transform/validate | 3 | DBA·2w |
| 5 | Legacy load + reconcile | 4 | DBA·2w |
| 6 | Results ingestion service | 1 | BE·2w |
| 7 | Amendment write service | 1,6 | BE·2w |
| 8 | Officer identity integration | — | BE·1w |
| 9 | Partial-surname search (trigram) | 1,8 | BE+DBA·2w |
| 10 | Candidate/school ref data loader | 1 | BE·1w |
| 11 | Certificate entity + issuance | 1,6 | BE·1w |
| 12 | Certificate response format | 11 | BE·1w |
| 13 | Employer verification API | 1,12 | BE·2w |
| 14 | DPO field allow-list sign-off | 13 | BE·1w |
| 15 | Verification audit logging | 13 | BE·1w |
| 16 | Admin console: search+amend UI | 7,9 | FE·2w |
| 17 | API gateway + /v1 scaffold | — | BE·1w |
| 18 | mTLS cert issuance (employers) | — | INT·1w |
| 19 | OAuth2 tokens (schools) | — | INT·1w |
| 20 | Staging + prod provisioning | — | BE·2w |
| 21 | CI/CD pipeline | 20 | BE·1w |
| 22 | Observability baseline | 20 | BE·2w |
| 23 | Read replicas + lag monitoring | 1 | DBA·1w |
| 24 | Backup / DR strategy | 1 | DBA·2w |
| | **R0 subtotal** | | **37w** |

## R1 — Results-day critical path (months 4–7)

| # | Deliverable | Deps | Role·Est |
|---|---|---|---|
| 25 | PIN reserve/confirm service | 1 | BE·2w |
| 26 | Payment partner integration | 25 | INT·2w |
| 27 | Payment partner contract tests | 26 | INT·1w |
| 28 | Reconciliation job | 25 | INT·2w |
| 29 | Double-charge detect+refund | 28 | INT·2w |
| 30 | Candidate check API (browser) | 6,25 | BE·2w |
| 31 | USSD gateway integration | 30 | INT·2w |
| 32 | SMS channel integration | 30 | INT·1w |
| 33 | USSD/SMS session handling | 31,32 | BE·1w |
| 34 | USSD/SMS content review | 33 | BE·1w |
| 35 | Read-model: candidate payloads | 6 | BE+DBA·2w |
| 36 | Read-model: school exports | 6,10 | BE+DBA·2w |
| 37 | Object storage + CDN wiring | 35,36 | BE·1w |
| 38 | Cache refresh on amendment | 7,37 | BE·2w |
| 39 | Rate limiting, public endpoints | 30,13 | BE·1w |
| 40 | Candidate browser check page | 30 | FE·2w |
| 41 | School portal (login+download) | 19,36 | FE·2w |
| 42 | School account provisioning | 19 | INT·2w |
| 43 | School onboarding rollout | 42 | Auth·1w |
| 44 | Employer assoc. integration test | 13,18 | INT·2w |
| 45 | QA: FRD test suite | 25–38 | QA·2w |
| 46 | QA: DPO leakage test suite | 13 | QA·1w |
| 47 | End-to-end integration testing | 45,46 | QA·2w |
| | **R1 subtotal** | | **38w** |

## R2 — Hardening (months 8–9)

| # | Deliverable | Deps | Role·Est |
|---|---|---|---|
| 48 | Load-test harness (930->2,900/s) | 37 | QA+BE·2w |
| 49 | Load-test execution + tuning | 48 | BE+DBA·2w |
| 50 | Reconciliation job hardening | 28,29 | INT·1w |
| 51 | Amendment-refresh runbook+drill | 38 | BE·1w |
| 52 | Results-day cutover runbook | 47,49 | Auth·1w |
| 53 | Legacy migration verification | 5 | DBA·2w |
| 54 | Security review (TLS/mTLS) | 18,19 | INT+QA·2w |
| 55 | Final FRD regression pass | 47 | QA·2w |
| 56 | Officer training + UAT | 16 | Auth·1w |
| 57 | Legacy dual-run support | 53 | BE·2w |
| 58 | Documentation handover | all | Auth·1w |
| | **R2 subtotal** | | **17w** |

## Capacity check

- **Identified work:** 37 + 38 + 17 = **92 engineer-weeks**.
- **Raw capacity:** 6 engineers × 39 weeks (9 months) = **234 engineer-weeks**.
- **Effective capacity (estimate):** raw less ~20% for meetings, review, onboarding, leave = **~187 engineer-weeks**. Labelled estimate — no figure for this exists in the brief.
- **Headroom:** ~187 - 92 ~ **95 engineer-weeks**.

This totals to something a team of six can finish before the May sitting, with headroom to spare — but the headroom is not slack for new scope. It is reserved because packages 26/27, 31/32, 44 depend on organisations Takarda does not control: the payment partner, the telecom aggregator, the employers' association. One of those running long is absorbed by the reserve; two running long at once is not. If that happens, **what gets cut first is scope already marked deferred in Part B.6** — none of the packages above are cuttable without breaking a Regulator, Finance Director, or results-day commitment already made in the BRD.
