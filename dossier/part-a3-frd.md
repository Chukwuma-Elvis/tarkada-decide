# Part A.3 — Functional Requirements Document

Every requirement names a trigger and the observable response to that trigger. Numbering is stable across revisions (gaps are left deliberately for later insertion).

## PIN purchase (FR-100 series)

**FR-101.** When a candidate, agent, bank, or the website submits a PIN purchase request with a payment method and an `Idempotency-Key` it has not sent before, the system creates a PIN record in state `PENDING_PAYMENT`, calls the payment partner to charge 350000 kobo, and does not decrement any usage count.

**FR-102.** When the payment partner confirms the charge succeeded, the system sets the PIN to state `ACTIVE` with `remaining_uses = 5` and returns HTTP 201 with the PIN code.

**FR-103.** When the payment partner confirms the charge was declined, the system sets the PIN to state `FAILED`, returns HTTP 402, and does not create a usable PIN.

**FR-104.** When the payment partner does not respond within the configured timeout, the system sets the PIN to state `AWAITING_CONFIRMATION`, returns HTTP 202 with a status-check URL, and takes no further action until the reconciliation job (FR-108) resolves it.

**FR-105.** When a PIN purchase request arrives with an `Idempotency-Key` that matches an existing record, the system does not call the payment partner again and returns the existing record's current state and outcome.

**FR-106.** When a PIN purchase request arrives with an `Idempotency-Key` that matches an existing record but a different payment amount or method, the system rejects the request with HTTP 409 and does not attempt a charge.

**FR-107.** When a candidate is charged twice for the same purchase attempt (detected by the nightly reconciliation job matching the payment partner's settlement file against Takarda's PIN ledger by card token, amount, and a 30-minute proximity window), the system issues an automatic refund via the payment partner's refund API and records the refund against the PIN record, without requiring a human to review the case.

**FR-108.** When a PIN sits in `AWAITING_CONFIRMATION` for longer than 15 minutes, the reconciliation job queries the payment partner's transaction lookup (or, failing that, the next available settlement file) and transitions the PIN to `ACTIVE` or `FAILED` based on what it finds.

## Candidate result check (FR-200 series)

**FR-201.** When a candidate submits an exam number, sitting identifier, and an active PIN with `remaining_uses > 0`, the system returns the candidate's results for that sitting and decrements `remaining_uses` by one.

**FR-202.** When a candidate submits a PIN that has already been used five times, the system refuses the check, leaves the PIN's remaining count at zero, and returns the message that the PIN is exhausted.

**FR-203.** When a candidate submits a PIN and exam number combination where the exam number does not exist for the stated sitting, the system returns HTTP 404 and does not decrement the PIN.

**FR-204.** When a candidate resubmits a check with the same request `Idempotency-Key` as a prior successful check, the system returns the same stored result and does not decrement `remaining_uses` a second time.

**FR-205.** When a result check request arrives during the pre-materialization window before the announced release time, the system returns HTTP 404 regardless of whether the underlying result exists, since no release has occurred yet.

**FR-206.** When the announced release time is reached, the system serves candidate result checks exclusively from the pre-materialized read tier (Part B, ADR-001), not from a live query against the primary database.

## School bulk download (FR-300 series)

**FR-301.** When an authenticated school requests its result export for a sitting before the pre-materialization job for that sitting has completed, the system returns HTTP 202 with a `Location` header pointing to the eventual file.

**FR-302.** When an authenticated school requests its result export for a sitting after pre-materialization has completed, the system returns HTTP 200 with a downloadable file containing exactly the candidates enrolled at that school for that sitting.

**FR-303.** When a school requests results for a candidate not enrolled at that school, the system excludes that candidate from the response; a school never receives another school's candidate.

## Verification request (FR-400 series)

**FR-401.** When the employers' association submits a certificate number and a date of birth that match a candidate's record, the system returns HTTP 200 with only the fields the Data Protection Officer has designated as permitted (certificate validity, sitting, subject grades tied to that certificate) and excludes the candidate's other subjects, address, phone number, and examination centre.

**FR-402.** When the certificate number does not exist, or exists but the date of birth does not match, the system returns the same generic "no match" response and status code in both cases, so that a caller cannot distinguish a wrong certificate number from a wrong date of birth.

**FR-403.** When a verification request is received, the system records a verification event (timestamp, requesting account, certificate number, outcome) for audit, regardless of whether the request matched.

**FR-404.** When the same certificate is verified again after an amendment has changed its underlying result, the verification response reflects the current (post-amendment) value, not the value that was current at the time of any earlier verification.

## Amendment workflow (FR-500 series)

**FR-501.** When an authenticated Council officer submits an amendment for a result with a reason code and an evidence reference, the system creates a new, immutable result version, links it to the amendment record, the officer's identity, and the prior version, and never overwrites the prior version's stored values.

**FR-502.** When an amendment is submitted without an evidence reference, the system rejects the request with HTTP 400 and creates no amendment record.

**FR-503.** When an amendment is recorded, the system marks the result as changed for the next scheduled read-model refresh; it does not attempt to update the results-day static payload already generated for that candidate in real time.

**FR-504.** When any party requests the value a given result held as of a specific past date, the system reconstructs it from the version history and returns the version that was current on that date, never the latest version, unless the two happen to be the same.

## USSD / SMS channel (FR-600 series)

**FR-601.** When a candidate dials the published USSD short code and enters an exam number, sitting code, and PIN through the USSD menu, the system performs the same check as FR-201 through the telecom aggregator gateway and returns the result formatted to fit a single USSD screen (<= 182 characters per the common USSD page limit).

**FR-602.** When a candidate's USSD session times out before completing the PIN entry (per the telecom aggregator's session limit), the system does not decrement the PIN's `remaining_uses`, since no check request was completed.

**FR-603.** When a candidate sends an SMS in the published format (exam number, sitting code, PIN) to the published number, the system replies by SMS with the same result content as the USSD channel, or with a specific error message if the format is invalid.

**FR-604.** When a candidate on the USSD/SMS channel completes a check successfully, the response contains no data beyond what fits the channel's character limit — grade per subject and nothing else — deferring any richer detail (full transcript, certificate download) to the browser channel.
