# Part D.3 — Five queries, predicted

All five are scoped to one sitting; the `Result`/`ResultVersion` partitioning (Part D.2) prunes to that sitting's partition before any of the reasoning below even begins, so "does it get slower as the archive grows to 216,000,000 rows" is answered by the partitioning decision first, and repeated only where a query's answer differs from that default.

## Query 1 — Candidate fetching their own 9 results for one sitting, by exam number

- **Index:** unique index on `candidate(exam_number)`; index on `result_version(result_id)` reachable via `result(candidate_id)` within the sitting partition — in practice a composite `(candidate_id)` index local to each `result`/`result_version` partition.
- **Access method:** unique index seek on `exam_number` to resolve `candidate_id`, then an index seek (not a scan) within the pruned sitting partition on `candidate_id`, filtered to `is_current = true`.
- **Rows examined vs. returned:** ~9 examined, 9 returned. Tight — as it should be for a single-candidate lookup.
- **Scaling:** flat as the archive grows to 216,000,000 rows. Partition pruning plus a per-candidate index means this query only ever touches one sitting's partition and one candidate's rows, regardless of how many other sittings or candidates exist.
- **If too slow:** not expected to be. If it ever were, the fix would be a covering index (add `subject_id`, `grade` to the index) to make it index-only — cost: marginally larger index, negligible against the write volume this table already carries.

## Query 2 — School fetching every result for its ~400 candidates, one sitting

- **Index:** `school_candidate_enrollment(school_id, sitting_id)` to get the ~400 `candidate_id`s; `result_version(candidate_id)` (as above) to fetch their results, joined as a single set, not per-candidate.
- **The trap.** The naive approach — loop over the 400 candidate IDs and issue 400 separate point lookups — is the wrong access method for this query, even though each individual lookup is itself efficient. The correct method is one query using `candidate_id IN (…400 ids…)`, letting the planner do a single index scan (an index range/bitmap scan feeding a hash or merge join against the enrollment list) in one pass, not 400 round trips.
- **Rows examined vs. returned:** ~3,600 (400 candidates × 9 subjects) examined and returned — tight, once the set-based access method is used.
- **Scaling:** flat with archive growth (partition pruning to one sitting); the per-school size (~400) is bounded by real school size, not by archive size. **Note:** on results day this query does not touch the live database at all — it is served from the pre-generated per-school export file (ADR-001). This prediction describes the path taken outside the results-day window, when a school re-downloads later in the year.
- **If too slow:** unlikely at this row count; if a school were ever unusually large (say, thousands of candidates), the fix is the same set-based query — the access method already scales with candidate count, not with a fixed per-request cost.

## Query 3 — Employer verifying one certificate by certificate number + date of birth, DPO-filtered

- **Index:** unique index on `certificate(certificate_number)`; `candidate` reached via its primary key through the join, so no extra index needed there; `result_version` reached via `candidate_id` (already indexed for Query 1).
- **Access method:** unique index seek on `certificate_number` (one row), a primary-key join to `candidate` to compare the supplied date of birth, and an index seek on `result_version(candidate_id)` for the sitting the certificate covers.
- **Rows examined vs. returned:** ~1 certificate + ~9 results examined; the response returned to the caller is smaller still, since the application layer strips every field the Data Protection Officer has not permitted (address, phone, exam centre, other subjects) — the DPO filtering is an application-layer concern, not something the index or query plan does.
- **Scaling:** flat with archive growth — a unique index seek plus partition pruning by the certificate's own sitting.
- **If too slow:** not expected to be. No change proposed.

## Query 4 — Council counting candidates by grade in Mathematics, broken down by state, for one sitting

- **This is the query that does not need to be fast at all.** It is a one-off report run by Council staff after a sitting, not a request on any latency-bound path.
- **Index:** `result_version(sitting_id, subject_id)` to narrow to Mathematics rows within the sitting (~1,900,000 rows, since every candidate sits Mathematics) rather than scanning the other eight subjects' ~15,200,000 rows in the same sitting; no further index is added.
- **Access method:** index range scan on `(sitting_id, subject_id)` narrowing to Mathematics, joined to `candidate.state`, aggregated by `GROUP BY state, grade`.
- **Rows examined vs. returned:** ~1,900,000 examined, a few hundred returned (state × grade buckets). A large gap — but this is the *expected*, correct shape for an aggregate query, not a missing-index signal: the aggregate genuinely needs to touch every Mathematics row in the sitting to count it.
- **Scaling:** does not get slower as the *total* archive grows toward 216,000,000 rows, because partition pruning limits it to one sitting's Mathematics rows regardless of how many other sittings exist — but it is, and remains, proportional to that one sitting's own size (~1,900,000), which is fixed by the exam's own scale, not by the archive's age.
- **If it were made faster:** a covering index adding `state` and `grade` to the `(sitting_id, subject_id)` index would make this index-only — deliberately **not done** (see Part D.4): it would add write overhead to every one of ~17,000,000 result rows loaded per sitting for a report with no latency requirement. Run on a read replica, off the results-day path, at minutes-not-milliseconds cost, this query needs no further optimisation.

## Query 5 — Officer searching by partial surname, matching anywhere in the name

- **The trap.** A plain B-tree index on `surname` does not help this query at all. A B-tree accelerates a left-anchored prefix match (`surname LIKE 'oko%'`) via a sorted-order range scan, but a pattern with a leading wildcard (`surname LIKE '%oko%'`) has no relationship to the index's sort order — there is no way to seek to "contains oko anywhere" in a structure sorted by "starts with." Without a purpose-built index, this query falls back to a full sequential scan of the `candidate` table.
- **Index:** a trigram index (PostgreSQL `pg_trgm` extension, `GIN` index) on `surname` (and `other_names`), which decomposes each name into overlapping 3-character fragments and can be searched for "contains this fragment" efficiently.
- **Access method:** with the trigram index, a bitmap index scan over matching trigrams, rechecked against the actual pattern; without it, a sequential scan of all 24,000,000 candidate rows.
- **Rows examined vs. returned:** with the trigram index, examined rows are roughly proportional to the number of trigram matches for the searched fragment — much smaller than 24,000,000, though still larger than the handful actually returned, since trigram matching is a filter, not an exact match, and every candidate hit needs a final recheck against the literal pattern. Without the index, examined ~ 24,000,000 to return perhaps a handful — a genuine problem signal here, unlike Query 4's aggregate, because this is an interactive tool an officer is sitting in front of.
- **Scaling:** without the trigram index, cost grows linearly with the candidate table's size — a full scan gets worse every year as more candidates are added. With it, cost grows much more slowly (roughly with the number of trigram matches, not the table size), though not perfectly flat, since more candidates means more trigram collisions for common fragments.
- **If too slow even with the index:** for very short or very common fragments (e.g. a 2-letter search matching a huge number of trigrams), the fix is a minimum-fragment-length rule enforced at the application layer (e.g. require at least 3 characters) rather than a database change — the cost of *not* doing this is an officer-facing search that occasionally degrades to something close to the no-index case for the most common short fragments.
