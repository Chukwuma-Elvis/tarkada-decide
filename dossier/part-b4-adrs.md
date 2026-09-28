# Part B.4 — Architecture Decision Records

## ADR-001 — Pre-materialized static read tier for results-day traffic

**Context.** Results-day traffic reaches ~2,900 checks/second at peak against an eleven-month baseline under 20/second, while infrastructure cost must stay flat at NGN 14,000,000/month (Conflict A/B).

**Decision.** Before the announced release time, generate every candidate's result payload and every school's export file and publish them to object storage behind a CDN. Serve all results-day candidate and school reads from that tier; none touch the primary database.

**Alternatives.** (1) Scale the primary database and application tier to absorb the peak directly — rejected, breaks the flat-cost requirement (Part B.3). (2) Queue requests and drain them gradually after noon — rejected, directly violates the Registrar's "no queue, no waiting page" requirement.

**Consequences.** Candidate and school reads are cheap and flat-cost at any volume. In exchange, the payload is a snapshot: a correction made in the minutes before release, or during the results-day window itself, is not reflected until the next scheduled refresh (see ADR-002, Part B.6).

**One-way door?** No. The static tier can be replaced by a live-read design later without invalidating historical data, since it only affects how current data is served, not how it is stored.

**Reversal signal.** If the measured cost of the static tier plus its refresh jobs exceeds NGN 14,000,000/month for two consecutive results days, or if candidate complaints about stale post-amendment data during the results-day window exceed an agreed threshold set with the Head of Operations, the Engineering Lead reassesses this decision before the next sitting.

---

## ADR-002 — Results are append-only versioned records, never updated in place

**Context.** The Regulator requires any released result to be reproducible exactly as it stood on any past date for 50 years, with every amendment traceable to an officer and evidence. A mutable "current grade" column cannot satisfy this once overwritten.

**Decision.** A result's grade is never stored as a single mutable value. Each result is a logical entity (`Result`) with one or more immutable `ResultVersion` rows; an amendment creates a new version and links it to the prior version, the acting officer, and the evidence reference, without altering the prior version.

**Alternatives.** (1) A single mutable result row plus a separate audit log table recording old values — rejected: the audit log becomes the actual source of truth for reproducibility while the "real" table is not authoritative for its own history, which is a fragile split to maintain correctly for 50 years. (2) Full event sourcing of every field on every entity — rejected: the Regulator's requirement is specifically about results and amendments, not about every entity in the system; applying event sourcing everywhere adds complexity the brief's requirements do not ask for.

**Consequences.** Storage grows with every amendment rather than staying flat (acceptable: amendments run ~475/sitting, a tiny fraction of ~17,000,000 results/sitting). The Head of Operations does not get retroactive rewriting of a verification result an employer already has in hand (Conflict C) — this is the trade this decision makes on their behalf.

**One-way door?** Yes. Once real candidates' results have accumulated 18+ years of history under this model and that history has been relied on for verification and regulatory purposes, migrating to a different storage model without breaking continuity of the reproducibility guarantee already extended to the Regulator is not practically reversible.

**Reversal signal.** This is not expected to be reversed. If it were ever reconsidered, the trigger would be the Regulator formally withdrawing the 50-year reproducibility requirement — the Compliance Lead would be the one watching for that, since no other observation makes this decision worth revisiting.

---

## ADR-003 — PostgreSQL as the primary data store

**Context.** The workload is relational with strong integrity needs: exact-once PIN/payment handling, atomic linking of a `ResultVersion` to its `Amendment` and officer, and uniqueness constraints across candidates, sittings, and subjects.

**Decision.** Use PostgreSQL as the transactional primary, with read replicas for year-round read traffic outside the results-day static tier.

**Alternatives.** (1) A document store (e.g. MongoDB) — rejected: the amendment/versioning integrity model needs multi-row atomic transactions and relational constraints (candidate+sitting+subject uniqueness, foreign-key integrity linking officers to amendments) that a document model supports less naturally, and the Council's grade-count and partial-name queries are exactly the join/aggregate shapes a relational engine is built for. (2) A distributed NewSQL engine (e.g. a globally-distributed SQL cluster) — rejected: actual write volume (~17,000,000 result rows per sitting, twice a year, batch-loaded; ~475 amendments/sitting) is far below the scale that justifies that operational complexity, and the results-day read-scaling problem is already solved by ADR-001, not by the database.

