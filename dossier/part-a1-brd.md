# Part A.1 — Business Requirements Document

## The problem

The Council releases one national examination's results once a year and answers verification requests from employers and universities year-round. Today this runs on a 2009 system with no institutional memory attached to it. That system already fails its users in a measurable way: **9,100 candidates were charged twice** for their result-checker PIN last year, with no automated way to detect or refund the duplicate. It also has no stated capacity story for the concentrated demand of results day — 1,400,000 checks in the first hour, peaking near 2,900 a second — against the eleven-month baseline of under 20 a second.

Three groups suffer under the current arrangement. **Candidates**, some on 2G with feature phones, risk being charged twice for a result they cannot get through to check on the day it matters most. **Employers and universities**, whose verification volume is contracted to grow twelve-fold over the coming year (40,000 to 500,000 a month), need a channel that can absorb that growth without a matching twelve-fold cost. **The Council itself** carries regulatory exposure: it must be able to reproduce any released result exactly as it stood on any past date for fifty years, and trace every amendment to the officer who made it — a guarantee a 2009 system with no documented architecture cannot be assumed to provide today.

## What success looks like

Success is checkable, not aspirational:
- The result-check endpoint answers **99.95% of requests during the results-day peak hour** (<= 22 seconds of failure in that hour).
- Infrastructure spend does not exceed **NGN 14,000,000/month**, including on results day.
- The **9,100-a-year double-charge** figure falls to a number detected and refunded automatically, with zero requiring a human to read a spreadsheet.
- Every amendment carries an officer identity and evidence reference, retrievable on request, for the life of the fifty-year retention window.

## Options considered

1. **Do nothing** — keep the 2009 system, absorb the known double-charge cost and the unmeasured results-day risk. Rejected: the double-charge problem is already quantified and costing candidates money on every sitting, and the employers' association growth (12x within a year) has no ceiling on the current system's demonstrated capacity.
2. **Rebuild everything as one always-on, horizontally scaled service** sized to the results-day peak year-round. Rejected: this is the option that violates the Finance Director's flat NGN 14,000,000/month ceiling directly — provisioning for a 150x spike continuously means paying for capacity that sits idle for all but roughly one hour a year.
3. **Recommended: pre-materialize results-day reads, keep a modestly-provisioned transactional core for everything else.** Serve the results-day spike from a flat-cost static/cache tier built before noon, and keep a normally-provisioned relational database for the rest of the year's real workload (verification, school portal access outside results day, amendments, officer search). Full reasoning and rejected architecture patterns are in Part B.

## What the Council is committing to

- **Spend:** infrastructure at the current NGN 14,000,000/month ceiling; no incremental spend proportional to results-day traffic or the employers' association's growth to 500,000 verifications/month.
- **Risk accepted:** an amendment made close to results day will not appear on an already-generated results-day payload until a controlled cache-refresh step runs — see Part B, "What you are not building." The Council accepts a bounded propagation delay for amendments in exchange for a flat-cost, always-fast candidate experience.
- **Risk not accepted:** the fifty-year reproducibility and officer-attributed amendment trail are treated as non-negotiable; every architectural decision that touches results data is constrained by that requirement first.
- **Timeline:** first release live in time for the May sitting (nine months from today), built by a team of six engineers including the author. The Work Breakdown Structure (Part A.4) states explicitly what is cut if that does not fit.
