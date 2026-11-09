# Household optimisation governance, contracts and acceptance

> **PR #46 draft, documentation only. Not approved for implementation, merge or deployment.**
>
> This file preserves the complete text of the cited PR conversation checkpoints, including their original caveats. Early grouped checkpoints are summaries of earlier conversations, **not verified verbatim transfers of every historical discussion**. Later reviews and decision corrections take precedence where they explicitly identify an earlier misclassification. No household action is authorised by this documentation.
>
> Existing baseline: [functional-requirements.md](functional-requirements.md). This appendix does not replace it.

## Source contents

- [GitHub comment 6727739848](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727739848) — PR #46 — FR-OPT-CONSOLIDATION-001: Requirements Consolidation and Gap Analysis
- [GitHub comment 6727758036](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758036) — PR #46 — FR-OPT-CONTRACTS-001: Canonical Data Contracts and Owner Approval State Machines
- [GitHub comment 6727758336](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758336) — PR #46 — FR-OPT-E2E-TEST-001: End-to-End Household Optimisation Acceptance Scenario Catalogue
- [GitHub comment 6727758667](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758667) — PR #46 — FR-OPT-ROADMAP-001: Risk-Based Implementation Sequencing and Dependency Roadmap
- [GitHub comment 6727777320](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727777320) — PR #46 — FR-OPT-OWNER-DECISIONS-001: Consolidated Owner Decision Register
- [GitHub comment 6727781069](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727781069) — PR #46 — FR-OPT-MASTER-INDEX-001: Master Requirements Index and Coverage Reconciliation

---


---

<a id="comment-6727739848"></a>