**Consequences.** A single, well-understood engine that a six-person team can operate confidently within nine months. In exchange, horizontal write scaling is not available if write volume grows by orders of magnitude in the future — not expected given the numbers in this brief.

**One-way door?** No. A relational engine can, with real migration effort, be swapped for another relational engine later without changing the data model's shape.

**Reversal signal.** If sustained write throughput to the primary (outside batch-load windows) exceeds 70% of provisioned capacity for three consecutive months, the DBA raises this for reassessment.

---

## ADR-004 — Partition the results archive by examination sitting

**Context.** The archive will hold ~216,000,000 subject results across 18 years, growing every sitting, and must retain everything for 50 years. Every query in Part D is scoped to a single sitting.

**Decision.** Partition the `Result`/`ResultVersion` tables by sitting (year + sitting type). Older partitions can be moved to cheaper storage tiers without touching the active partition.

**Alternatives.** (1) No partitioning, one large table — rejected: every index on a single 216,000,000-row table grows without bound and every sitting-scoped query (all five in Part D) pays the cost of an ever-larger index even though it only ever needs one sitting's slice. (2) Partition by candidate region/state — rejected: none of the five required query shapes filter by region as their primary access path; this would optimize a query the brief does not ask for (the one query that does group by state, Query 4, is a low-frequency report that does not need this).

