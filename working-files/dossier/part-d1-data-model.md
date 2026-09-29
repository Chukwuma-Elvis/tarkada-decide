# Part D.1 — The data model

## Entities

- **Candidate** — `candidate_id` (PK), `exam_number` (unique), `surname`, `other_names`, `date_of_birth`, `state`, `exam_centre_id` (FK), `phone`.
- **Sitting** — `sitting_id` (PK), `year`, `sitting_type` (MAY | NOVEMBER).
- **Subject** — `subject_id` (PK), `name`.
- **Result** — `result_id` (PK), `candidate_id` (FK), `sitting_id` (FK), `subject_id` (FK). Unique on (`candidate_id`, `sitting_id`, `subject_id`). This row identifies *that a result exists*; it never itself carries a grade.
- **ResultVersion** — `result_version_id` (PK), `result_id` (FK), `grade`, `version_number`, `effective_from`, `recorded_by_officer_id` (FK, nullable — null only for the original load, non-null for every amendment), `evidence_reference` (nullable — null only for the original load), `is_current` (boolean). **Insert-only.** A `Result`'s current grade is the `ResultVersion` with `is_current = true`; every prior version stays in the table unchanged, forever.
- **Amendment** — `amendment_id` (PK), `result_id` (FK), `prior_version_id` (FK -> ResultVersion), `new_version_id` (FK -> ResultVersion), `officer_id` (FK), `reason_code`, `evidence_reference`, `amended_at`.
- **Certificate** — `certificate_number` (PK), `candidate_id` (FK), `sitting_id` (FK), `issued_at`, `status` (`ACTIVE` | `SUPERSEDED`), `superseded_by_amendment_id` (FK, nullable). (Assumption 8: one certificate per candidate per sitting.) Status flips via FR-505; the certificate row is never deleted, so `GET /certificates/{n}/status` (FR-405) always has an answer, including for a certificate superseded decades ago.
- **VerificationEvent** — `verification_id` (PK), `certificate_number` (FK), `requester_account_id` (FK), `requested_at`, `match_outcome`, `fields_returned`. Audit-only; never exposed back to the requester beyond the immediate response. Doubles as the subscription list for FR-406: any employer account with a `VerificationEvent` against a certificate in the trailing 12 months is notified when that certificate's status changes.
- **Pin** — `pin_id` (PK), `idempotency_key` (unique), `amount_kobo` (= 350000), `remaining_uses`, `state`.
- **PaymentAttempt** — `attempt_id` (PK), `pin_id` (FK), `idempotency_key`, `partner_reference` (nullable), `outcome`, `requested_at`, `resolved_at`.
- **ResultCheckEvent** — `check_id` (PK), `pin_id` (FK), `exam_number`, `sitting_id`, `checked_at`, `outcome`. One row per PIN use; supports FR-202's exhaustion rule and fraud/audit review.
- **School**, **SchoolCandidateEnrollment** (`school_id`, `candidate_id`, `sitting_id`) — scopes the bulk export to a school's own candidates (FR-303).

## Cardinality

Candidate 1—* Result (9 per sitting, per the brief's average, × however many sittings a candidate sat). Result 1—* ResultVersion (>=1, append-only). Amendment references exactly two ResultVersions (prior, new) and one officer — never zero, never more. Candidate 1—* Certificate (one per sitting sat). Pin 1—* PaymentAttempt (normally one; more only on partner timeout/retry). Pin 1—<=5 ResultCheckEvent.

## Money

`amount_kobo` and every payment-related figure is a whole number of minor units (kobo). No monetary value in this model is ever a decimal or floating-point type.

## Why this shape, for the Regulator's requirement

A single mutable `grade` column cannot answer "what did this say on 14 March 2019" once it has been overwritten. Here, that question is answered by selecting the `ResultVersion` for a `Result` whose `effective_from` is the latest one at or before the requested date — a query over immutable rows, not a reconstruction from a separate audit log that might drift from the "real" table. **A result row is never updated in place.** The `Result` row is stable identity only; every value it has ever held is a distinct, permanent `ResultVersion` row, and an amendment is the act of creating one more.
