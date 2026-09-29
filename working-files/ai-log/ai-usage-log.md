# Part E — AI usage log

Tool: Claude (Anthropic), used throughout as a drafting and reasoning partner, working directly from the assignment brief.

**Stakeholder conflicts.** Re-checked the three named conflicts against the brief's own numbers (traffic ratio, budget, retention window) before accepting the framing. Held up, no correction needed.

**Query 5 index design — caught and corrected.** First pass proposed a plain B-tree index on `surname` for the officer's partial-name search. Checked: a B-tree only accelerates a left-anchored prefix match; it gives no benefit against a leading-wildcard pattern, so the query would have fallen back to a full 24,000,000-row scan. Corrected to a `pg_trgm` trigram GIN index and priced its extra write/storage cost separately (Part D.3, D.4).

**OpenAPI spec validation — caught and corrected.** Initial spec declared `openapi: 3.0.3` with a `mutualTLS` security scheme. `openapi-spec-validator` rejected it — that type only exists in 3.1. Bumped the version, re-ran, passed.

**WBS capacity check.** Verified by recomputing per-phase totals against the table rather than trusting one summed figure; the 20% overhead deduction is labelled an estimate since no such figure exists in the brief. The table's page count moved twice during later refinement (3->2 pages via table typography, then back to 3 when a dossier-wide "no orphaned heading" fix pushed the R1 table to a new page as a unit) — both are logged as deliberate, explained trade-offs, not oversights.

**Grading a competing submission.** Found it argued why a rejected cloud architecture blew the budget but never argued why its chosen one fit — checked this dossier for the same asymmetry, found it, and added reasoning (not invented pricing) to Part B.3.

**Integrating that submission's ideas.** Reused its three-part impossibility proof and its certificate-status/notification mechanism (now FR-405/406/505). Rejected its 2G handshake arithmetic — it presented 600ms + 600ms as 1.8 seconds; that's 1.2 seconds — and rewrote Part C.1 with the correct figures for both TLS versions.

**Diagram verification — caught and corrected.** Wrote a script to render each `.drawio` file's actual geometry rather than trusting that valid XML meant a correct diagram. Its first run flagged false overlaps; checked before trusting that result, and found the checker itself was ignoring a `verticalAlign=top` style. Fixed the checker, confirmed all three diagrams are genuinely clean.

**BRD/PRD list rendering — caught and corrected.** Rendering those two pages (flagged as needing more depth) showed bulleted lists rendering as run-on text: a bold lead-in line directly followed by a list with no blank line, which `python-markdown` merges into one paragraph. Fixed in both files; scanned the rest of the dossier for the same pattern.

**Table column overflow — two dead ends, then fixed.** Long `<code>` tokens overflowed table cells since the PDF renderer only wraps at whitespace. First tried character-anywhere wrapping: stopped the overflow but broke ordinary prose mid-word. Then tried an invisible zero-width space after separators: the right idea, but that character isn't in the PDF's font encoding and rendered as a visible box instead. Landed on a plain space after separators, scoped to table cells only, verified at high zoom.