**Original checkpoint:** [PR #46 comment 6727739848](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727739848)

# PR #46 — FR-OPT-CONSOLIDATION-001: Requirements Consolidation and Gap Analysis

**Status:** Documentation-only draft consolidation assessment. No repository files changed, no merge, deployment, implementation or household modification.

## Review scope and evidence
Reviewed PR #46 description and all **17** existing PR conversation comments at the time of review. These include the early functional/optimisation checkpoints and individual model validation, model governance, monitoring, explainability, trust, decision support, data lifecycle, human oversight, operational readiness, acceptance gates, change impact, experiments and periodic review specifications. This assessment covers **PR conversation documentation**, not a full line-by-line audit of all repository files or implementation code.

## 1. Consolidated functional domains
A. Core conversation/persona/context/guest permissions.
B. Household operations: heating, EV, lighting, media, security and infrastructure.
C. Household intelligence: goals, recommendations, forecasts, scenarios, experiments and planning.
D. Evidence and models: provenance, lifecycle, validation, monitoring, trust, explanations and decision traceability.
E. Safety and governance: owner authority, policy, privacy, incidents, continuity and audit.
F. Delivery and assurance: operational runbooks, integration tests, readiness gates and release controls.

Preserve original FR identifiers and links to their source comments. Do not silently replace individual drafts with this index.

## 2. Overlap register and canonical ownership
| Overlap | Canonical owner | Referencing modules |
| --- | --- | --- |
| Action-specific owner approval, consent and role checks | FR-OPT-HUMAN-OVERSIGHT-001 | Model governance, decision support, experiments, incident response, readiness |
| Data provenance, retention and source classification | FR-OPT-DATA-LIFECYCLE-001 | Validation, explainability, trust, monitoring, digital twin |
| Model lifecycle and advisory eligibility | FR-OPT-MODEL-GOV-001 | Validation, monitoring, controlled learning, release |
| Model accuracy and validation criteria | FR-OPT-VALIDATION-001 | Trust, monitoring, experiments |
| Ongoing quality alerts and monitoring | FR-OPT-MONITOR-001 | Risk forecasting, incidents, operations |
| Recommendation evidence and confidence | FR-OPT-TRUST-001 | Decision support, explainability |
| Explanation fidelity and model-to-decision trace | FR-OPT-EXPLAIN-001 | Trust, decisions, model governance |
| Alternatives and owner choices | FR-OPT-DECISION-001 | Goals, scenarios, portfolio, coordinated optimisation |
| Cross-system dependency and change preview | FR-OPT-CHANGE-IMPACT-001 | Digital twin, continuity, trial design |
| Experiment preregistration and verified outcome | FR-OPT-EXPERIMENT-001 | Controlled trials, benefits verification, model promotion |
| Operational support/runbooks | FR-OPT-OPERATIONS-001 | Continuity, incident response, monitoring |
| Cross-module acceptance and release readiness | FR-OPT-READINESS-GATE-001 | Governance, operations, validation, testing |
| Periodic review and closure status | FR-OPT-REVIEW-001 | All modules |

**Interpretation:** These are predominantly shared concerns, not demonstrated irreconcilable contradictions. Consolidation should use common interfaces and cross-references rather than discard valuable domain-specific safeguards.

## 3. Ambiguities and precedence decisions
1. **Suspension vs no automatic changes:** A read-only monitoring finding or governance status may make a model *ineligible to provide new advisory recommendations* under a preapproved policy, but it cannot autonomously uninstall, deploy, restart, reconfigure or control household services. Define exact enforcement location and independent safety behaviour before implementation.
2. **Notification cap:** The agreed maximum **three routine optimisation recommendations per weekly digest** is shared across modules; credible urgent safety/security alerts are separately governed, not automatically suppressed or permitted to change systems.
3. **Conversation vs records:** The agreed **five-minute conversation retention after last interaction** is separate from privacy-governed persistent audit, consent, model, incident and decision records.
4. **Identity vs authority:** Voice recognition, presence, personality and Guest Mode are not sufficient owner authentication for high-risk action approvals; exact approval factors remain an open design decision.
5. **Research/simulation vs live:** Data collection, scenario calculation, experiment proposal, trial authorisation, software release and live device action are separate gates. A green model score, validated forecast, successful simulation or accepted review is not permission to execute.
6. **Evidence confidence vs model quality vs recommendation trust:** Maintain distinct metrics; a high aggregate score cannot override hard safety/policy failures or critical missing evidence.
7. **Outcome vs execution:** Command accepted, action executed and verified beneficial outcome are distinct states; never report success without the corresponding evidence.
8. **Historical compatibility:** Legacy Jarvis identifiers and entity renames must be audited, not silently globally replaced; preserve HA entity/unique IDs and compatibility pending separate review.

## 4. Open decision register
**OD-01** Confirm actual Declan conversation/STT/TTS identifiers.
**OD-02** Confirm whether the separate bridge is installed and its compatibility obligations.
**OD-03** Decide whether legacy spoken “Jarvis” aliases remain supported.
**OD-04** Approve the routine outcome contract: requested/attempted/executed/verified/error semantics.
**OD-05** Define quiet-hours and urgent notification delivery policy.
**OD-06** Select high-risk owner authentication and approval factors; owner disagreement handling.
**OD-07** Define precise advisory-eligibility suspension enforcement without live changes.
**OD-08** Define canonical schemas and IDs for evidence, model, recommendation, approval, incident, execution and audit events.
**OD-09** Define retention schedules and privacy-safe deletion/audit reconciliation.
**OD-10** Define practical test environment isolation and resource budgets for Proxmox/HA/Frigate.
**OD-11** Determine requirements prioritisation and feasible implementation slices.
**OD-12** Determine which draft requirements are accepted for design and which remain exploratory.

These are **open**, not decisions made by this comment.

## 5. Canonical records required before implementation
- **EvidenceRecord:** ID, source, observed/ingested time, units, quality, sensitivity, lineage, validity, retention.
- **ModelRecord:** ID/version/hash, owner, purpose, dependencies, risk, validation, approved advisory scope, lifecycle.
- **RecommendationRecord:** ID/version, goal, exact proposal, baseline, alternatives, model/evidence references, trust, uncertainty, expiry.
- **ApprovalRecord:** authenticated owner, action/target/parameters, conditions, validity, revocation, separate executor authority.
- **IncidentRecord:** severity, evidence, correlation, affected components, triage, communications, disposition.
- **ExecutionRecord:** separately authorised executor, exact action, attempts, observed state, outcome verification.
- **AuditEvent:** event ID, time, actor, object version, previous/new state, reason, evidence and integrity metadata.

Schemas are proposed requirements, **not implemented API contracts**.

## 6. Gap and priority register
**P0 (before any consequential implementation):** Authority enforcement architecture; canonical approval/execution state machine; trust boundary and guest isolation; non-execution negative tests; immutable audit/provenance; device safety constraints; entity/legacy identifier compatibility.
**P1 (before advisory rollout):** Canonical records; evidence quality and source access; model validation/monitoring/trust distinctions; decision explanations; owner-facing uncertainty; notification delivery and rate limits; resource budgets.
**P2 (before controlled trials):** Pre-registration, digital twin fidelity, confounder analysis, owner-approved trial boundaries, rollback, verified outcome analysis.
**P3 (before full optimisation programme):** Long-term benefits, portfolio governance, strategic roadmaps, broader autonomous research, continuous improvement and retirement cadence.

## 7. Requirement lifecycle and evidence levels
Use: drafted → owner-reviewed → accepted for design → designed → implemented → unit/integration/security-tested → independently validated → owner-accepted → separately approved for release → deployed → verified in production. Do not infer later states from earlier ones. A GitHub PR comment is a **documentation checkpoint**, not a committed repository file or proof of production behaviour.

## 8. Cross-cutting acceptance scenarios
1. Heating prediction advice must not alter Hive schedule or one-hour override without approval.
2. EV charging recommendation must respect the no-auto-top-up rule and owner choice to top to 50% or charge until midnight.
3. Renamed light entity must produce explicit compatibility warning, not an unverified global replacement.
4. Guest Mode and spoofed voice identity cannot approve high-risk changes.
5. Digital twin and shadow evaluation cannot call live HA services.
6. Missing telemetry, model drift and expired validation must reduce claim confidence, not fabricate health.
7. Critical incident alert may notify within approved policy but cannot autonomously deploy, restart or change devices.
8. Model version change invalidates approvals bound to the earlier artefact when material.
9. Proxmox/Frigate resource pressure must not be aggravated by unbounded optional simulation.
10. Failed/unknown execution must not be described as a verified successful outcome.
11. Routine recommendations respect shared three-per-week digest cap.
12. Five-minute conversational reset does not delete separately retained decision/audit evidence.

## 9. Proposed next documentation deliverables
A. Canonical requirement inventory and cross-reference matrix with original comment links.
B. Shared data-contract and approval state-machine specification.
C. Owner decision log for OD-01 through OD-12.
D. End-to-end acceptance scenario catalogue with pass/fail evidence.
E. Risk-based implementation roadmap, only after owner reviews the consolidated requirements.

## Formal requirement
**FR-OPT-CONSOLIDATION-001:** PR #46 shall maintain a traceable consolidated requirements index, canonical ownership of cross-cutting concerns, explicit conflict precedence, open owner decisions, common record contracts, acceptance evidence and separate documentation/implementation/release statuses.

**Non-negotiable:** No consolidation finding, accepted draft, green readiness gate, model score or PR comment authorises implementation, merge, deployment, spending, backup operations, device control or household policy change. All consequential actions require separate explicit owner approval.

**Assessment:** Broad draft coverage, but not yet a single owner-approved, implementation-ready specification.



---

<a id="comment-6727758036"></a>

**Original checkpoint:** [PR #46 comment 6727758036](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758036)

# PR #46 — FR-OPT-CONTRACTS-001: Canonical Data Contracts and Owner Approval State Machines

**Draft documentation only. No code, commits, merge, deployment, purchases or household changes authorised.**

## Purpose
Define interoperable, versioned contracts for evidence, model assessments, recommendations, approvals, incidents, executions and audit events. These are proposed future schemas, not deployed APIs. One canonical permission boundary shall apply across all PR #46 capabilities.

## Shared envelope
Every record: stable UUID/ID, schema_version, object_version, created_at/updated_at UTC ISO-8601, actor_type/actor_id, source, correlation_id, causation_id, classification, provenance_refs, integrity metadata, retention class, redaction flags. IDs immutable; versions monotonic; timestamps distinguish observation from ingestion; no secrets in event payloads. Backward-compatible schema migrations must be explicitly versioned and tested.

## EvidenceRecord
source_type/source_id; observed_at, ingested_at, unit, value or protected reference, precision, quality status (verified/supported/estimated/hypothetical/disputed/unknown), validity period, collection authorisation, lineage/transformations, sensitivity, retention, source integrity. Corrections append superseding records; preserve audit link.

## ModelRecord
model_id/version/hash; owner; intended use and prohibited uses; environment; artefact provenance; data and feature schema versions; dependencies; validation result and expiry; risk tier; monitoring profile; lifecycle state; advisory eligibility. No promotion based on a status field alone.

## RecommendationRecord
recommendation_id/version; household goal; proposed action as structured, exact target/parameters; baseline; alternatives; evidence/model references; confidence components; expected benefit/cost/risks; hard constraints; expiry; status (draft, evaluated, owner review, approved for specified next step, rejected, deferred, expired, superseded); separate approval/execution references. No free-text recommendation becomes an executable command.

## ApprovalRecord
approval_id; authenticated owner; authentication assurance method; action class; exact operation, entity/service IDs and parameters; expected effects and risks acknowledged; proposal/version hash; scope; not_before/expires_at; conditions; revocation; one-time or bounded-use nonce; decision (pending, granted, denied, revoked, expired, consumed); immutable evidence and audit references. No inferred, blanket, guest, voice-only high-risk or silent consent.

## IncidentRecord
incident_id; source alert IDs; severity; affected components; evidence; confirmed vs hypothesised cause; state (new, confirming, active, investigating, awaiting owner, monitoring recovery, resolved, accepted residual risk); assigned owner; notifications and delivery states; remediation proposal; closure evidence. Correlated alerts retain their original IDs.

## ExecutionRecord
execution_id; approval_id; exact command hash; executor identity; environment; target; precondition checks; idempotency key; attempt timestamps; response; observed device/service state; outcome verification; failure/unknown state; rollback reference if separately authorised. Approval granted does not imply execution; API success does not imply physical outcome.

## AuditEvent
append-only event_id, aggregate_id/version, actor, action, prior/new state, timestamp, reason, source/correlation IDs, approval/evidence references, integrity digest, privacy classification. Correct via compensating event; no silent mutation. Retention/deletion exceptions documented.

## State machine and transitions
Approval: proposed -> pending verification -> granted/denied; granted -> consumed/revoked/expired; any ambiguous or failed verification -> denied/no execution. No transition from expired/revoked/denied to executable. Reapproval creates a new ID.

Execution: proposed -> awaiting approval -> approved for execution -> preflight -> dispatched -> observed -> verified OR failed/unknown/partially completed. Execution cannot begin without valid scoped approval, matching proposal hash, target/parameters, current policy, actor authority, time and nonce. Changed proposal invalidates approval. Dispatch timeout is UNKNOWN, never automatic retry of non-idempotent actions.

Incident and recommendation transitions cannot grant execution privileges. Model eligibility may be restricted by preapproved read-only governance but no automatic deploy/rollback/service restart.

## Trust boundaries
Conversation, STT, LLM output, model recommendations, web research, guest input, HA sensor data and GitHub documentation are untrusted as command authority. Enforce authorisation in a separate, least-privileged policy/executor boundary. Never accept instructions embedded in logs, transcripts, source documents or model outputs.

## Idempotency and concurrency
Exactly-once delivery cannot be assumed. Use unique action IDs, idempotency keys, compare-and-swap/version checks, durable execution journals, deduplication and reconciliation after timeout. Concurrent/conflicting owners or automation changes -> block and seek review. Revocation checked at execution time; document limits once irreversible actions begin.

## Failure handling
Missing evidence -> qualify; unavailable identity/approval/audit -> no consequential action; unknown target -> no action; stale entity mapping -> no action; model mismatch -> new approval; lost executor response -> unknown and reconcile read-only; privacy restrictions -> redact; storage corruption -> preserve evidence and escalate.

## Acceptance tests
Schema validation and migration; provenance and timezone handling; redaction; stale evidence; forged guest/voice approvals; expired/replayed nonce; changed action hash; duplicate execution requests; network timeout and unknown outcome; concurrent approvals; executor compromise boundary; partial execution; audit immutability; revocation; five-minute conversational context separation; heating/EV/lighting safety. Pass requires zero unauthorised consequential actions.

## Formal requirement
**FR-OPT-CONTRACTS-001:** All PR #46 optimisation modules shall use versioned canonical evidence, model, recommendation, approval, incident, execution and audit records, with explicit state machines, strong owner authority, replay protection, idempotency, privacy and auditable outcome verification. **No model, conversation or document can bypass the independent approval/execution boundary.**

---
This is a PR conversation specification checkpoint, not a committed repository file. Explicit owner approval is required before any consequential action.



---

<a id="comment-6727758336"></a>

**Original checkpoint:** [PR #46 comment 6727758336](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758336)

# PR #46 — FR-OPT-E2E-TEST-001: End-to-End Household Optimisation Acceptance Scenario Catalogue

**Draft documentation only. No code, commits, merge, deployment, purchases or household changes authorised.**

## Purpose
Provide a traceable, risk-based set of future integration and acceptance scenarios connecting PR #46 requirements to reproducible evidence. This is a test specification, not a claim that tests have been executed.

## Test case contract
Each case must specify test ID, requirement IDs, risk, preconditions, model/data versions, synthetic fixtures, permitted environment, stimulus, expected advisory output, forbidden effects, required audit events, cleanup, evidence and pass/fail criteria. Use isolated mocks/simulations; never exercise live HA controls without separately authorised test scope.

## Core scenarios
**E2E-01 Heating:** Owner asks for earlier warmth; Declan analyses weather, schedule, one-hour override and uncertainty, proposes alternatives; must not change climate.home. Verify provenance and approval gate.
**E2E-02 EV:** Low SOC on plug-in does not auto-top-up. Declan may ask whether to charge to 50% or until midnight; no charging action without explicit scoped authorisation. Verify tariff assumptions and stop policy.
**E2E-03 Entity rename:** Missing legacy light entity and current light.living_room_wall_lights produce compatibility warning; no silent global rewrite or attempted unknown command.
**E2E-04 Tuya failure:** One command rejected; routine outcome reported partial/failed as evidenced, not success; no blind retry.
**E2E-05 Guest Mode:** Guest asks to modify owner policies, security settings or deploy code; decline and audit, while permitted guest-facing assistance remains available.
**E2E-06 Spoofed speaker:** Incorrectly recognised voice or speaker uncertainty cannot authorise high-risk actions.
**E2E-07 Context expiry:** Follow-up within five minutes retains conversation context; after five minutes requires fresh clarification. Persistent audit/consent records are not erased by context expiry.
**E2E-08 Model drift:** Heating predictor loses accuracy; monitoring flags evidence and uncertainty, proposes investigation, no automatic retraining or thermostat change.
**E2E-09 Conflicting models:** EV models disagree on departure readiness; Declan explains alternatives and declines false certainty.
**E2E-10 Counterfactual:** Simulated tariff/temperature change stays isolated; no live service call or schedule edit.
**E2E-11 Alert flood:** Correlated failures deduplicated; routine optimisation digest cap of three applies, urgent safety/security alerts use separately approved escalation.
**E2E-12 Resource pressure:** Optional model simulation constrained under Proxmox/HA/Frigate pressure; essential service protections hold.
**E2E-13 Cloud outage:** ElevenLabs or OpenAI STT outage triggers disclosed degradation/fallback where configured; no invented success.
**E2E-14 Music:** Spotify/Music Assistant queue status distinguishes actual playback from command acceptance; blacklist and positive feedback obey owner-approved scope.
**E2E-15 Data privacy:** Guest or injected web content cannot access occupancy, face recognition, credentials, financial records or privileged execution.
**E2E-16 Approval replay:** Expired, revoked, altered, duplicate or out-of-scope approval cannot execute.
**E2E-17 Execution timeout:** Unknown HA result remains unknown; read-only reconciliation, no automatic non-idempotent retry.
**E2E-18 Incident:** Security/model warning creates evidence-backed alert, not autonomous camera/lock/schedule changes.
**E2E-19 Backup:** Missing S3 verification marker flags backup assurance gap; no archive deletion, restore or marker fabrication.
**E2E-20 Trial:** Owner-approved experiment scope enforced; no automatic permanent adoption; compare outcomes with preregistered baseline.
**E2E-21 Explainability:** Trace source -> model version -> forecast -> recommendation -> owner decision -> execution evidence; missing link disclosed.
**E2E-22 Dual-owner conflict:** Conflicting instructions from Jaco and Edd deferred under agreed authority policy; no fabricated consensus.
**E2E-23 Monitoring outage:** Absence of alerts not treated as health; report coverage gap.
**E2E-24 Readiness gate:** Green documentation checklist cannot deploy, merge or operate devices.

## Evidence and coverage
Produce matrix by module and risk class, including positive, negative, adversarial, degraded and recovery cases. Record execution time, exact versions, environment isolation, logs/traces redacted, assertions, deviations, owner review and unresolved defects. Avoid using live personal data where synthetic fixtures suffice.

## Release gates
P0 tests: identity, authorisation, non-execution, privacy, physical safety, idempotency and audit. P1: accuracy, monitoring, context, resource budgets, compatibility. P2: controlled trials and outcome validation. Any safety-critical failure blocks relevant release eligibility pending independent review; a pass does not authorise release.

## Formal requirement
**FR-OPT-E2E-TEST-001:** PR #46 shall define reproducible, risk-based end-to-end tests with explicit forbidden effects and auditable evidence across conversation, household systems, optimisation models, safety and approvals. **Tests remain documentation-only until separately implemented and authorised.**

---
This is a PR conversation specification checkpoint, not a committed repository file. Explicit owner approval is required before any consequential action.



---

<a id="comment-6727758667"></a>

**Original checkpoint:** [PR #46 comment 6727758667](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758667)

# PR #46 — FR-OPT-ROADMAP-001: Risk-Based Implementation Sequencing and Dependency Roadmap

**Draft documentation only. No code, commits, merge, deployment, purchases or household changes authorised.**

## Purpose
Provide an owner-reviewable implementation order for PR #46 without starting implementation, modifying the repository or implying approval to deploy.

## Workstream 0 — Baseline reconciliation
Confirm repository/runtime state, actual conversation/STT/TTS identifiers, bridge installation, legacy Jarvis aliases, existing HA entity IDs, routine outcome contract and quiet-hours rules. Map each requirement to owner, source comment and acceptance tests. Preserve existing identifiers until migration design is approved.

## Workstream 1 — Safety and contracts (P0)
Design canonical records and independent owner authorisation/execution boundary; permissions, Guest Mode, high-risk identity assurance, audit, idempotency, approval expiry/revocation, safe failure modes and negative tests. No autonomous household optimisation execution. Gate: owner reviews architecture and threat model.

## Workstream 2 — Observability and evidence (P1)
Establish source inventory, provenance, quality/freshness, privacy/retention, read-only telemetry and diagnostic correlation; resource budgets for Proxmox/Frigate/HA. Gate: evidence integrity and non-intrusive collection verified in isolated tests.

## Workstream 3 — Reliable conversation and core routines (P1)
Prioritise voice command correctness, five-minute context, phrase matching, speaker uncertainty, routine outcome reporting, entity mapping and failure isolation. Preserve manual controls and existing heating/EV safeguards. Gate: E2E scenarios for current household use cases.

## Workstream 4 — Advisory models (P1)
Introduce model registry, offline validation, read-only monitoring, drift alerts, explainability and trust classification. Predictions and recommendations remain advisory; no self-promotion or automatic changes. Gate: independent accuracy, privacy and non-execution tests.

## Workstream 5 — Household planning and simulations (P2)
Implement only after separate approval: goal tracking, scenario comparisons, digital twin, change impact, alternatives, cost/benefit forecasts and counterfactuals. Gate: fidelity, uncertainty and dependency coverage.

## Workstream 6 — Controlled experiments (P2)
Design preregistered trials with exact owner consent, safety limits, baselines, rollback plans and measured outcomes. A successful trial does not permit permanent change. Gate: trial review and separate approval.

## Workstream 7 — Advanced optimisation (P3)
Long-term goals, portfolio strategy, research, institutional memory, continuous learning and lifecycle management after foundational governance and quality have been demonstrated. Gate: sustained benefits and risk reviews.

## Dependency and prioritisation rules
No model advice before evidence quality; no consequential recommendation before risk/uncertainty disclosure; no execution pathway before independently tested authorisation; no production trial before isolated simulation and owner approval; no deployment before readiness and rollback review. Protect essential services over optional model workloads.

## Deliverables per workstream
Requirement IDs and exclusions, architecture/design, data contracts, threat/privacy review, tests and evidence, owner decisions, migration/rollback, operational runbook, release proposal. Use statuses: draft, owner-reviewed, accepted for design, designed, implemented, tested, validated, release-approved, deployed, verified. Do not skip stages.

## Cost and capacity
Estimate engineering effort, cloud API costs, local compute/GPU/RAM, storage and support burden with assumptions. Do not fabricate estimates without measurement. Require explicit approval for new subscriptions, hardware or service spending.

## Change and governance
Use small reversible changes, explicit target environments, peer/independent review proportionate to risk, audit and rollback readiness. This roadmap does not grant permission to create branches, commit code, merge, restart HA or deploy.

## Acceptance
Roadmap must show critical dependencies, P0 blockers, owner decisions, measurable acceptance, realistic capacity constraints and separate approval at each consequential step. Review when household priorities, infrastructure or model evidence changes.

## Formal requirement
**FR-OPT-ROADMAP-001:** PR #46 shall maintain a risk-based, dependency-aware, owner-approved implementation roadmap with explicit evidence and release gates, prioritising permissions, reliability and observability before advanced autonomous intelligence. **Roadmap acceptance is not implementation or deployment approval.**

---
This is a PR conversation specification checkpoint, not a committed repository file. Explicit owner approval is required before any consequential action.



---

<a id="comment-6727777320"></a>

**Original checkpoint:** [PR #46 comment 6727777320](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727777320)

# PR #46 — FR-OPT-OWNER-DECISIONS-001: Consolidated Owner Decision Register

**Draft documentation only. This records open decisions, not owner consent or an approval to change systems.** Source: PR #46 description and existing conversation checkpoints; no live HA inspection claimed.

## Decision status and process
All entries below are **OPEN / NOT YET APPROVED** unless the underlying household preference is already explicitly recorded; even then, implementation details require review. Each decision must eventually record owner, exact choice, rationale, affected FRs, evidence, date, expiry/review trigger, dissent and superseding revision. Guest Mode cannot resolve owner decisions. Lack of response is not approval.

| ID | Decision / question | Options or required evidence | Dependency |
|---|---|---|---|
| OD-01 | Confirm deployed Declan conversation, STT, TTS and satellite IDs | Read-only inventory against HA and repo; record exact versions | Required for compatibility and testing |
| OD-02 | Confirm separate voice bridge installation and responsibility | Installed/unused/retired; identify interface owner | Required for architecture and migration |
| OD-03 | Legacy spoken Jarvis aliases | Retain temporarily / remove after transition / retain permanently | Owner choice; avoid breaking voice commands |
| OD-04 | Routine outcome contract | Requested, accepted, executed, verified, partial, failed, unknown | Define once across scripts, UI and voice |
| OD-05 | Quiet hours and alert escalation | Owner-approved hours, delivery devices, urgent exceptions, fallback | Routine three-per-week digest remains |
| OD-06 | High-risk approval authentication | Explicit approved mechanism and risk tiers; voice identity alone insufficient | Security design blocker |
| OD-07 | Multiple-owner conflict and authority | Joint approval or scoped per-owner authority; unresolved means defer | Do not infer consensus |
| OD-08 | Model advisory eligibility suspension | Restrict advice vs any live service/model change | No autonomous restart/deploy |
| OD-09 | Canonical record schemas and retention | Approve IDs, versions, sensitive fields, deletion/audit constraints | Contracts are draft only |
| OD-10 | Resource budgets and isolated testing | Proxmox/HA/Frigate protections and simulation quotas | No production fault injection |
| OD-11 | Prioritised implementation slices | Reliability/permissions first versus advanced optimisation | No implementation authorised by prioritisation |
| OD-12 | Draft acceptance ownership | Which FRs accepted for design versus exploratory | Acceptance does not authorise deployment |
| OD-13 | Existing heating override details | One-hour temporary override and safe schedule resumption | Confirm entity and exact routine semantics |
| OD-14 | EV charging approval semantics | On plug-in ask top to 50% or charge until midnight; no automatic <50% top-up | Confirm stopping, midnight and schedule interaction |
| OD-15 | Guest Mode handover and persona | Welcome, guest assistance, owner return sass, restricted permissions | Never let personality override safety |
| OD-16 | Music feedback authority | Household-wide blacklist, positive weighting, source of truth and reversals | No unverified playback or silent policy changes |
| OD-17 | Owner review of historical draft completeness | Reconcile detailed conversation drafts with PR comment summaries and repository files | Do not claim full transfer until verified |

## Pre-existing agreed constraints, not open for silent reinterpretation
- Conversation context lasts **five minutes after the last interaction**, distinct from audit retention.
- Routine optimisation digest contains **at most three recommendations per week** across modules; urgent alerts follow separate owner-approved policy.
- Owner approval is explicit, scope/version/action-bound; research, trial, purchase, deployment, policy and live household execution are separate.
- Guest Mode and voice identification alone never grant owner authority.
- No automatic EV top-up solely because SOC is below 50%; existing owner choice and charge limits are to be preserved.
- One-hour temporary heating override requirement remains; confirm operational details before design.
- No implementation, merge, deployment, purchases, backup operations, service restarts or live HA modifications under this documentation phase.

## Suggested review order
**Gate A, safety/compatibility:** OD-01–08, OD-13–14.
**Gate B, contracts and privacy:** OD-09–10.
**Gate C, household experience:** OD-05, OD-15–16.
**Gate D, scope and delivery:** OD-11–12, OD-17.

## Decision acceptance
A decision is resolved only with an explicit owner-approved option, rationale, scope, affected requirements and tests, and a recorded decision version. If evidence is unavailable or owners disagree, mark **deferred/disputed**, never silently select a default.

## Formal requirement
**FR-OPT-OWNER-DECISIONS-001:** Maintain a traceable, owner-controlled register of unresolved PR #46 decisions, preserving options, dependencies, authority, history and explicit resolution before relevant design/release gates. **This comment does not resolve any decision or authorise implementation.**



---

<a id="comment-6727781069"></a>

**Original checkpoint:** [PR #46 comment 6727781069](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727781069)

# PR #46 — FR-OPT-MASTER-INDEX-001: Master Requirements Index and Coverage Reconciliation

**Documentation-only index.** This is an index of PR #46's existing conversation comments, **not a claim that all detailed requirements have been committed to the repository**.

## Source and completeness assessment
Reviewed PR #46 description and existing PR conversation comments through the owner decision register. The PR description identifies `docs/functional-requirements.md`, `docs/legacy-jarvis-reference-audit.md` and persona/branding documentation. The additional specifications have been posted as PR discussion comments. **A line-by-line comparison with the repository's actual Markdown contents and all historical conversation drafts has not yet been completed.**

**Conclusion: coverage is broad, but full requirement completeness is NOT VERIFIED.** In particular, early long-form conversation drafts are represented by grouped summaries in the PR, so exact examples, thresholds, acceptance criteria and wording may not all be present in the branch.

## Master index
| Module(s) or subject | Source comment | Coverage qualification |
|---|---|---|
| Conversation, personality, Guest Mode, five-minute context | [#6727257835](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727257835) | Checkpoint summary; detailed chat drafts not verified in repo |
| Household goals, milestones, setbacks, reviews, dependencies, coordinated optimisation | [#6727257835](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727257835) | Checkpoint summary; detailed chat drafts not verified in repo |
| Continuous learning, knowledge, observability, safety, testing | [#6727257835](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727257835) | Checkpoint summary; detailed chat drafts not verified in repo |
| FR-OPT-SCENARIO-001; RESEARCH-001; STRATEGY-001; BENEFITS-001; PORTFOLIO-001 | [#6727353857](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727353857) | Grouped checkpoint; detail in conversation |
| FR-OPT-ASSURANCE-001; FR-OPT-RISK-001 | [#6727398209](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727398209) | Grouped checkpoint |
| FR-OPT-INCIDENT-001; FR-OPT-CONTINUITY-001; FR-OPT-TWIN-001 | [#6727444983](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727444983) | Grouped checkpoint |
| FR-OPT-VALIDATION-001 | [#6727463290](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727463290) | Individual specification comment |
| FR-OPT-MODEL-GOV-001 | [#6727483039](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727483039) | Individual specification comment |
| FR-OPT-MONITOR-001 | [#6727547284](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727547284) | Individual specification comment |
| FR-OPT-EXPLAIN-001 | [#6727561377](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727561377) | Individual specification comment; expanded conversation draft |
| FR-OPT-TRUST-001 | [#6727596152](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596152) | Individual specification comment |
| FR-OPT-DECISION-001 | [#6727596493](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596493) | Individual specification comment |
| FR-OPT-DATA-LIFECYCLE-001 | [#6727596846](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596846) | Individual specification comment |
| FR-OPT-HUMAN-OVERSIGHT-001 | [#6727597202](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597202) | Individual specification comment |
| FR-OPT-OPERATIONS-001 | [#6727597455](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597455) | Individual specification comment |
| FR-OPT-READINESS-GATE-001 | [#6727597853](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597853) | Individual specification comment |
| FR-OPT-CHANGE-IMPACT-001 | [#6727714604](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714604) | Individual specification comment |
| FR-OPT-EXPERIMENT-001 | [#6727714934](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714934) | Individual specification comment |
| FR-OPT-REVIEW-001 | [#6727715316](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727715316) | Individual specification comment |
| FR-OPT-CONSOLIDATION-001 | [#6727739848](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727739848) | Cross-cutting consolidation and gap register |
| FR-OPT-CONTRACTS-001 | [#6727758036](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758036) | Canonical proposed contracts and approval states |
| FR-OPT-E2E-TEST-001 | [#6727758336](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758336) | 24 future test scenarios |
| FR-OPT-ROADMAP-001 | [#6727758667](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758667) | Risk-based implementation sequencing |
| FR-OPT-OWNER-DECISIONS-001 | [#6727777320](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727777320) | 17 unresolved owner decisions |

## Repository document mapping required
1. `docs/functional-requirements.md`: compare every section against this index; mark source-backed existing baseline, new draft, duplicate, unresolved decision and missing acceptance criteria.
2. `docs/legacy-jarvis-reference-audit.md`: reconcile all legacy references with actual installed identifiers; do not rename entity IDs, unique IDs, storage keys or runtime domains automatically.
3. `README.md`, `docs/guest-persona.md`, `docs/branding-declan.md`, historical migration guide: confirm current Guest Mode-only persona and automatic handover wording, without erasing historical migration context.
4. Add future versioned spec files only after explicit documentation-edit approval. GitHub comments are not substitutes for committed docs or independent validation.

## Coverage reconciliation method
For every requirement: unique FR ID; exact statement; source conversation or PR comment; target repo file/section; owner; type (functional, safety, privacy, non-functional, acceptance); status; duplicate/contradiction links; test IDs; explicit decision dependencies. Status options: **captured in PR comment**, **confirmed in repository file**, **missing from repository**, **partially represented**, **conflicting**, **needs owner review**, **accepted for design**. Do not mark as confirmed without file-level verification.

## Potentially under-transferred detail to verify
- Natural conversation context expiry, correction/clarification, guest welcome/handover and owner return sass.
- Detailed household goal progress, milestones, setbacks, dependencies, reviews and coordinated heating/EV/lighting scenarios.
- Safe optimisation trials, recommendation prioritisation, model calibration, long-term monitoring and lifecycle.
- Proactive intelligence, knowledge management, continuous learning, privacy, observability, testing and release safety.
- Exact EV charge-to-50%-or-midnight choice and one-hour heating override.
- Voice phrase catalogue, entity rename compatibility, Tuya partial failures and routine outcome reporting.
- Spotify/Music Assistant category discovery, household-wide blacklist, positive feedback, playback verification and voice fallback.
- Legacy identifier migration and bridge integration decisions from the original PR description.
- Any tables, examples, numerical criteria or detailed acceptance cases present only in the drafting conversations.

## Canonical responsibility and duplication controls
Owner approval: FR-OPT-HUMAN-OVERSIGHT-001; record schemas: FR-OPT-CONTRACTS-001; data lineage: FR-OPT-DATA-LIFECYCLE-001; model lifecycle: FR-OPT-MODEL-GOV-001; validation: FR-OPT-VALIDATION-001; monitoring: FR-OPT-MONITOR-001; explanations: FR-OPT-EXPLAIN-001; recommendation trust: FR-OPT-TRUST-001; choices: FR-OPT-DECISION-001; acceptance: FR-OPT-E2E-TEST-001 and FR-OPT-READINESS-GATE-001; open decisions: FR-OPT-OWNER-DECISIONS-001. Domain-specific requirements should cross-reference these contracts rather than create conflicting implementations.

## Completion gate
Do not declare the consolidated specification complete until: (a) all source drafts are enumerated; (b) every requirement is mapped to an actual versioned repository section; (c) duplicates/conflicts are reconciled; (d) owner decisions and acceptance tests are linked; (e) safety/approval constraints are independently reviewed; and (f) the owner accepts the consolidated documentation. Implementation and release are later, separate gates.

## Formal requirement
**FR-OPT-MASTER-INDEX-001:** Maintain a source-linked master index and verifiable repository coverage matrix for all PR #46 requirements, preserving unresolved gaps and owner decisions. **Do not equate PR comments, drafted specifications, accepted designs, implemented code or deployed functionality. No code, merge or deployment is authorised by this index.**
