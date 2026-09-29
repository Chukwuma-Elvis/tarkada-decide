# Part C.3 — The API contract

The full machine-readable contract is in the repository at `api/openapi.yaml` (OpenAPI 3.1, validated with `openapi-spec-validator` — see repository README for how to check it). This section states the design decisions behind it.

## Resources, not actions

Every URL names a thing: `/pins`, `/result-checks`, `/schools/{schoolId}/sittings/{sittingId}/results`, `/certificates/{certificateNumber}/verifications`, `/certificates/{certificateNumber}/status`, `/amendments`, `/results/{resultId}`, `/results/{resultId}/versions`. There is no `/checkResult` or `/verifyCertificate` — an action becomes the creation of a resource that represents that event (a "verification," a "result check," an "amendment") rather than a verb bolted onto a noun.

## Method, safety, and idempotency, made explicit

| Operation | Method | Safe? | Idempotent? | Why |
|---|---|---|---|---|
| Purchase a PIN | `POST /pins` | No | Yes, via `Idempotency-Key` | Creates a resource (has a side effect: a charge), but the idempotency key makes a retried request return the same result rather than charging again — see ADR-007. |
| Check a result | `POST /result-checks` | No | Yes, via `Idempotency-Key` | Decrements a PIN's remaining uses — a real side effect — so it cannot be `GET`; the idempotency key protects a candidate retrying over a flaky 2G connection from losing a second use for one check. |
| School export | `GET /schools/{schoolId}/sittings/{sittingId}/results` | Yes | Yes | Pure read, no state change; repeating it is harmless. |
| Verify a certificate | `POST /certificates/{certificateNumber}/verifications` | No | No, by design | Not safe, because it writes a verification-event audit record every time (a real side effect the Data Protection Officer and the Regulator both rely on); deliberately not idempotent, because two verification attempts are two auditable events, not one. The date of birth also travels in the body rather than the query string specifically so it is never logged or cached as part of a URL. |
| Record an amendment | `POST /amendments` | No | Yes, via `Idempotency-Key` | A real write with regulatory weight; idempotency protects an officer's form double-submit from creating two amendment records for one action. |
| Read current result / version history | `GET /results/{resultId}`, `GET /results/{resultId}/versions` | Yes | Yes | Pure reads. |
| Check certificate status | `GET /certificates/{certificateNumber}/status` | Yes | Yes | Pure read of validity state only (`ACTIVE`/`SUPERSEDED`) — no date-of-birth challenge, since it returns no subject data at all. This is Conflict C's resolution made concrete (Part B.0): anyone holding a certificate, including years later, can always ask whether it still stands, without Takarda needing to have reached them proactively. |

## Parameters: filter vs. identify vs. body

- **Path parameters identify a specific resource**: `{schoolId}`, `{sittingId}`, `{certificateNumber}`, `{resultId}`, `{pinId}`. These are never optional and never used to filter a collection.
- **Query parameters filter a collection**: e.g. `subject` on the school export endpoint narrows the returned rows without changing which resource is being addressed; `cursor`/`limit` control pagination. A missing or invalid query parameter never returns 404 — it returns 400 (invalid) or is treated as "no filter" (absent), since it is not identifying anything.
- **Body parameters carry data for a create or check operation**: the PIN's payment method, the result-check's exam number/PIN/sitting, the verification's date of birth, the amendment's reason code and evidence reference. Anything the Data Protection Officer requires never to appear in a URL (date of birth, PIN) is a body field, never a query parameter, so it cannot end up in a server access log or a shared cache key.

## Status codes per outcome

Full mapping is in the spec; the pattern is consistent: `200`/`201` for a normal success, `202` for "accepted, not yet resolved" (a PIN awaiting payment confirmation, a school export still being generated), `400` for a malformed request, `401`/`403` for missing or insufficient credentials, `404` for a genuinely absent resource, `409` for an idempotency-key conflict (same key, different payload), `422` for a request that is well-formed but cannot be fulfilled as a matter of business rule (a PIN that is exhausted — matching FR-202's exact wording), and `429` for rate limiting. Verification deliberately returns the same status and body shape whether the certificate number does not exist or the date of birth does not match (FR-402), so a caller cannot use the response to enumerate valid certificate numbers.

## Versioning

The API is versioned in the URI path (`/v1/...`), per ADR-008. A version is supported for a minimum of 12 months after a successor version ships; the old version's responses carry `Deprecation` and `Sunset` headers once a successor exists, so a school's integration that has not been touched since last results day continues to work and is told, in-band, that it should eventually move.
