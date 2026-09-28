# Part C.1 — Protocol choice per consumer

## Candidate (2G / feature phone / browser)

**Chosen:** USSD, via a telecom aggregator gateway, as the primary channel; SMS as a fallback for the result content itself; HTTPS/JSON (HTTP/1.1 with keep-alive, TLS 1.3) as a secondary channel for candidates with a data connection.

**Why the others lost.** A plain HTTPS request over a fresh connection costs, before any application data moves: one DNS lookup, one TCP handshake (1 round trip), and one TLS handshake (1 round trip under TLS 1.3, 2 under TLS 1.2) — a minimum of 2–3 round trips before the actual request is even sent. On 2G, a round trip commonly runs 300–500ms or worse under congestion; that is 1–1.5 seconds of pure setup cost before the candidate's exam number and PIN have even been transmitted. USSD avoids this entirely: it rides the existing signalling channel between the handset and the telecom network that is already established for the phone to be reachable at all, so there is no separate connection to set up. This is the layer at which the decision is actually made — it is a transport-layer and session-layer choice (USSD's own session protocol vs. TCP+TLS), not an application-layer one, and it is decided by the numbers (2G round-trip cost, ~150x results-day spike, "no queue" requirement) rather than by preference.

**What breaks if this is wrong.** Forcing every candidate onto browser/HTTPS would mean the population described in the brief — "a large share sit the examination in towns served by 2G," many on feature phones — experiences each check as several seconds of connection setup before any result appears, on top of whatever the results-day load itself costs. That directly produces the complaint volume the Registrar's "no queue" requirement is trying to prevent, just moved from a server-side queue to a client-side one the candidate can't see the cause of.

**Connection reuse.** For the browser/HTTPS path, the server keeps connections alive (HTTP keep-alive) so a candidate's five PIN uses across a session reuse one TLS handshake rather than paying its cost five times, and enables TLS session resumption for a returning candidate.

## School (bulk export, ~400 rows/school)

**Chosen:** HTTPS/REST, HTTP/1.1 or HTTP/2, standard TLS 1.2/1.3.

**Why the others lost.** A school's admin fetches its export once a year; the connection-setup cost that matters so much for the candidate on 2G is negligible here — a school has ordinary internet connectivity and makes one request, not thousands. USSD would be a poor fit for a 400-row bulk payload, which USSD's page-size limits cannot carry at all. No optimisation beyond a standard REST/TLS setup is justified by the numbers.

**What breaks if this is wrong.** Over-engineering this path (e.g., a custom binary protocol to save milliseconds) would spend Integrations-engineer time (a scarce resource per the WBS) solving a round-trip-cost problem that does not exist for this consumer.

## Employers' association (up to 500,000 verification calls/month, machine-to-machine)

**Chosen:** HTTPS/REST with HTTP/2 and persistent, pooled connections; mutual TLS (Part C.2).

**Why the others lost.** At 500,000/month (~0.19/sec average, but arriving from the association's own systems, likely in bursts around business hours or in batches around employer request volume), the cost that matters is not per-request round-trip latency but the overhead of repeatedly establishing new connections from a data-centre client making many calls. HTTP/2 multiplexing over a small pool of long-lived connections amortises the handshake cost across many requests, which is the application-layer and transport-layer decision that matters here — the opposite emphasis from the candidate channel, where the handshake itself had to be eliminated.

**What breaks if this is wrong.** Forcing the association onto a per-request-new-connection model (no keep-alive, HTTP/1.0-style) would multiply TLS handshake and certificate-verification overhead by 500,000/month for no benefit, and one slow or stalled request on a non-multiplexed connection would queue every request behind it from that same client — exactly the "one slow response blocking the queue behind it" failure mode this decision is chosen to avoid.
