# Part C.4 — The PIN purchase, fixed

## The problem restated

The payment partner charges the card at the moment a PIN is issued and accepts no idempotency key. Any retry — a client timeout, a page reload, a flaky 2G connection — risks a second charge. Last year this happened 9,100 times. The fix has to live entirely on Takarda's side of the boundary, since the partner's behaviour cannot be changed for this release (Assumption 3).

## Request flow

1. The client (website, bank terminal, agent app) generates an `Idempotency-Key` once per purchase attempt and sends it with every retry of that same attempt.
2. Takarda looks up the key. If a PIN record already exists for it, Takarda returns that record's current state immediately and **does not call the payment partner again** — this is the core of the fix, and it does not depend on anything the partner supports.
3. If no record exists, Takarda creates a PIN in state `PENDING_PAYMENT` (uses = 0, inactive) in the same transaction as recording the idempotency key, then calls the payment partner to charge 350,000 kobo.
4. The partner responds in one of three ways:
   - **Success** -> PIN moves to `ACTIVE`, `remaining_uses = 5`. Response: HTTP 201 with the PIN code.
   - **Declined** -> PIN moves to `FAILED`. Response: HTTP 402. Nothing was charged; the candidate may retry with a new idempotency key.
   - **No response within the configured timeout** -> PIN moves to `AWAITING_CONFIRMATION`. Response: HTTP 202 with a status-check URL. Takarda genuinely does not know whether the charge landed, and says so rather than guessing.

## State kept

A `PIN` row (idempotency key, state, remaining_uses, amount_kobo) and a `PaymentAttempt` row (partner reference if known, outcome, requested_at, resolved_at) per attempt. The idempotency key is unique at the database level, so two near-simultaneous requests with the same key cannot both create a PIN — the second one is rejected by the uniqueness constraint and re-reads the first one's result instead.

## Resolving an unknown outcome

A reconciliation job polls the payment partner's transaction-lookup-by-reference call (or, failing that, the next daily settlement file — Assumption 3) for any PIN still in `AWAITING_CONFIRMATION` after 15 minutes, and resolves it to `ACTIVE` or `FAILED` based on what the partner's own record shows. The candidate is never asked to resolve this themselves; the status-check URL from step 4 lets the client poll for the outcome once it is known.

## Detecting and refunding a double charge that happens anyway

Even with the above, the partner itself could still charge twice on its own side (a partner-side retry bug, or two genuinely different idempotency keys generated across two separate app sessions by the same candidate). A nightly job matches the payment partner's settlement file against Takarda's PIN ledger, grouping by card token, exact amount (350,000 kobo), and a 30-minute proximity window. Any group with more than one matching charge for what is otherwise the same purchase is flagged automatically; the job calls the partner's refund API for the duplicate charge and records the refund against the PIN record. No spreadsheet, and no human decision, is required for this to happen — matching the Council's own stated cost of the current failure (9,100/year, all currently handled without automation).
