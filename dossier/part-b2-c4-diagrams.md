# Part B.2 — C4 diagrams

Diagrams are submitted as files in the repository (`diagrams/*.drawio`, editable in diagrams.net / draw.io), per the submission rule that diagrams belong in the repository as files rather than as images pasted into this PDF. This section describes each one and states what it deliberately leaves out.

## System Context — `diagrams/context.drawio`

Shows Takarda and every external party it exchanges data with at run time: the Candidate, the School, the Council Officer, the Regulator/Council Board, the Employers' Association, the Payment Partner, and the Telecom Aggregator that carries USSD/SMS traffic.

**What it deliberately leaves out:** the legacy 2009 system (a one-time migration source, not a running dependency once the platform is live), any internal Council system not touched by this platform (finance, HR), and the author's own build/deploy tooling. A context diagram answers "who does this system talk to," not "everything the Council operates."

## Container — `diagrams/container.drawio`

Shows the runnable pieces: the API Gateway/Edge; the Public Read Service (serving both candidate checks and school exports, reflecting ADR-001's decision that these two consumers share the same static-tier design); the PIN & Payment Service and its Reconciliation Job; the Results & Amendment Service; the Verification Service; the Officer Console; the Read-Model Builder; the Message Broker carrying amendment events; and the three data stores — the primary PostgreSQL database, its read replicas, and the object storage/CDN tier that holds pre-materialized results-day payloads.

**What it deliberately leaves out:** the specific deployment topology (containers, VMs, or managed services), the cloud provider, and exact scaling numbers for each service — those are implementation and capacity decisions, not architectural ones, and the brief does not ask for a capacity model beyond what the decisions themselves need.

## Component — `diagrams/component-read-model.drawio`

Zooms into the **Read-Model Builder**, chosen as the part of this system most likely to be got wrong, because it is the exact seam where two decisions that are individually simple — ADR-001 (flat-cost, instant reads via pre-materialization) and ADR-002 (amendments are versioned, never instant) — have to coexist without either silently losing an amendment or publishing a half-built payload. It shows the Refresh Scheduler (drives the pre-release full build and the post-release scheduled ticks), the Amendment Event Consumer and Dirty-Set Tracker (track which candidates/schools need regeneration without rebuilding everything on every amendment), the two generators, a Consistency Checker (a row-count sanity check that exists specifically to catch a partial or corrupt build before it goes live), and the Publisher (an atomic/versioned write, so a reader never sees a half-updated results set).

**What it deliberately leaves out:** the exact queueing/backoff mechanism between the event consumer and the dirty-set tracker, and the specific refresh-cycle interval — both are operational tuning parameters to be set from real results-day load-test data (WBS package 49), not architectural commitments to make on paper now.
