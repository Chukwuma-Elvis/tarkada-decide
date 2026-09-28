# Part B.6 — What you are not building

## 1. Real-time push notification of amendments

A reasonable person would expect that when a result is amended, the affected candidate, school, and any employer who verified it are automatically notified. **Left out of Release 1** because it requires a new outbound channel (SMS/email delivery, its own cost and failure handling) that has no stakeholder deadline attached to it in this brief, and would compete for the same nine months as the results-day path, which does have a fixed, unmovable deadline. **Revisit when:** amendment volume or complaint volume about "found out late" exceeds a threshold agreed with the Head of Operations, or when the notification infrastructure being built for other purposes (e.g., a future payment receipt) can be reused at marginal cost.

## 2. Self-service live analytics dashboards for the Council

A reasonable person would expect the Council to want live, interactive dashboards (grade distributions, pass rates by state, trends over time) rather than the single post-sitting report this design produces (Part D, Query 4). **Left out of Release 1** because Query 4 has no latency requirement stated anywhere in the brief, and building an interactive dashboard layer on top of it would be optimising for a request nobody has made, at the cost of results-day-critical work. **Revisit when:** the Council explicitly asks for continuous, self-service reporting rather than a per-sitting report — at that point this becomes a new, separately-scoped piece of work, not a Release 1 add-on.

## 3. Any candidate identity check beyond PIN + exam number

A reasonable person would expect stronger proof that the person checking a result is the candidate it belongs to — a photo, a biometric, a second factor. **Left out of Release 1** because the brief describes the existing trust model (PIN + exam number) without flagging it as a known fraud problem, and changing it would touch every channel, including USSD/SMS, where stronger identity checks are hardest to deliver on a feature phone. **Revisit when:** PIN-sharing or impersonation is measured as an actual problem (e.g., via a support-ticket or fraud-complaint volume threshold agreed with the Head of Operations) — not before, since there is no evidence in this brief that it is one today.

## 4. A self-service dispute/complaints portal beyond the automated double-charge refund

A reasonable person would expect a general-purpose portal for candidates to raise any billing or result dispute themselves. **Left out of Release 1** because the one dispute type with a quantified cost in this brief — the double charge — is fixed structurally by ADR-007 without needing a portal at all; a general dispute portal would be built for problems this brief does not enumerate or size. **Revisit when:** a second dispute type is identified and quantified with real volume, the same way the double-charge problem was quantified at 9,100/year.
