# Part D.5 — What would prove you wrong

Each is a specific, checkable observation — not a feeling that something is slow.

**Query 1 (candidate's own 9 results).** Wrong if the query plan shows anything other than a single-partition index seek returning ~9 rows — e.g. a sequential scan anywhere in the plan — or if measured p99 latency exceeds **50ms** against production-scale data.

**Query 2 (school bulk fetch, ~400 candidates).** Wrong if the plan shows 400 separate index probes (a nested-loop, one-row-at-a-time pattern) instead of one set-based scan, or if rows examined exceeds roughly **2x** the expected ~3,600.

**Query 3 (certificate verification).** Wrong if the plan contains a sequential scan anywhere, or if the returned response ever includes a field outside the Data-Protection-Officer-permitted set (address, phone, exam centre, other subjects) — that second failure mode is a correctness bug, not a performance one, and would be caught by the DPO field-leakage test suite (WBS package 46) before it reached this stage.

**Query 4 (Mathematics grade count by state).** The claim under test is "this does not need to be fast." Wrong if this report is ever observed taking longer than **5 minutes** on a read replica, or if anyone puts it on a live, user-facing path rather than running it as a scheduled batch report — at that point the "doesn't need to be fast" premise no longer holds and the declined covering index (Part D.4) should be reconsidered.

**Query 5 (partial-surname search).** Wrong if, with the trigram index in place, the planner still falls back to a sequential scan on `candidate` (visible directly in the query plan), or if measured latency for a typical 4-or-more-character fragment exceeds **1 second**. A slow result for a very short (1–2 character) fragment does *not* falsify the prediction — that case is already named as a known weak point handled by an application-layer minimum-length rule, not a database fix.
