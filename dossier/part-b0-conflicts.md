# Part B.0 — The stakeholder conflicts

The brief warns that at least three stakeholder pairs are in direct conflict and one request is impossible as written, and that finding and naming them carries more weight than any diagram in this dossier. They are named here, first, because every later decision — the architecture pattern, the ADRs, the data model — is a response to them, not an independent choice.

## Conflict A — Registrar vs. Finance Director

The Registrar wants every candidate served instantly at noon with no queue and no staggered release. The Finance Director's budget is flat at NGN 14,000,000/month regardless of traffic. Results-day load reaches ~2,900 checks/second at peak against an eleven-month baseline under 20/second — a ~150x spike. Serving that spike live against a database provisioned for the average means paying for peak capacity that sits idle almost all year, which is exactly what the Finance Director has ruled out.

## Conflict B — Head of Schools vs. Finance Director

The same root cause as Conflict A, arriving from a second direction: 21,000 schools each pulling their full result list at the identical noon instant is a second traffic spike competing for the same flat budget.

## Conflict C — Head of Operations vs. Regulator (the impossible request)

The Head of Operations wants an amendment to "appear everywhere immediately, including on certificates an employer has already verified." The Regulator requires every released result to remain reproducible exactly as it stood on any past date, for 50 years, with every amendment traceable to an officer and evidence. Taken literally, Operations' request is impossible on three independent grounds, not just one:

1. **Physical/authority boundary.** Once a verification response has left Takarda's network — printed, screenshotted, filed in an employer's HR system — Takarda has no computational reach over that copy. No API call rewrites a PDF already sitting in someone else's archive.
2. **Legal and evidentiary causality.** What an employer verified on a given date was an accurate statement of the Council's record at that instant. An employment decision may already rest on it. Retroactively mutating that historical fact would break the non-repudiation and evidentiary value the Regulator's 50-year requirement exists to protect in the first place — the two halves of the Head of Operations' own request are in tension with each other, not just with the Regulator.
3. **Distributed-consistency limits.** Even restricted to Takarda's own systems, pushing a change to an unbounded set of external parties with zero-latency, guaranteed delivery and no acknowledgement channel is not achievable without those parties running a persistent connection to Takarda, which they don't.

## Conflict D — Chief Executive vs. the combined stakeholder wishlist

The Chief Executive fixes the constraint that decides everything else: go live for the May sitting, nine months away, with six engineers. Taken together, the Registrar, Head of Schools, Head of Operations, Regulator, DPO, and the employers' association's growth target describe a system whose honestly-decomposed scope exceeds what six engineers can build in that time (Part A.4 shows the arithmetic). This is a capacity conflict, not a technical one, and it is resolved the same way the others are: by naming, in advance, which capabilities are cut to make the date (Part B.6), rather than discovering the shortfall in month eight.

## Conflict E — Data Protection Officer vs. the default shape of a verification API

The default REST instinct for "let an employer check a certificate" is a resource-read endpoint that returns the candidate record it finds. The DPO's requirement — an employer verifying one certificate must never see the candidate's other subjects, address, phone, or examination centre — is in direct conflict with that default, because a generic read naturally returns the row it finds, not a filtered subset of it. This is resolved by never building the generic endpoint at all: the verification API (Part C.3) is a dedicated resource with an allow-listed response shape from the first line of its design, not a general candidate lookup with redaction bolted on afterward.

## The resolution adopted across this dossier

**For A and B:** results-day reads for candidates and schools are served from a pre-materialized static tier built before noon, not from the live database — see ADR-001. This buys the Registrar and the Head of Schools their "instant, everyone, at noon" experience inside a cost envelope that is flat by construction, because cost there scales with data size, not with request rate.

**For C:** "everywhere immediately" is honoured for every *future* access — any new check or verification after an amendment sees the current value at once — but not by rewriting a verification response an employer already has in hand. Results are stored as append-only, versioned records (ADR-002), so the Regulator's reproducibility requirement is served by the same version history that makes "current value" well-defined. To give the Head of Operations the closest thing to their actual request that is still honest, every certificate carries a status-check reference (a URI, rendered as a QR code on the printed certificate) that any holder can re-query at any time: `GET /certificates/{certificateNumber}/status`. When an amendment supersedes a certificate, its status flips to `SUPERSEDED`, naming the amendment and the current value, and Takarda dispatches a status-change notification to any employer who verified that certificate in the trailing 12 months (Part C.3, Part A.3 FR-405/FR-406). This does not rewrite what the employer already has — it gives them an active way to find out it changed, which is the strongest version of "appears everywhere" compatible with the Regulator's requirement.

**For D:** the WBS (Part A.4) is built from the scope that survives after Part B.6's cuts, not the other way around — capacity is not discovered to be short after the fact.

**For E:** the verification endpoint's response shape is a first-class design decision (Part C.3), not a filter applied to a general-purpose one.

**The named cost, stated once here and carried through the rest of this dossier:** the Head of Operations does not get literal retroactive correction of an already-issued verification, and a correction made in the hour before or during results day is not visible on an already-generated payload until the next scheduled refresh. This is treated as the price of Conflicts A and B's resolution, not a separate failure — it is recorded as the lowest-ranked quality attribute in Part B.1, and as the first line of the trade-off register in Part B.5.