**Consequences.** Sitting-scoped queries stay fast and flat-cost as the archive grows (Part D.3). In exchange, any query that must span many sittings at once (e.g., a candidate's full 18-year transcript) touches multiple partitions — accepted, since no stakeholder in this brief asks for that access pattern at results-day speed.

**One-way door?** Yes. Once 18 years of data (24,000,000 candidates, ~216,000,000 results) are relied upon under this partitioning scheme for active verification (growing to 500,000/month) with no permitted downtime, re-partitioning that volume of live, legally-significant data is a major, risky migration, not a routine change.

**Reversal signal.** If a genuinely new access pattern emerges that must span all sittings for a single candidate at results-day latency (not currently required by any stakeholder here), the Engineering Lead and DBA jointly reassess before committing further sittings to this scheme.

---

## ADR-005 — A distinct protocol per consumer class, not one uniform API

**Context.** Three consumers have incompatible constraints: a candidate on 2G/feature phone, a school pulling ~400 rows once a year, and the employers' association making up to 500,000 calls/month from a data centre.

**Decision.** Candidates are served primarily via USSD/SMS through a telecom aggregator, with a lightweight HTTPS/JSON path for those with data access; schools and the employers' association are served via a conventional HTTPS/REST API.

**Alternatives.** (1) One HTTPS/REST API for all three, with the candidate channel required to have data connectivity — rejected: the Council has explicitly ruled out a design that only serves people with good phones and signal, and a large share of candidates sit the exam in towns served by 2G. (2) One custom binary protocol for all three, optimized for the lowest-capability client — rejected: this would under-serve the employers' association's need for a well-documented, contract-grade REST interface it can integrate against, for no benefit to that consumer.

**Consequences.** Three integration surfaces to build and operate instead of one, spread across the WBS's Integrations role. In exchange, no consumer is forced onto a protocol mismatched to its constraints — full reasoning in Part C.1.

**One-way door?** No. Additional channels can be added later (e.g., a mobile app) without displacing the existing three.

**Reversal signal.** If USSD/SMS usage falls below a small fraction of candidate checks (say, under 5%) for two consecutive sittings, indicating the population has moved to data-capable devices faster than assumed, the Product Lead reassesses whether that channel still earns its operating cost.

---

## ADR-006 — Differentiated authentication per consumer class

**Context.** The employers' association is a machine client under contract; schools are 21,000 independently-administered accounts; candidates are anonymous one-off users with only a PIN and exam number.

**Decision.** The employers' association authenticates by mutual TLS client certificate. Schools authenticate by OAuth2 client-credentials bearer token issued at onboarding. Candidates on USSD/SMS are trusted at the level of the telecom aggregator's session and authenticated at the application layer only by PIN + exam number; browser candidates use server-side TLS only, with the same PIN + exam number model.

**Alternatives.** (1) Bearer tokens for everyone, including the employers' association — rejected: a token can be copied and replayed from any machine, whereas a certificate-pinned mutual TLS connection ties the association's calls to a specific, revocable machine identity appropriate to a contracted B2B relationship. (2) Mutual TLS for schools as well — rejected: managing certificate issuance, rotation, and revocation for 21,000 independently-administered school accounts is an operational burden disproportionate to the risk; a revocable bearer token is simpler to issue and to cut off per-school if compromised.

**Consequences.** Three authentication mechanisms to build, document, and operate rather than one. In exchange, each consumer's authentication strength is proportionate to its actual trust relationship with Takarda.

**One-way door?** No. A consumer class's authentication mechanism can be upgraded later (e.g., moving schools to mutual TLS) without affecting the other two.

**Reversal signal.** If a school credential compromise incident occurs, the Security Lead reassesses whether bearer tokens remain adequate for that consumer class.

---

## ADR-007 — Reserve/confirm idempotency for PIN purchase, built on Takarda's side

**Context.** The payment partner charges the card at PIN issuance and accepts no idempotency key; this caused 9,100 double charges last year.

**Decision.** Takarda creates a PIN record in `PENDING_PAYMENT` state, keyed by a client-supplied idempotency key, before calling the partner. A repeated request with the same key returns the existing record instead of charging again. If the partner's response times out, the PIN is held in `AWAITING_CONFIRMATION` and resolved by an asynchronous reconciliation job, never by re-calling the partner from the client's retry. Full flow in Part C.4.

**Alternatives.** (1) Wait for the payment partner to add idempotency-key support — rejected: it is stated as not supported today, and the fix must exist for the May sitting; waiting on a third party's roadmap is not a decision Takarda controls. (2) Deduplicate only on the client side (e.g., disable the "buy" button after one tap) — rejected: this does not protect against network-level retries, timeouts, or a candidate reloading the page, which is exactly the failure mode that produced 9,100 double charges.

**Consequences.** Takarda carries the complexity of a state machine and a reconciliation job that would otherwise sit with the payment partner. In exchange, the double-charge problem is fixed without depending on the partner changing anything.

**One-way door?** No. If the partner later adds idempotency-key support, Takarda's reserve/confirm layer can be simplified without changing the PIN data model.

**Reversal signal.** If the payment partner announces native idempotency-key support, the Integrations engineer reassesses whether the reconciliation job can be retired in favour of relying on the partner directly.

---

## ADR-008 — URI-path API versioning with a minimum 12-month support window

**Context.** Schools integrate with the API infrequently (once a year, around results day) and are the consumer most likely to be running against an old version without realising it.

**Decision.** Version the API in the URI path (`/v1/...`, `/v2/...`). A version remains supported for a minimum of 12 months after a successor version ships, with `Deprecation` and `Sunset` response headers on the old version once a successor exists.

**Alternatives.** (1) Header-based versioning (e.g., an `Accept` media-type parameter) — rejected: it is easy for a school's contracted developer, who touches this integration once a year, to omit or get wrong silently, whereas a URI path is visible in every request they already have working. (2) No formal versioning, evolve the API in place with backward-compatible changes only — rejected: the PIN purchase fix, the DPO field allow-list, and the amendment-visibility model are all changes substantial enough that "backward compatible only" cannot be guaranteed to hold for the life of the platform.

**Consequences.** Takarda must run and support more than one API version simultaneously for at least 12 months after any breaking change. In exchange, a school that has not re-integrated since last results day keeps working.

**One-way door?** No. The versioning scheme itself can be changed for a future major version without affecting already-issued versions' behaviour.

**Reversal signal.** If maintaining two live versions simultaneously ever pushes a results-day load test outside its target margins, the Engineering Lead reassesses the minimum support window length (not the versioning approach itself).
