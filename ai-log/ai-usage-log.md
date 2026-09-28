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

**Output:** 58 packages totalling 92 engineer-weeks, checked against a raw capacity of 234 engineer-weeks (6 × 39 weeks) and an estimated effective capacity of ~187 engineer-weeks after overhead.

**What required verification, and how:** This is arithmetic, not a factual claim that could be checked against an external source — verified by recomputing the running totals per phase against the table (Part A.4) rather than trusting a single summed figure. The 20% overhead deduction is explicitly labelled an estimate in the document itself, since no such figure exists in the brief, and no external source was available to check it against.
