# Part E — AI usage log

Tool: Claude (Anthropic), used throughout as a drafting and reasoning partner for this dossier, working directly from the assignment brief supplied by the student.

## Entry 1 — Stakeholder conflict analysis

**Task given:** Read the brief's stakeholder list and identify which pairs of stated requirements are in direct conflict, and which single request is impossible as written.

**Output:** Three conflicting pairs identified — Registrar vs. Finance Director, Head of Schools vs. Finance Director (same root cause: fixed budget vs. a ~150x results-day traffic spike), and Head of Operations vs. Regulator (amendment visibility vs. 50-year point-in-time reproducibility) — with the third also identified as the impossible-as-written request.

**Verification performed:** Re-checked each conflict against the brief's own stated numbers (NGN 14,000,000/month fixed; <20 checks/sec baseline vs. ~2,900/sec peak; 50-year retention requirement) rather than accepting the framing on first read, to confirm the conflict was forced by the numbers and not an assumption. Held up — no correction needed.

## Entry 2 — Index design for the partial-surname search (Query 5)

**Task given:** Predict the index, access method, and cost for a Council officer's partial-surname search ("matches anywhere in the name") against 24,000,000 candidate rows.

**Initial output:** The first pass toward this answer treated a standard B-tree index on `surname` as sufficient, reasoning by the general habit that "an index makes lookups fast."

**What was actually checked:** How a B-tree index actually supports the SQL `LIKE`/`ILIKE` operator — a B-tree can accelerate a left-anchored prefix match (`'name%'`) via a sorted range scan, because a prefix match aligns with the index's own sort order. A pattern with a leading wildcard (`'%name%'`) has no such alignment; there is no way to seek toward "contains this substring anywhere" in a structure sorted by "starts with."

**What was actually true:** A plain B-tree index on `surname` gives the officer's "anywhere in the name" search no benefit at all — without a purpose-built index, the query falls back to a full sequential scan of all 24,000,000 candidate rows.

**Correction made:** Replaced the plain B-tree recommendation with a PostgreSQL `pg_trgm` trigram `GIN` index, which is designed for substring search, and priced its higher write and storage cost separately from the other four proposed indexes in Part D.4. This is recorded in Part D.3 (Query 5) and Part D.4 as the final, corrected answer — the log entry here documents that the first instinct was wrong and why.

## Entry 3 — OpenAPI contract validation

**Task given:** Produce the API contract as a specification file that validates, per the assignment's submission requirement.

**Initial output:** A spec declared as `openapi: 3.0.3`, using `type: mutualTLS` for the employers' association's security scheme, to represent certificate-based machine authentication (ADR-006).

**Verification performed:** Ran the file through `openapi-spec-validator` (installed locally) rather than assuming it was correct because it "looked right."

**What was actually true:** The validator rejected the file — `mutualTLS` is not a valid `securitySchemes` type under OpenAPI 3.0.x; it was only introduced in OpenAPI 3.1.

**Correction made:** Changed the document version to `openapi: 3.1.0` and re-ran the validator, which then passed with no errors. The validated file is committed at `api/openapi.yaml`.

## Entry 4 — Work Breakdown Structure capacity check

**Task given:** Decompose nine months of work for a six-engineer team into packages of at most two engineer-weeks each, and state honestly whether the total fits.

**Output:** A package list checked against a raw capacity of 234 engineer-weeks (6 x 39 weeks) and an estimated effective capacity of ~187 engineer-weeks after overhead; totals are re-derived in Part A.4 whenever the package list changes.

**What required verification, and how:** This is arithmetic, not a factual claim that could be checked against an external source — verified by recomputing the running totals per phase against the table (Part A.4) rather than trusting a single summed figure. The 20% overhead deduction is explicitly labelled an estimate in the document itself, since no such figure exists in the brief, and no external source was available to check it against.

## Entry 5 — Grading a competing submission surfaced a gap in this one

**Task given:** Independently grade a different student's Takarda submission against the brief, and give a percentage with reasoning.

**Output:** A findings table and a weighted score (~71%), including a note that the competing submission quantified why a *rejected* cloud architecture (serverless + DynamoDB) blew the budget, but never showed a comparable cost argument for its own *chosen* architecture — an asymmetry: rigor applied to what was rejected, not to what was recommended.

**What was actually checked:** Whether this dossier had the identical asymmetry. It did — ADR-001 and Part B.3 argued why a scaled-for-peak monolith and synchronous microservices would each break the NGN 14,000,000 ceiling, but never argued why the *chosen* design stays under it, beyond asserting "flat cost by construction."

**Correction made:** Added a short reasoning paragraph to Part B.3 ("Does the chosen architecture actually fit...") arguing the fit structurally — cost is coupled to data volume (a few GB/day) rather than request rate (the ~150x spike) — rather than inventing specific cloud prices, since the brief explicitly does not require a pricing sheet and fabricated dollar figures would violate the "every number is sourced, measured, or a labelled estimate" rule.

## Entry 6 — Reused two ideas from the competing submission, rejected a third

**Task given:** Take the best parts of the competing submission (Entry 5) and integrate them into this dossier.

**What was reused, and why:** (1) A sharper three-part proof of *why* the Head of Operations' request is impossible (physical boundary, legal/evidentiary causality, distributed-consistency limits) — integrated into Part B.0, strengthening what was previously a one-sentence assertion. (2) A concrete certificate-status/revocation endpoint with a notification to recent verifiers — integrated as FR-405/FR-406, `GET /certificates/{certificateNumber}/status`, and a `SUPERSEDED` status on the `Certificate` entity, giving Conflict C's resolution an actual mechanism rather than only a policy statement.

**What was checked and rejected:** The competing submission's own 2G-latency arithmetic ("TCP (1 RTT = 600ms) + TLS 1.3 (1 RTT = 600ms) requires 1.8 seconds") does not add up — 600ms + 600ms = 1,200ms, not 1,800ms. Rather than reusing the number, Part C.1 was rewritten with the arithmetic shown correctly: TCP + TLS 1.3 is 2 round trips (1.2s at a 600ms RTT), TCP + TLS 1.2 is 3 round trips (1.8s) — the *idea* of putting a concrete number on the handshake cost was worth keeping; the specific number as originally presented was not.
