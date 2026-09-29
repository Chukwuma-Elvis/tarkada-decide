# Part B.1 — Quality attributes, ranked

Each attribute is written as a scenario with a number, not a single word. Ranking follows the scenarios; each entry states what the ranking costs.

## 1. Cost predictability (highest)
**Scenario:** Monthly infrastructure spend does not exceed NGN 14,000,000, including the results-day peak hour, for the first two years.
**Cost of ranking it first:** every other attribute below is architected to fit inside this ceiling rather than the reverse. Specifically, it forces the read path off the live database during results day (Part B.3), which is the single decision most other decisions in this dossier trace back to.

## 2. Availability during the results-day window
**Scenario:** The result-check endpoint answers 99.95% of requests during the results-day peak hour, which allows twenty-two seconds of failure in that hour.
**Cost:** buys almost all its safety margin from pre-computation before noon, not from real-time scaling — so anything that must be computed live at the moment of the check (a fresh database read, a live permission check against changing data) is a liability we deliberately avoid on this path.

## 3. Auditability and 50-year reproducibility
**Scenario:** Any result released to a candidate, school, or employer can be reconstructed exactly as it stood on any date up to 50 years after release, and every amendment names the officer and evidence that produced it.
**Cost:** results are never updated in place (Part B.4, ADR-002). This costs storage (every version is kept, not overwritten) and costs the Head of Operations the "instant everywhere" amendment experience they asked for — see Conflict C in this dossier's framing.

## 4. Accessibility on low-end devices
**Scenario:** A candidate on a 2G connection with a feature phone, using USSD or SMS with no browser, completes a result check in one session without a data connection.
**Cost:** the candidate-facing payload and protocol are designed for the worst device and network in the population, not the average one — richer experiences (result history, certificate download, formatted transcripts) are pushed to the browser channel and explicitly excluded from USSD/SMS (FR-604).

## 5. Confidentiality of verification responses
**Scenario:** An employer verifying one certificate by certificate number and date of birth receives only the certificate's validity and the subject grades it covers — never the candidate's other subjects, address, phone number, or examination centre.
**Cost:** the verification endpoint cannot simply reuse the candidate's full result record; it needs its own filtered view, maintained and tested separately from every other read path (FR-401, FR-402).

## 6. Verification throughput growth
**Scenario:** The verification endpoint sustains a twelve-fold increase in monthly volume, from 40,000 to 500,000, without a corresponding increase in cost or latency.
**Cost:** ranked below confidentiality and accessibility because, at 500,000/month, average load is roughly 0.19 requests/second — trivial next to the results-day peak of 2,900/second. The real risk here is not throughput; it is that this channel is a machine client that can retry aggressively, so the cost paid is defensive: rate limiting and connection-reuse design (Part C.1), not extra compute.

## 7. Freshness of amendment visibility (lowest — deliberately)
**Scenario:** A result amendment is visible to every new check, download, or verification within one scheduled cache-refresh cycle, not instantly, during the results-day window.
**Why it is ranked last, and what that costs:** this is the attribute we have agreed to be worse at. An amendment made in the hour before or during results day will not appear on an already-generated candidate payload or school export until the next refresh cycle runs. The Head of Operations feels this cost directly; it is the price paid for attributes 1 and 2 above, and it is why amendments during the sitting are treated as a controlled, scheduled operation rather than a live one (ADR-001, ADR-002).
