# Part B.0 — The stakeholder conflicts

The brief warns that at least three stakeholder pairs are in direct conflict and one request is impossible as written, and that finding and naming them carries more weight than any diagram in this dossier. They are named here, first, because every later decision — the architecture pattern, the ADRs, the data model — is a response to them, not an independent choice.

## Conflict A — Registrar vs. Finance Director

The Registrar wants every candidate served instantly at noon with no queue and no staggered release. The Finance Director's budget is flat at NGN 14,000,000/month regardless of traffic. Results-day load reaches ~2,900 checks/second at peak against an eleven-month baseline under 20/second — a ~150x spike. Serving that spike live against a database provisioned for the average means paying for peak capacity that sits idle almost all year, which is exactly what the Finance Director has ruled out.

## Conflict B — Head of Schools vs. Finance Director

The same root cause as Conflict A, arriving from a second direction: 21,000 schools each pulling their full result list at the identical noon instant is a second traffic spike competing for the same flat budget.

## Conflict C — Head of Operations vs. Regulator (the impossible request)

The Head of Operations wants an amendment to "appear everywhere immediately, including on certificates an employer has already verified." The Regulator requires every released result to remain reproducible exactly as it stood on any past date, for 50 years, with every amendment traceable to an officer and evidence. Taken literally, Operations' request requires rewriting a verification event that already happened — an impossibility, since a past event cannot be un-happened — and would, if attempted by mutating the underlying record, destroy the exact historical record the Regulator's requirement exists to protect.

## The resolution adopted across this dossier

**For A and B:** results-day reads for candidates and schools are served from a pre-materialized static tier built before noon, not from the live database — see ADR-001. This buys the Registrar and the Head of Schools their "instant, everyone, at noon" experience inside a cost envelope that is flat by construction, because cost there scales with data size, not with request rate.

**For C:** "everywhere immediately" is honoured for every *future* access — any new check or verification after an amendment sees the current value at once — but not by rewriting a verification response an employer already has in hand. Results are stored as append-only, versioned records (ADR-002), so the Regulator's reproducibility requirement is served by the same version history that makes "current value" well-defined.

**The named cost, stated once here and carried through the rest of this dossier:** the Head of Operations does not get literal retroactive correction of an already-issued verification, and a correction made in the hour before or during results day is not visible on an already-generated payload until the next scheduled refresh. This is treated as the price of Conflicts A and B's resolution, not a separate failure — it is recorded as the lowest-ranked quality attribute in Part B.1, and as the first line of the trade-off register in Part B.5.
