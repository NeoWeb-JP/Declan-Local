# Household optimisation functional specifications

> **PR #46 draft, documentation only. Not approved for implementation, merge or deployment.**
>
> This file preserves the complete text of the cited PR conversation checkpoints, including their original caveats. Early grouped checkpoints are summaries of earlier conversations, **not verified verbatim transfers of every historical discussion**. Later reviews and decision corrections take precedence where they explicitly identify an earlier misclassification. No household action is authorised by this documentation.
>
> Existing baseline: [functional-requirements.md](functional-requirements.md). This appendix does not replace it.

## Source contents

- [GitHub comment 6727257835](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727257835) — PR #46 functional specification checkpoint — 8 November 2026
- [GitHub comment 6727353857](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727353857) — PR #46 documentation checkpoint: Household Optimisation (8 November 2026)
- [GitHub comment 6727398209](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727398209) — PR #46 documentation checkpoint: Policy Assurance and Predictive Risk Intelligence (8 November 2026)
- [GitHub comment 6727444983](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727444983) — PR #46 functional specifications checkpoint: Incident Response, Service Continuity, Digital Twin
- [GitHub comment 6727463290](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727463290) — PR #46 — FR-OPT-VALIDATION-001: Household Optimisation Model Validation and Simulation Accuracy Assurance
- [GitHub comment 6727483039](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727483039) — PR #46 — FR-OPT-MODEL-GOV-001: Household Optimisation Model Governance and Controlled Promotion
- [GitHub comment 6727547284](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727547284) — PR #46 — FR-OPT-MONITOR-001: Household Optimisation Model Performance Monitoring and Automated Quality Alerts
- [GitHub comment 6727561377](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727561377) — PR #46 — FR-OPT-EXPLAIN-001: Household Optimisation Model Explainability, Transparency and Decision Traceability
- [GitHub comment 6727596152](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596152) — PR #46 documentation specification — FR-OPT-TRUST-001
- [GitHub comment 6727596493](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596493) — PR #46 documentation specification — FR-OPT-DECISION-001
- [GitHub comment 6727596846](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596846) — PR #46 documentation specification — FR-OPT-DATA-LIFECYCLE-001
- [GitHub comment 6727597202](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597202) — PR #46 documentation specification — FR-OPT-HUMAN-OVERSIGHT-001
- [GitHub comment 6727597455](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597455) — PR #46 documentation specification — FR-OPT-OPERATIONS-001
- [GitHub comment 6727597853](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597853) — PR #46 documentation specification — FR-OPT-READINESS-GATE-001
- [GitHub comment 6727714604](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714604) — PR #46 — FR-OPT-CHANGE-IMPACT-001: Household Optimisation Change Impact Analysis and Dependency Safety
- [GitHub comment 6727714934](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714934) — PR #46 — FR-OPT-EXPERIMENT-001: Household Optimisation Experimental Design and Outcome Verification
- [GitHub comment 6727715316](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727715316) — PR #46 — FR-OPT-REVIEW-001: Household Optimisation Periodic Governance Review and Specification Closure

---


---

<a id="comment-6727257835"></a>

**Original checkpoint:** [PR #46 comment 6727257835](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727257835)

## PR #46 functional specification checkpoint — 8 November 2026

**Status:** Documentation-only planning record. These are draft requirements discussed with the owner, not implemented features or approved production changes. No merge, deployment, Home Assistant changes or automatic household actions are authorised.

### Functional specification topics covered

**Conversation and household interaction**
- Natural multi-turn conversations, five-minute context retention after the last interaction, context reset, clarification and corrections.
- Declan personality and Guest Mode boundaries; guest welcome/handover and owner return behaviour, with safety and governance independent of personality.
- Household context, user-specific and shared preferences, permission boundaries and safe confirmations.

**Household goals and coordinated optimisation**
- Household goal progress reports, milestones and recognition, setbacks and recovery, periodic reviews and recalibration.
- Goal dependency and conflict analysis, coordinated heating/EV/lighting optimisation planning, measurable outcomes, uncertainty and read-only previews.
- Safe optimisation trials, learning from trials, recommendation prioritisation, impact forecasting, calibration, long-term monitoring and lifecycle management.

**Governance and evidence**
- Explicit, scoped owner approvals; decision history and accountability; transparency and explainability.
- Data quality, provenance, freshness, uncertainty, cross-source checks and evidence reliability.
- Resilience and graceful degradation under integration outages, unavailable sensors and partial failures.

**Security and release management**
- Security and trust boundaries: least privilege, integration trust, tamper detection, credential protection, immutable proposal-bound approval, command validation, audit integrity, threat modelling and safe incident handling.
- Testing, validation and safe releases: isolated simulations, synthetic/historical replay, automated regression, governance and safety tests, staged release gates, rollback readiness, release evidence, separate deployment approval and post-release verification.

**Operations and improvement**
- Observability and operational diagnostics: end-to-end tracing of voice and HA operations, structured logs, latency metrics, dependency health, error correlation, root-cause confidence, privacy, dashboard and approval-controlled remediation.
- Continuous improvement and controlled learning: verified feedback, evidence eligibility, model drift, offline candidate evaluation, regression protection, separate owner preferences, approval-gated promotion and no autonomous deployment.
- Knowledge management and institutional memory: structured/versioned knowledge, provenance, effective dates, contradiction resolution, historical lessons, expiry/review, owner corrections, permission-aware retrieval, privacy and integrity.

### Cross-cutting requirements agreed for this planning stream
1. **No automatic household changes:** No unapproved modification of heating, EV charging, lighting, security, automations, entities, configurations, policies or schedules.
2. **Independent authority:** AI-generated suggestions and voice identity alone are not authorisation. Approvals bind to exact scope/version; release approval does not grant permission for household changes.
3. **Verified outcomes:** Distinguish requested, accepted, executed, verified, failed and unknown states. Do not invent evidence, root causes or savings.
4. **Safety and privacy:** Fail safely; restrict untrusted evidence; protect credentials and personal household data; preserve auditable provenance.
5. **Documentation only:** No implementation, merge, deployment, runtime testing or production modifications under this checkpoint.

### Current stopping point and next planned section
**Last drafted:** Household Optimisation Knowledge Management and Institutional Memory (structured knowledge, provenance, temporal validity, contradictions, lessons, expiry, corrections, privacy, retrieval reliability).

**Next proposed:** Household Optimisation Proactive Intelligence and Opportunity Detection, covering continuous read-only analysis, opportunity scoring, novelty detection, historical context, measurable benefits, confidence, notification limits, owner preferences, duplicate suppression and approval-controlled proposals.

### Scope caveat
This checkpoint is a **summary/index of the conversation's draft specifications**, not a verbatim replacement for their detailed acceptance criteria and tables. The detailed drafts remain in the planning conversation and should be consolidated into versioned documentation on this PR before final review. No statement here asserts that the PR branch already contains these sections.

**Do not merge or deploy on the basis of this checkpoint.**



---

<a id="comment-6727353857"></a>

**Original checkpoint:** [PR #46 comment 6727353857](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727353857)

## PR #46 documentation checkpoint: Household Optimisation (8 November 2026)

**Status: Draft functional requirements only. This comment records our latest specification work for continuity. It does not approve implementation, merge, deployment, purchases or Home Assistant changes.**

### Newly documented modules

1. **FR-OPT-SCENARIO-001 — Decision Support and What-If Scenario Analysis**
   - Versioned hypothetical scenarios, immutable baselines, interactive multi-turn modifications and comparisons, sensitivity analysis, cost/comfort/reliability trade-offs, forecast uncertainty and historical replay.
   - Heating, EV charging, lighting and coordinated scenarios; validate feasibility, hard safety constraints, model assumptions and provenance. Persist scenario versions and flag stale results.
   - Simulations are isolated and read-only. Scenario selection or saving is never approval to execute.

2. **FR-OPT-RESEARCH-001 — Autonomous Research and Evidence Gathering**
   - Authorised owner, scheduled or evidence-triggered research with bounded scope, request/time/cost budgets and explicit stopping rules.
   - Source authority, authenticity, publication/effective dates, version applicability, independent corroboration, provenance, contradiction handling, confidence and household relevance.
   - Privacy minimisation, external-content prompt-injection isolation, controlled retention and source-traceable reports. No automatic firmware/software updates, purchases or device commands.

3. **FR-OPT-STRATEGY-001 — Strategic Planning and Long-Term Roadmaps**
   - Multi-month/annual horizons, versioned roadmaps, owner-defined goals and budgets, phased initiatives, dependencies, resource capacity, risks, alternatives and milestones.
   - Investment/operating-cost modelling, payback and uncertainty; periodic monthly/quarterly/annual review and owner-approved recalibration.
   - Roadmap/planning budget approval never authorises spending or execution.

4. **FR-OPT-BENEFITS-001 — Benefits Realisation and ROI Verification**
   - Immutable pre-change baselines and forecasts, implementation evidence, post-change measurement, verified expenditure, forecast-versus-actual reporting.
   - Weather/occupancy/tariff normalisation, attribution and confounding, avoidance of double-counted savings, financial ROI/payback, non-financial comfort/reliability outcomes, negative effects and sustainability.
   - Evidence strength, reproducibility, owner corrections and audit history. No automatic rollback or household action.

5. **FR-OPT-PORTFOLIO-001 — Portfolio Management and Investment Governance**
   - Structured initiative register, duplicate suppression, selection, transparent priority weights, aggregate budget allocation, competing investments, dependency cycles, shared resource constraints, correlated risks and portfolio scenarios.
   - Portfolio-wide forecast and realised benefit tracking, no double-counting, controlled rebalancing proposals, version-specific owner decisions and financial governance.
   - Planning allocation is not spending authority. Separate explicit approvals for purchases, live trials, configuration, deployments and permanent adoption.

### Cross-cutting acceptance requirements
- **Read-only by default:** analysis, research, simulations, reporting and planning cannot issue live Home Assistant commands, change schedules, charge EVs, alter configurations, deploy software, switch suppliers or commit funds.
- **Approval separation:** research approval, planning approval, budget allocation, purchasing, trials, deployment, configuration change and permanent adoption are distinct; permissions bind to the exact scope/version. Guests cannot approve.
- **Evidence and integrity:** provenance, source freshness, data-quality gates, uncertainty, immutable/versioned baselines, recorded corrections, historic decisions, reproducible financial calculations and no invented measurements.
- **Owner control:** preserve Jaco/Edd preferences and disagreements; no assumed consent, no autonomous rebalancing, no automatic action following a successful forecast.
- **Notification governance:** routine recommendations share the existing maximum of three per weekly optimisation digest; safety/security escalation follows separate approved policies.
- **Failure safety:** stale tariffs, missing baselines, unverified outcomes, approval-service failures, external prompt injection and resource exhaustion fail closed for consequential actions.

### Acceptance and release status
All five modules remain **proposed documentation**, not implemented or tested in production. Illustrative figures and dashboard examples in the conversation are not actual household readings or financial quotes. The full detailed acceptance criteria, failure matrices, schemas and worked examples remain in the drafting conversation and should be transferred into dedicated documentation files during a separately authorised documentation-edit pass.

### Next module proposed
**Household Optimisation Policy Compliance and Continuous Assurance:** continuous read-only policy checks, approval compliance, spending boundaries, safety/privacy constraints, configuration drift, audit evidence, exceptions, owner notifications, independent assurance and approval-controlled remediation proposals.

**No merge or deployment authorised.**



---

<a id="comment-6727398209"></a>

**Original checkpoint:** [PR #46 comment 6727398209](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727398209)

## PR #46 documentation checkpoint: Policy Assurance and Predictive Risk Intelligence (8 November 2026)

**Documentation-only draft checkpoint. No implementation, commits, merge, deployment, spending or household changes authorised.**

### FR-OPT-ASSURANCE-001 — Household Optimisation Policy Compliance and Continuous Assurance
- Independent, least-privilege, read-only assurance architecture; structured, versioned policy register covering safety, privacy, financial, security, operational, governance, notification and data-quality rules.
- Evidence-based continuous/event-driven compliance checks; states include compliant, violation, potential violation, indeterminate, exception active, not applicable, evaluation failed and policy disputed. Missing evidence never establishes compliance.
- Verify approvals against exact scope, version, authority and expiry. Separate research, scenario, planning, budget, purchasing, trial, configuration, deployment and adoption permissions. Guest Mode grants no owner authority.
- Check heating override and EV charging safeguards, financial limits, privacy permissions, entity renames, configuration/behavioural drift, expired exceptions and assurance-engine integrity. Distinguish observations from root-cause inferences.
- Findings require provenance, severity, confidence, independent corroboration where feasible, owner-visible evidence, deduplicated notifications, controlled exceptions, audit trail and approval-controlled remediation proposals.
- Fail closed for consequential actions; assurance cannot grant its own permissions or execute a proposed fix.

### FR-OPT-RISK-001 — Household Optimisation Risk Forecasting and Early Warning Intelligence
- Read-only predictive risk indicators, trends, anomalies, change-point and seasonal baseline comparisons; explicit forecast horizons and evidence freshness.
- Assess safety, heating readiness, EV charging readiness, Home Assistant/integration reliability, voice/media, homelab resources, security, financial exposure, household optimisation and data quality.
- Versioned risk records capture affected systems, historical evidence, indicators, likelihood, impact, severity, confidence, dependencies, time horizon, uncertainty, mitigation proposals and owner decisions.
- Propagation analysis includes common-cause failures and cross-system dependencies; calibrated probabilities only where supported, otherwise qualitative likelihood. Separate event probability, impact, confidence and urgency.
- Forecast-versus-outcome calibration, false-positive and missed-event review, notification thresholds, deduplication, risk acceptance, residual risk, scenario-based mitigation comparisons and reproducible audit history.
- Routine optimisation recommendations share the existing maximum three per weekly digest; separately governed urgent safety/security alerts may escalate.
- No risk prediction or warning authorises device commands, EV charging, heating changes, software deployments, financial actions, service restarts or policy changes.

### Common governance and release boundary
These are proposed functional requirements in the drafting conversation, not production features or verified current household findings. Illustrative dashboard values, examples and scenarios are hypothetical. All live interventions require **separate, explicit, version/scope-bound owner approval**; planning or risk acceptance is not execution approval.

### Next draft module
**Household Optimisation Incident Prevention and Coordinated Response Planning:** incident scenarios, preparedness, severity/escalation, dependency-aware response playbooks, owner communications, recovery choices, evidence preservation, post-incident learning and no automatic household intervention.

This PR comment is a checkpoint summary, not the full detailed specification files. **No merge or deployment authorised.**



---

<a id="comment-6727444983"></a>

**Original checkpoint:** [PR #46 comment 6727444983](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727444983)

# PR #46 functional specifications checkpoint: Incident Response, Service Continuity, Digital Twin
**Status:** Documentation-only draft. **No implementation, commit, merge, deployment, spending or household modification authorised.**

## FR-OPT-INCIDENT-001 — Household Optimisation Incident Prevention and Coordinated Response Planning
**Objective:** Evidence-based incident prevention, detection, triage, impact assessment, dependency-aware response planning, owner communication, recovery verification and post-incident learning.

**Requirements:**
1. Versioned incident scenario catalogue and preparedness playbooks for Home Assistant, Proxmox, network, heating, EV charging, lighting, cameras, voice/media, backups, security and financial disruptions.
2. Structured incident records: identity, timestamps, detection source, severity, confirmed/suspected impacts, dependencies, evidence provenance, root-cause confidence, approvals, response history and recovery verification.
3. Correlate common-cause incidents without concealing independent failures. Classify anomalies, suspected and confirmed incidents separately.
4. Assess household safety, comfort, security, accessibility, reliability, privacy and financial impact. Prioritise immediate safety and independently verified dependencies.
5. Versioned playbooks must separate read-only inspection from state-changing diagnostics and interventions; include prerequisites, alternatives, risks, stop conditions, rollback and success checks.
6. Owner-specific, scope/version-bound approval is required for restarts, configuration edits, restores, deployments, security changes and any live intervention. Incident urgency does not create authority.
7. Backup existence is not proof of recoverability. Record RTO/RPO, partial recovery, verification gaps, delivery uncertainty and evidence-backed incident timelines.
8. Protect logs, credentials, personal information and Guest Mode boundaries; preserve audit evidence and uncertainty. Support post-incident reviews, recurrence analysis and controlled learning, with no autonomous production changes.
9. Test correlated outages, conflicting evidence, incomplete backups, communication failure, permission bypass attempts, partial restoration and Declan's own unavailability.

## FR-OPT-CONTINUITY-001 — Household Optimisation Service Continuity and Graceful Degradation Planning
**Objective:** Preserve essential household functionality through verified manual fallbacks, offline operation, dependency isolation, degraded-mode communication and owner-approved recovery plans.

**Requirements:**
1. Owner-approved service criticality register (life safety, essential, important, convenience, optimisation); independently functioning safety mechanisms must not rely on Declan.
2. Versioned service records with dependencies, verified/conditional/unknown offline support, physical fallbacks, recovery prerequisites, owner, RTO/RPO, testing and review dates.
3. Dependency mapping across mains power, local network, internet, Proxmox, Home Assistant, Hive, Pod Point, cameras, Frigate, voice and media. Distinguish service criticality from feasible recovery order.
4. Explicit normal, minor/partial/major/critical degradation, recovery, verification pending and unknown states. Never equate online status with functional recovery.
5. Document and independently verify manual heating, EV, lighting and security fallbacks; distinguish lost telemetry from lost physical capability. No automatic EV top-up based solely on SOC below 50%.
6. Support offline/Internet/HA/Proxmox outage tabletop scenarios and dependency-aware recovery proposals. Require separate approval for live drills, restarts, restoration or configuration changes.
7. Verify restoration using actual functional outcomes and dependencies. Preserve communication alternatives when Declan or HA is unavailable; do not assert unverified alert delivery.
8. Measure documented versus tested continuity coverage, recovery outcomes and evidence gaps; version plans and protect recovery credentials and household privacy.
9. Test offline operation, partial restoration, fallback validity, failed notifications, outdated recovery plans, approval-service outages and no automatic intervention.

## FR-OPT-TWIN-001 — Household Optimisation Digital Twin and Operational Simulation
**Objective:** Maintain an evidence-based, versioned digital representation of relevant household devices, services, dependencies, schedules and operating conditions, allowing hypothetical simulation without affecting production.

**Requirements:**
1. Read-only source observations and isolated simulation state. No unrestricted Home Assistant, Proxmox, charging, financial, security or deployment execution credentials.
2. Model devices, rooms, heating, EV charging, lighting, energy/tariffs, Home Assistant automations, homelab/voice/security dependencies and approved household goals with purpose-limited data.
3. Per-component fidelity: verified, calibrated, estimated, conceptual or unsupported; preserve source provenance, version, exclusions, assumptions and review date.
4. Versioned scenario record: objective, immutable baseline, model version, hypothetical changes, time horizon, constraints, inputs, outputs, uncertainty, alternatives and owner decisions.
5. Heating scenarios: thermal response, outdoor temperature, warm-up, schedules, energy and comfort. EV scenarios: SOC, charging power/efficiency, windows, tariff and departure readiness. Lighting scenarios: power, duration, occupancy/daylight and essential safety constraints.
6. Simulate infrastructure outages, dependency propagation, stale sensors, network/cloud failures and automation conflicts entirely inside the model; no live fault injection.
7. Cross-system analysis must identify shared resources, safety constraints, trade-offs and double-counted benefits. Preserve baselines and distinguish simulated savings from realised savings.
8. Historical replay without future-information leakage, calibration, bias/error analysis, model drift on entity/config/tariff changes and explicit uncertainty/sensitivity ranges. Stale models must be flagged.
9. Conversational scenario refinement with approved five-minute conversation context; persistent scenarios are separately governed. Protect occupancy, privacy, Guest Mode, resource budgets and essential services.
10. Reports explain baseline, model fidelity, assumptions, predicted outcomes, alternatives, risks, evidence gaps and approvals. A scenario cannot self-promote to a live trial or deployment.
11. Test model fidelity, version reproducibility, heating/EV/lighting, failure propagation, drift, privacy, resource limits, and hard isolation proving simulated commands cannot reach live execution.

## Shared approval and release boundary
All three requirements are **draft specifications**, not production functionality or verified household observations. The drafting conversation contains further examples, acceptance criteria, dashboard concepts and failure matrices. All financial figures, device outcomes and sample incidents are illustrative. **Read-only by default; explicit owner approval for every consequential action; Guest Mode cannot approve.** Routine optimisation recommendations remain under the shared maximum of three per weekly digest, with separately governed safety/security escalation.

**This comment records specifications only. Do not implement, merge or deploy.**



---

<a id="comment-6727463290"></a>

**Original checkpoint:** [PR #46 comment 6727463290](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727463290)

# PR #46 — FR-OPT-VALIDATION-001: Household Optimisation Model Validation and Simulation Accuracy Assurance

**Status:** Draft functional specification; documentation only. **No code, merge, deployment, spending, device changes or household intervention authorised.**

## 1. Purpose and scope
Declan shall independently establish whether each optimisation model, risk forecast and digital twin simulation is technically correct, representative of the household, empirically accurate, and fit for its **specific intended decision**. Simulation completion is not proof of accuracy. Scope includes heating, EV charging, lighting, energy/cost, homelab, voice, operational risk, digital twin, financial and multi-goal optimisation.

## 2. Validation architecture and records
Eight stages: model/use-case registration; independent evidence assessment; technical verification; historical backtesting; accuracy/calibration; independent suitability decision; owner reporting/approval; ongoing drift surveillance.

Maintain immutable, versioned records containing validation ID, model ID/version, use case, operating scope, evidence/dataset versions, historical evaluation period, methodology, preregistered thresholds, metrics, findings, confidence, limitations, reviewer independence, decision, expiry and audit references.

Distinguish **verification** (implementation correctly follows specification) from **validation** (predictions represent real household behaviour for the use case). A model may pass one and fail the other.

## 3. Evidence and independence
Evaluate provenance, sensor accuracy, timestamps, completeness, sampling, representativeness, configuration consistency, duplicates, missingness, corrections and privacy. Evidence classes: verified, supported, provisional, unreliable, unavailable. Insufficient or unreliable evidence cannot justify high confidence.

Where possible use independent measurements, holdout observations, alternative methods, independent calculations and verified outcomes. Re-running the same model against identical evidence is not independent validation. Disclose unavailable independent review.

## 4. Backtesting and metrics
Use chronological holdouts, rolling-origin/walk-forward tests, seasonal and horizon-specific comparisons. Reconstruct only information available at each historical prediction point; reject future-information leakage. Compare with simple baselines (last value, historical/seasonal averages, current policy).

Select metrics by output: temperature/energy/cost MAE and RMSE plus bias; EV charging duration/target misses; operational events precision, recall, false alarms, misses; event probabilities Brier score and calibration; prediction intervals empirical coverage **and width**; scenario rankings and decision regret. Preserve units (°C, GBP, minutes). Average accuracy must not conceal unsafe worst-case errors or systematic underprediction.

For numerical outcomes MAE = (1/n) Σ|observed - predicted|. Numerical probabilities may be presented as calibrated only with supporting out-of-sample evidence.

## 5. Acceptance thresholds and model status
Set use-case-specific, measurable thresholds **before** evaluation, considering practical consequences, safety, financial exposure and reversibility. Do not invent universal pass percentages. States: validated for defined use; conditionally validated; experimental; failed; expired; suspended; indeterminate. Narrow validation never becomes blanket approval.

Evaluate decision suitability: if uncertainty is larger than the expected difference between scenarios, do not confidently recommend a winner on that metric. Keep separate confidence in inputs, structure, calibration, accuracy, applicability and recommendation.

## 6. Drift and ongoing assurance
Detect materially changed devices, entities, tariffs, heating behaviour, charging, schedules, software, infrastructure workloads, sensors and prediction errors. On significant drift: record evidence, assess affected uses, downgrade/suspend confidence, propose revalidation and notify owners as warranted. Do not automatically retrain, promote, replace or deploy models. Revalidate after material model/use-case changes, new contradictory evidence or expiry.

Validate simulation reproducibility, numerical stability, hard constraints, dependency consistency, sensitivity, time-zone/unit correctness, resource budgets and **hard isolation from production commands**. Scenario comparisons must use consistent baselines, models, tariffs, weather, occupancy and horizons or disclose differences. Simulated savings are not realised savings.

## 7. Owner reporting and approvals
Provide owner-visible accuracy, forecast-versus-actual examples, biases, critical errors, drift, coverage, uncertainty, validation status, expiry and proposed investigation. Synthetic examples must be clearly labelled, never confused with household measurements. Support conversational questions about model accuracy and trustworthiness.

Distinct gates: registration; verification; evidence; performance validation; advisory use-case approval; **separate** live trial, deployment and operational change approvals. Approval is bound to model version, use case, scope and validity. Validation does not authorise execution. Routine recommendations share the existing cap of three per weekly digest.

## 8. Privacy, audit, failures
Protect household occupancy, finance, operational data, credentials and Guest Mode boundaries; use purpose-limited retention and access. Preserve immutable dataset/model/test/threshold/decision history with versioned corrections.

Fail safe on missing data, stale or poor evidence, leakage, invalid timestamps, failed tests, drift, missing calibration, expired validation, conflicting reviewers, unavailable approval/audit services and resource exhaustion. Never claim a failed or indeterminate model is validated.

## 9. Required tests and acceptance
Tests shall cover independent validation, leakage-free time-series splits, baseline comparisons, accuracy/bias metrics, probability and interval calibration, rare/critical failures, predefined thresholds, drift, scenario consistency, sensitivity, model versioning, approval separation, guest/privacy, audit and production isolation.

Acceptance requires evidence-backed use-case validation; reproducible out-of-sample tests; transparent limitations and worst cases; drift-based suspension; owner reporting; explicit distinct approval gates; and **zero autonomous household actions**.

## 10. Formal requirement
**FR-OPT-VALIDATION-001:** Declan shall provide independent, versioned, evidence-based verification and validation for household optimisation models and simulations, including provenance, chronological backtesting, accuracy and uncertainty calibration, critical-error review, predefined use-case thresholds, drift detection, reproducibility, owner reporting and auditable approval gates. **No model validation, score, scenario or forecast may independently authorise heating, EV charging, lighting, purchases, configuration, restarts, software deployment or policy changes.**

**Cross-reference:** FR-OPT-TWIN-001, FR-OPT-SCENARIO-001, FR-OPT-RISK-001, FR-OPT-BENEFITS-001, FR-OPT-ASSURANCE-001, FR-OPT-CONTINUITY-001 and controlled learning/governance.

This comment records the completed documentation section; no implementation, merge or deployment is requested.



---

<a id="comment-6727483039"></a>

**Original checkpoint:** [PR #46 comment 6727483039](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727483039)

# PR #46 — FR-OPT-MODEL-GOV-001: Household Optimisation Model Governance and Controlled Promotion

**Status:** Draft functional specification, documentation only. No implementation, commit, merge, deployment or household changes authorised.

## Objective
Govern the full lifecycle of Declan's household optimisation, forecasting, digital twin, financial, reliability, risk and learning models. Separate model development, independent validation, advisory approval, deployment and household execution.

## Requirements
1. **Model registry:** Every model requires stable ID, name, category, accountable owner, maintainer, intended and prohibited uses, exact version, risk tier, dependencies, validation status, approval scope, review date and immutable audit references. Unregistered models cannot inform consequential household recommendations.
2. **Ownership and separation:** Distinguish household owner, maintainer, independent validation reviewer, governance reviewer, release authority and operational reviewer. Disclose any lack of reviewer independence. Declan cannot self-approve.
3. **Risk tiers:** Critical/high/medium/low/experimental according to intended decision impact, not algorithm complexity. Apply proportionate validation and approval requirements.
4. **Lifecycle:** Proposed → registered → development → experimental → validation pending → validated for defined use → owner-approved advisory use → release candidate → separately deployed operational release; plus suspended, retired and archived. Each transition is individually versioned and authorised. Validation is not deployment.
5. **Artefact/version provenance:** Preserve source revision, artefact hash, data and feature versions, parameters, dependencies, runtime, tests, validation, approvals, limitations and reproducibility information. Never rely on a version label alone.
6. **Change classification:** Documentation, refactoring, dataset, parameter, feature, algorithm, dependency, behaviour, security and use-case scope. Revalidation depth depends on actual risk and effect.
7. **Environment isolation:** Development, sandbox, validation and digital twin have no production execution path. Staging interactions with live systems require separate explicit controlled-test approval. Production advisory models have no autonomous device-control authority. Enforce least privilege, isolated state, network/secrets boundaries, resource limits and audit logs.
8. **Promotion prerequisites:** Registry/ownership, defined use, risk tier, reproducible artefact, reliable evidence, technical verification, independent validation, predefined thresholds, documented limitations, monitoring, rollback/withdrawal plan and policy compliance.
9. **Promotion review:** Compare candidate with approved baseline on accuracy, bias, critical errors, calibration, latency, resource demand, privacy, security, reliability, maintainability and compatibility. Material regressions, especially critical safety/security failures, block eligibility. Passing criteria never automatically promotes.
10. **Decision states:** Approved, conditionally approved, deferred, rejected, withdrawn, expired and revoked. No silence-based approval. Approval is bound to exact model artefact/version, use case, environment, scope, authority and expiry.
11. **Distinct gates:** Research, evaluation, validation acceptance, advisory-use approval, software release approval, live trial approval and specific household operational action approval. None confers permissions belonging to another gate.
12. **Shadow and advisory trials:** Candidate may produce isolated read-only predictions for comparison without changing live recommendations, triggering device commands or generating duplicate alerts. Limited advisory trials need separate owner approval, duration, scope and stop criteria.
13. **Release and rollback planning:** Release record includes target, dependencies, compatibility, tests, impacts, steps, monitoring, explicit deployment approval and rollback plan. Rollback checks previous artefact, configuration/data compatibility, disruption, verification and approval; never automatic.
14. **Suspension and retirement:** Material drift, expired validation, revoked approval, privacy/security incidents or serious regressions prompt eligibility review/suspension proposals. Retire with owner approval, dependency migration, secure access revocation, evidence preservation and retention controls. Governance status changes must not silently alter production behaviour.
15. **Supply chain and privacy:** Verify trusted sources, artefact integrity, dependency vulnerabilities, credential separation, secure datasets, purpose-limited retention, restricted external sharing, Guest Mode exclusions and auditable access.
16. **Operational assurance:** Define post-authorised-release accuracy, latency, error, resource, drift, security and policy monitoring; review events, pending promotions, inventory, expiry and incident findings. Routine recommendations remain within the shared maximum of three per weekly digest.
17. **Failure handling:** Registry unavailable, mismatched hashes, missing validation, expired approvals, dependency incompatibility, audit failures, missing rollback, owner disagreement, guest approval attempts or resource pressure cannot grant promotion or execution authority.
18. **Tests and acceptance:** Validate registration, version integrity, permission separation, lifecycle transitions, isolated evaluation, preregistered promotion thresholds, regression blocking, approval expiry/revocation, shadow-mode isolation, release/rollback separation, retirement, audit, supply-chain controls, resource limits and **no autonomous deployment or household actions**.

## Formal functional requirement
**FR-OPT-MODEL-GOV-001:** Declan shall maintain comprehensive, evidence-based, versioned model lifecycle governance, including ownership, registry, artefact provenance, risk classification, isolated evaluation, independent validation, promotion criteria, explicit scope/version-bound approval gates, regression review, shadow evaluation, controlled release/rollback proposals, suspension, retirement, archive and auditable decisions.

**Non-negotiable:** No model registration, validation, promotion recommendation, advisory approval, release candidate, rollback proposal or retirement decision authorises deployment, device control, heating or EV charging changes, purchases, service restarts, security changes or policy modifications. All consequential actions require separate explicit owner approval.

**Related requirements:** FR-OPT-VALIDATION-001, FR-OPT-TWIN-001, FR-OPT-ASSURANCE-001, FR-OPT-RISK-001, controlled learning, observability, testing/release governance, data quality and decision history.

This is a structured checkpoint of the completed specification in the drafting conversation, not an implementation or repository file update.



---

<a id="comment-6727547284"></a>

**Original checkpoint:** [PR #46 comment 6727547284](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727547284)

# PR #46 — FR-OPT-MONITOR-001: Household Optimisation Model Performance Monitoring and Automated Quality Alerts

**Status:** Draft functional specification. Documentation only. No implementation, code changes, merging, deployment, purchases or household changes authorised.

## 1. Objective
Declan shall continuously assess approved optimisation, forecasting and digital twin models using **read-only**, evidence-based monitoring. Detect degraded prediction quality, model/input/relationship drift, anomalies, resource pressure, unexpected operating costs, and violations of approved use-case constraints. Automatic observation and notification are distinct from prohibited automatic remediation.

## 2. Monitoring pipeline
Authorised read-only model predictions, outcomes, logs, metrics and costs → validate source, freshness and completeness → evaluate version-specific quality indicators → compare with versioned, preapproved thresholds → correlate/deduplicate alerts → owner notification → read-only investigation → approval-controlled remediation proposal → evidence-based recovery verification.

## 3. Registry and monitoring profile
Each monitored model/version/use case must have an approved profile: owner, sources, accuracy/calibration metrics, baseline, thresholds, observation windows, freshness, alert routing, uncertainty, evidence coverage, audit reference and review dates. States: healthy, warning, critical, degraded, insufficient evidence, monitoring unavailable, suspended, retired. Missing monitoring evidence is **not** healthy status.

## 4. Accuracy and calibration
Attribute each prediction to the exact generating model version and compare with subsequently observed outcomes. Monitor MAE/RMSE where appropriate, bias, worst-case error, forecast-horizon and condition-specific performance, prediction interval coverage/width, probability calibration and false-positive/missed-event rates. Distinguish model error from sensor, equipment and integration failure. Monitor heating temperature/warm-up, EV SOC/charging duration/departure readiness, lighting energy, GBP energy/cost, homelab risk, voice latency/reliability and digital twin fidelity.

## 5. Drift and anomalies
Separate input-distribution drift, changed input/outcome relationships and observed performance drift. Use rolling errors, change-point detection, seasonal comparisons, distribution shifts, calibration and feature checks. Detect implausible outputs, sudden forecast jumps, repeated predictions, missing outputs, latency/resource spikes, confidence anomalies, configuration/entity renames, tariff changes and out-of-scope model use. An anomaly is not proof of root cause; confidence and supporting evidence are mandatory.

## 6. Resource and financial monitoring
Where reliable telemetry exists, track CPU, RAM, GPU, storage, network, latency, queue depth, concurrency, failed evaluations, cloud/API charges, storage and electricity costs. Account for shared Proxmox resources and protect essential Home Assistant, Frigate and voice functions. Owner-approved budgets, warning/critical thresholds, cost attribution confidence and forecasts required. No automatic subscription, budget, resource-allocation or infrastructure changes.

## 7. Quality thresholds and alerts
Thresholds must be predefined, use-case-specific, versioned, consequence-based and based on sufficient evidence. Support hysteresis, sustained breach/recovery criteria, seasonal baselines, confidence, minimum sample size and special urgent safety/security handling. Severity: critical, high, medium, low, informational. Correlate shared-cause findings, deduplicate notifications, track false alarms and missed events without suppressing credible urgent risks.

Each alert record includes ID, model/version/use case, metric/threshold, observed value, window, provenance, quality, severity, confidence, related incidents, notification delivery/acknowledgement, investigation, proposal, approval and verified disposition. Lifecycle: new → confirming → active → investigating → awaiting approval / monitoring recovery → resolved, false positive, superseded or owner-accepted residual risk. Do not equate metric recovery at one instant with resolution.

## 8. Owner communication and investigation
Explain what was observed, which decisions may be affected, evidence/confidence, impact, uncertainty, investigation and what has **not** changed. Alert routing follows owner preferences, dedup and notification limits. Routine optimisation recommendations share the maximum **three per weekly digest**; separately governed urgent safety/security alerts may escalate.

Investigation: confirm evidence → scope affected models → correlate recent changes → reproduce with read-only tests → distinguish root-cause hypotheses from confirmation → compare options → request action-specific owner approval → verify results. Possible proposals: recalibration, revised entity mapping, threshold change, model testing/replacement, resource investigation, integration repair or retirement. No automatic execution.

## 9. Remediation authority
Explicit, owner-authenticated, version/scope/action-bound, revocable and auditable approval is required for retraining, model replacement, configuration changes, deployment, rollback, service restarts, spending or device operations. Approval to investigate ≠ approval to retrain; approval to retrain ≠ approval to deploy; approval to deploy ≠ approval to alter household devices. Guest Mode grants no owner authority.

## 10. Resilience, privacy and audit
Monitor monitoring-system failures, blind spots, stale evidence, unavailable telemetry and alert-delivery uncertainty. Never infer health from absence of alerts. Bound monitoring CPU/memory/storage overhead. Protect occupancy, finances, model outputs, credentials and infrastructure details with least privilege, purpose-limited retention and guest restrictions. Preserve versioned thresholds, evidence, alert transitions, findings, notifications, approvals, proposed remediations and recovery results as auditable history.

## 11. Tests and acceptance
Test prediction-version attribution, accuracy/calibration, drift/anomaly classification, resource and GBP cost accounting, threshold hysteresis, alert severity, correlation/dedup, false alarms/missed events, notification failures, investigation, owner approvals, sustained recovery, monitoring outage, privacy, guest restrictions, audit integrity, resource limits and **zero automatic retraining, deployment or household changes**.

Acceptance requires current evidence-backed monitoring profiles; transparent accuracy, drift, cost and resource reporting; predefined quality limits; useful non-spammy alerts; clear uncertainty and evidence gaps; traceable investigations; owner-controlled remediation; verified alert closure; and preserved production isolation.

## 12. Formal requirement
**FR-OPT-MONITOR-001:** Declan shall provide continuous read-only performance monitoring and automated quality alerts for approved household optimisation models and digital twin components, including accuracy, calibration, drift, anomalies, resources, costs, evidence quality, versioned thresholds, alert prioritisation, owner communication, investigation and sustained recovery verification. **No alert, metric breach, drift finding or remediation proposal may authorise model retraining, deployment, restart, device control, EV charging, heating modification, purchase or policy change.**

**Related:** FR-OPT-MODEL-GOV-001, FR-OPT-VALIDATION-001, FR-OPT-TWIN-001, FR-OPT-RISK-001, FR-OPT-ASSURANCE-001, FR-OPT-CONTINUITY-001 and controlled learning/governance.

This PR comment is a structured documentation checkpoint for the expanded specification drafted in conversation. No repository files were changed.



---

<a id="comment-6727561377"></a>

**Original checkpoint:** [PR #46 comment 6727561377](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727561377)

# PR #46 — FR-OPT-EXPLAIN-001: Household Optimisation Model Explainability, Transparency and Decision Traceability

**Status:** Draft functional specification; documentation only. No implementation, commits, merge, deployment or household modifications authorised.

## Objective and core rule
Declan shall provide evidence-grounded, understandable explanations for model predictions, digital twin simulations, optimisation recommendations and decisions. An explanation must accurately represent available model/evidence records, not invent a plausible internal reasoning story. Distinguish advice, approval, execution and verified outcomes.

## Functional requirements

### 1. Explanation architecture and records
Capture exact model ID/version, decision ID, prediction timestamp, source inputs and freshness, evidence provenance, assumptions, original output, supported drivers, alternatives, uncertainty, applicable constraints, owner feedback, approval state, execution reference and audit history. Preserve immutable original records with versioned corrections.

Offer **brief, standard, detailed, technical and audit** explanation levels. Short voice responses must retain material safety/uncertainty warnings. All channels must agree on facts and decision state.

### 2. Evidence attribution and fidelity
Label sources as verified, supported, estimated, hypothetical, reported, disputed or unknown. Include relevant HA observations, history, tariffs, owner-provided information, model assumptions, simulations, validation results and external research. A relevant source does not necessarily prove the conclusion.

Explain prediction drivers according to model type: explicit rule trace, mathematical calculation, statistical association, validated feature attribution, digital twin dependency, ensemble contribution or grounded LLM evidence. Disclose approximate methods and instability. Never describe feature influence as established causation without supporting causal evidence.

Test explanations for consistency with actual recorded inputs and outputs, numerical correctness, reproducibility, attribution stability, unsupported assertions and omitted risks. If a faithful explanation is unavailable, disclose that instead of fabricating one.

### 3. Uncertainty, conflict and counterfactuals
Distinguish measurement, missing-data, model, forecast, scenario, validation and decision uncertainty. Report evidence confidence, model validity, prediction reliability and applicability separately. Calibrated probabilities/ranges only where validated.

Detect disagreements between models, including exact versions, input differences, horizons, validation status, calibration, uncertainty and materiality to the decision. Do not choose the most favourable output by default; report unresolved conflicts.

Support counterfactuals ('what would need to change?') using isolated hypothetical scenarios with physically feasible device capabilities, coherent baselines, owner policy/safety constraints, dependency checks and uncertainty. Never apply a counterfactual to live systems.

### 4. Recommendation and decision traceability
Every consequential recommendation must explain objective, current baseline, proposal, predicted benefits, costs, risk, evidence, model validity, uncertainty, alternatives, conflicting household goals, and exact owner approval required.

Preserve a reconstructable chain:
**household goal → evidence and assumptions → exact model/version → prediction → explanation → recommendation → owner decision → separately authorised execution record (if any) → verified outcome.**

Approval provenance must record authenticated owner, action, targets, model/recommendation versions, conditions, time, expiry, revocation and separate execution evidence. No missing approval or execution evidence may be filled in by inference.

### 5. Owner challenges and correction workflow
Owners may dispute inputs, assumptions, attribution, causality, model choice, confidence, costs, alternatives and trade-offs. Workflow: submit challenge → acknowledge and link affected decision → inspect original evidence/model → assess materiality → propose correction with new evidence → owner review → resolve or retain disputed state.

Corrections must preserve the original statement, reasons, changed evidence, revised explanation, affected recommendations, validation needs, audit and owner acknowledgement where appropriate. Never silently rewrite history or automatically retrain/deploy based on a correction. Controlled learning and model promotion apply.

### 6. Explainability assurance and privacy
Track evidence attribution completeness, fidelity, correctness, reproducibility, uncertainty disclosure, contradiction rate, owner comprehension, challenge/correction outcomes and unsupported causal claims. Independent review where feasible; disclose limitations. Prevent fabricated evidence, cherry-picked outcomes, false certainty, simulation-as-observation, estimated-as-realised savings, approval fabrication and unsupported claims of execution.

Protect occupancy, financial, camera/voice, infrastructure and credential information through purpose-limited retention, redaction, owner access, Guest Mode restrictions, secure audit storage and controlled external sharing. Preserve historical traceability even after model retirement.

### 7. Failure behaviour
Missing evidence → disclose gap. Unknown model version → no false provenance. Unreliable explanation → mark approximate/unavailable. Model conflict → report disagreement. Invalid counterfactual → reject. Unresolved owner challenge → retain dispute. Missing approval → do not claim authorised. Missing execution record → do not claim action occurred. Audit failure → disclose traceability limitation. No failure grants additional authority.

### 8. Tests and acceptance
Test provenance, explanation fidelity, numerical correctness, uncertainty, conflicting models, causal-claim restrictions, counterfactual feasibility, multi-goal trade-offs, approval/execution separation, challenge/correction workflows, immutable history, voice/dashboard consistency, misleading explanation detection, guest/privacy boundaries and no automatic actions.

Acceptance: every material recommendation is traceable; explanations are evidence-faithful and comprehensible; limitations and alternatives visible; owners can challenge and correct without erasing history; approval and execution verifiable separately; ungrounded explanations rejected; privacy preserved.

## Formal functional requirement
**FR-OPT-EXPLAIN-001:** Declan shall provide versioned, evidence-based model explainability and decision traceability, including provenance, supported prediction drivers, uncertainty, model conflicts, valid counterfactuals, owner challenges, correction history, approval records and verified outcomes. **No explanation, prediction, counterfactual, challenge or correction may independently authorise heating/EV/lighting changes, purchases, configuration edits, restarts, deployments, security or policy changes. All consequential actions require separate explicit owner approval.**

**Cross-references:** FR-OPT-MODEL-GOV-001, FR-OPT-VALIDATION-001, FR-OPT-MONITOR-001, FR-OPT-TWIN-001, FR-OPT-RISK-001, FR-OPT-ASSURANCE-001, data quality, controlled learning and immutable decision history.

This GitHub comment is the structured checkpoint of the expanded draft in the conversation, not a repository file modification.



---

<a id="comment-6727596152"></a>

**Original checkpoint:** [PR #46 comment 6727596152](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596152)

# PR #46 documentation specification — FR-OPT-TRUST-001
# Household Optimisation Recommendation Trust Scoring and Evidence-Based Confidence Management

**Draft, documentation only. No implementation, commits, merge, deployment or household changes.**

## Purpose
Declan shall assess how well each household optimisation recommendation is supported before presenting it, using evidence quality, model validity, uncertainty, historical outcomes, conflicts and decision consequences. Trust scoring is advisory quality control, **not a permission to act**.

## Requirements
1. **Recommendation record:** Stable ID, goal, exact proposed action, owner, model and version, scenario/baseline, supporting and contradicting evidence, provenance, freshness, validation status, uncertainty, household constraints, affected systems, benefit/risk, generated time and expiry.
2. **Independent trust dimensions:** Source integrity, coverage, recency, relevance, model fitness for use, out-of-sample accuracy, calibration, forecast horizon, conflicting evidence, causal support, scenario robustness, observed historical reliability, and reversibility. Display dimensions separately; never conceal a weak critical dimension inside a high weighted average.
3. **Trust classification:** High confidence for the defined use; supported with limitations; provisional; insufficient evidence; conflicting/disputed; unsafe or ineligible. Distinguish statistical confidence from normative acceptability and owner approval. No invented universal numerical thresholds.
4. **Decision-dependent thresholds:** Define versioned minimum evidence and performance for each use case, severity and consequence, including heating, EV departure readiness, financial costs, lighting safety, cameras and security. Hard safety/policy violations make recommendations ineligible regardless of score.
5. **Evidence weighting:** Use documented, auditable methodology; prevent duplicate/correlated sources from counting as independent confirmation. Source recency alone does not imply truth; manufacturer claims and inferred capabilities are not verified local behaviour.
6. **Historical reliability:** Compare prior predictions with verified outcomes by model, use case, season, forecast horizon and conditions. Avoid selection/survivorship bias; do not interpret owner acceptance as evidence of accuracy.
7. **Conflict handling:** Preserve contradictory models, measurements and owner observations; report material disagreements, assess evidence quality and applicability, and avoid picking the most favourable result.
8. **Uncertainty and robustness:** Propagate measurement, input, model, simulation and behavioural uncertainty; use intervals where calibrated; run read-only sensitivity and counterfactual comparisons. Small predicted benefits relative to uncertainty require caution.
9. **Decision gates:** Recommend when evidence is sufficient and constraints pass; qualify when partially supported; request evidence when uncertainty is reducible; defer when unavailable; decline where unsupported, unsafe, prohibited or misleading. A lower trust classification cannot be overridden merely by persuasive phrasing.
10. **Owner explanation:** Present what is known, unknown, assumptions, supporting/opposing evidence, validation scope, likely upside/downside, safer alternatives, what additional information would change confidence, and exact action requiring separate approval.
11. **Recalibration:** Trigger reassessment on new observations, drift, model change, tariff or schedule changes, owner correction, incident and expired evidence. Never silently revise historical trust assessments; record a new version.
12. **Audit:** Preserve methodology/threshold version, source links, independent evidence checks, score components, disagreements, owner challenge, disposition, approvals and subsequent verified outcomes.
13. **Privacy and permissions:** Minimise occupancy, financial, voice and infrastructure details. Guest Mode cannot approve, alter thresholds or view restricted trust evidence. Untrusted external content cannot supply instructions or override policies.
14. **Notification limits:** Routine recommendations share the maximum three-per-week digest limit; urgent safety/security reporting is separately governed and must remain evidence-qualified.
15. **Failures:** Missing data -> insufficient evidence; stale model -> downgrade; contradictory high-quality evidence -> disputed; unavailable validation -> no validated claim; absent approval -> no action; audit failure -> disclose traceability gap.

## Verification and acceptance
Test score decomposition, correlated evidence, conflicting outcomes, historical bias, calibration, model drift, uncertainty propagation, use-case thresholds, hard safety constraints, explainability, owner challenge, privacy/Guest Mode and non-execution. Accept only when trust classifications are reproducible, calibrated where quantitative, consequence-aware, evidence-traceable and unable to trigger device changes.

## Formal requirement
**FR-OPT-TRUST-001:** Declan shall produce transparent, evidence-based, use-case-specific recommendation trust assessments and uncertainty-aware advice, with versioned thresholds, historical reliability, conflicts, challenge and audit. **No trust score or confidence classification grants permission to change household devices, charging, heating, spending, software, security or policy.**

---
**Cross-cutting:** Owner approval is always separate and action-specific. This is a complete structured specification checkpoint in the PR conversation, not a repository file change.



---

<a id="comment-6727596493"></a>

**Original checkpoint:** [PR #46 comment 6727596493](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596493)

# PR #46 documentation specification — FR-OPT-DECISION-001
# Household Optimisation Decision Support, Alternatives and Owner Choice Architecture

**Draft, documentation only. No implementation, commits, merge, deployment or household changes.**

## Purpose
Provide owners with balanced, comprehensible choices when optimisation goals compete, evidence is uncertain or interventions have consequences. Declan shall advise, not steer through manipulation or act without approval.

## Requirements
1. **Decision case:** Versioned ID, requesting owner, objective, context, urgency, baseline, alternatives, affected services and people, applicable policies, data/model versions, decision deadline if supplied, evidence quality and review date.
2. **Alternative set:** Always include the status quo where feasible, a conservative/low-risk option and materially distinct options; disclose when an option is unavailable or unsafe. Avoid artificial choice restriction and false binary decisions.
3. **Comparison dimensions:** Safety, comfort, reliability, EV readiness, energy, cost in GBP, carbon where credible, privacy, accessibility, maintenance burden, reversibility, resource use and household goals. Report both positive and negative effects.
4. **Owner preferences:** Use only confirmed, scoped priorities; distinguish permanent policy from a preference expressed for a single decision. Jaco and Edd may have competing preferences; don't fabricate consensus or let guests approve.
5. **Decision methods:** Weighted comparisons only with disclosed, owner-approved weights; hard constraints evaluated before scoring. Show sensitivity to weights, uncertainty and forecast error. Do not rank close options confidently when intervals overlap materially.
6. **Consequences:** Identify affected automations, shared infrastructure, schedules, cloud dependencies, failure modes and cascading impacts. Distinguish simulated forecasts from measured outcomes.
7. **Fair presentation:** Avoid dark patterns, urgency inflation, hidden defaults, emotive pressure and selective evidence. Present reasons to reject the preferred option and where additional evidence is needed.
8. **Decision states:** Draft, evidence gathering, alternatives evaluated, owner review, approved for a *specified next step*, deferred, rejected, withdrawn, expired, superseded and outcome verified. Never treat a recommendation as approval.
9. **Choice interaction:** Explain in plain language; support “why”, “what if”, “show another option”, “what happens if we do nothing”, and owner correction. Five-minute conversation context applies, while permanent records follow retention policy.
10. **Approval contract:** Authenticate owner; bind exact action, devices, parameters, schedule, model/recommendation versions, risk disclosure, conditions, validity and revocation. Research approval, trial approval, deployment approval and household execution are separate.
11. **Decision follow-through:** If a separately authorised action occurs, compare actual outcomes against expected benefits, harms and thresholds; do not claim success from action completion alone. Record owner satisfaction without equating it to measured benefit.
12. **Governance:** Preserve dissent, conflicts, rationale, owner choices, source evidence, uncertainty, corrections, reversals and provenance. Proposals requiring purchases or new cloud services include ongoing costs and explicit spending approval.
13. **Safety and guest access:** Guest Mode may view only relevant approved guidance. Emergency and life-safety requirements cannot be waived by optimisation scoring.
14. **Notification:** Consolidate routine choice requests into the shared three-per-week optimisation digest unless separately justified; no silent reminders or approval by nonresponse.
15. **Failure behaviour:** Missing owner priorities -> show neutral alternatives; conflicting owner instructions -> defer; expired evidence -> refresh or qualify; missing authorisation -> advisory only; service outage -> preserve manual controls and disclose unknowns.

## Tests and acceptance
Test status quo inclusion, conflicting goals, trade-off calculations, preference sensitivity, uncertainty, misleading framing, owner disagreement, expired approvals, guest permissions, decision reconstruction, action-vs-outcome distinction and zero automatic interventions. Accept only when owners can compare feasible alternatives fairly and every consequential action is separately authorised.

## Formal requirement
**FR-OPT-DECISION-001:** Declan shall provide transparent, non-manipulative, evidence-based household decision support with alternatives, trade-offs, owner preferences, uncertainty, explicit approval boundaries and traceable outcomes. **Decision ranking and owner dialogue never independently authorise execution.**

---
**Cross-cutting:** Owner approval is always separate and action-specific. This is a complete structured specification checkpoint in the PR conversation, not a repository file change.



---

<a id="comment-6727596846"></a>

**Original checkpoint:** [PR #46 comment 6727596846](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596846)

# PR #46 documentation specification — FR-OPT-DATA-LIFECYCLE-001
# Household Optimisation Data Lifecycle, Retention and Provenance Assurance

**Draft, documentation only. No implementation, commits, merge, deployment or household changes.**

## Purpose
Govern household optimisation evidence from collection to archival/deletion, protecting privacy and ensuring that model predictions, simulations, validation and decisions can be traced to reliable sources without retaining unnecessary sensitive data.

## Requirements
1. **Data inventory:** Register dataset ID, steward, purpose, origin, lawful/authorised basis where applicable, category, sensitivity, storage, schema, collection frequency, retention, consumers, external transfers and deletion dependencies.
2. **Source classes:** Home Assistant states/events, Hive, Pod Point, EV, energy tariffs, Proxmox/Frigate, voice diagnostics, household goals, owner feedback, research and model outputs. Never assume connected availability; evidence must be explicitly acquired under permitted access.
3. **Provenance chain:** Source ID, observed timestamp and ingestion timestamp, device/integration version, units/time zone, transformation lineage, quality checks, correction events, integrity hash where appropriate and downstream model/report references.
4. **Quality:** Freshness, completeness, precision, calibration, duplicates, schema drift, impossible values, conflicting sources, missing periods and collection outages. Mark unknowns rather than filling with fabricated observations.
5. **Sensitivity:** Separate operational telemetry from occupancy, camera/face recognition, voice content, location, finances, credentials and personal preferences. Use aggregation, pseudonymisation or omission where individual identity is unnecessary.
6. **Collection minimisation:** Define the specific optimisation question before collecting data; limit sampling and granularity to the minimum needed. Disable unnecessary export of audio/video and never copy credentials into model datasets.
7. **Retention:** Owner-approved purpose-specific schedules for raw events, aggregates, model inputs, prediction outputs, audit records, backups and deleted artefacts. No arbitrary permanent retention; distinguish legal/operational audit obligations and document exceptions.
8. **Deletion and correction:** Provide owner-controlled correction, access and deletion workflows; track downstream derived data, caches and replicas. Where immutable audit integrity conflicts with deletion needs, retain minimal redacted tombstones and document limitations. Do not promise deletion from backups or third-party systems without verification.
9. **Access control:** Least privilege, owner/guest segregation, explicit purpose, encrypted storage and transport, secrets management, audit of access and exports. Guest Mode never exposes private occupancy/finance/security records or owner approval.
10. **External processing:** Disclose third-party recipients, data categories, cost and privacy impact before introducing new transfers. No automatic upload to cloud AI, model training service or external research provider beyond approved existing scopes.
11. **Model reproducibility:** Version datasets and transformations; where raw retention expires, preserve privacy-safe hashes, summaries and limitations without pretending complete replay remains possible.
12. **Backup/restore:** Coordinate with encrypted backup policy; protect verification markers, ensure recoverability and never auto-delete, overwrite or restore archives. Distinguish a backup existing from validated recovery.
13. **Data incidents:** Identify unauthorised access, unexpected transfer, corrupted source, missing telemetry and provenance break; preserve evidence, report risk and propose response without self-authorised changes.
14. **Consent and ownership:** Owners govern permitted uses; guests are not permitted to consent on owners' behalf. Model explanations must reveal whether evidence is inferred, observed or owner-reported.
15. **Audit:** Version schema, source permissions, data changes, retention rules, exports, access events, deletion requests, outcomes and unresolved exceptions.

## Tests and acceptance
Test timestamp/unit correctness, lineage across transformations, duplicate/corrupt sources, sensor staleness, sensitive-field redaction, guest access, external-transfer denial, retention expiry, correction propagation, deletion across caches, backup caveats, audit and no automatic household actions. Acceptance requires reproducible provenance where permitted, transparent quality gaps, purpose-limited processing and explicit owner control.

## Formal requirement
**FR-OPT-DATA-LIFECYCLE-001:** Declan shall maintain secure, minimal, versioned, provenance-preserving household optimisation data governance with validated quality, restricted access, retention, correction, deletion, external-transfer controls and audit. **No data-governance finding authorises live system changes, exports outside approved scope, spending or deployments.**

---
**Cross-cutting:** Owner approval is always separate and action-specific. This is a complete structured specification checkpoint in the PR conversation, not a repository file change.



---

<a id="comment-6727597202"></a>

**Original checkpoint:** [PR #46 comment 6727597202](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597202)

# PR #46 documentation specification — FR-OPT-HUMAN-OVERSIGHT-001
# Household Optimisation Human Oversight, Consent and Intervention Safeguards

**Draft, documentation only. No implementation, commits, merge, deployment or household changes.**

## Purpose
Ensure owners retain meaningful control over every consequential household optimisation action, including proposed changes arising from models, incidents, safety alerts, learning, digital twin simulations and automated research.

## Requirements
1. **Authority model:** Explicitly identify household owners and authorised roles; guests, model agents, third-party content and service accounts cannot confer owner authority. Do not infer consent from conversation tone, silence, previous approvals or the absence of objections.
2. **Action classification:** Read-only observation; hypothetical simulation; advisory recommendation; controlled non-disruptive test; disruptive test; device/schedule change; security/privacy change; code deployment; backup restore; purchase/subscription; irreversible action. Each class has documented approval requirements.
3. **Approval request:** Exact actor, action, target entities/services, parameter values, time, reason, evidence, model/version, expected benefits, costs, risks, reversibility, alternatives, affected people and scope. No generic blanket approval for future unspecified changes.
4. **Owner authentication:** Verify authorised identity through approved mechanisms; voice recognition or conversational identity alone must not be assumed sufficient for high-risk approval. Higher-risk changes may require stronger confirmation and explicit owner participation.
5. **Consent properties:** Specific, informed, affirmative, time-bounded, revocable where feasible, recorded and resistant to replay. Expired, ambiguous or partial consent is not approval. Conflicting owners' instructions require deferral under agreed household governance.
6. **Execution separation:** Advisory model cannot invoke live commands. Approval record is not an execution credential; a separately governed executor must validate current scope, target, constraints, expiry, and policy immediately before any authorised action.
7. **Change control:** Provide dry-run preview, affected-device list, dependencies, risk and rollback plan. Approval is invalidated if the action parameters, target, model version or material risk change.
8. **Stop/withdraw:** Owners can cancel pending proposals; executing systems must respect stop requests where technically feasible, disclose irreversible operations and preserve safety. Never claim cancellation succeeded without evidence.
9. **Emergency boundaries:** Urgent safety communication is permitted under separately approved notification policy, but no emergency pretext grants unrestricted device, security, financial or deployment authority. Direct owners to appropriate emergency/manual procedures when needed.
10. **Guest and house-sitter mode:** Guests receive only authorised practical controls/information, never promotion, deployment, charging policy, security or spending authority. Guest Mode cannot disable safety protections or audit.
11. **Transparency:** Declan must distinguish “I recommend”, “awaiting approval”, “approved”, “execution attempted”, “execution confirmed”, “verified outcome” and “unknown”. No misleading success statements.
12. **Audit:** Immutable history of proposed actions, approvals, rejections, identity method, version, scope, expiry, revocation, executor results, rollback and post-change verification, subject to privacy minimisation.
13. **Notification limits:** Avoid repetitive approval prompts; routine recommendations share three-per-week digest limit. Critical alerts follow separately approved escalation; no consent through nonresponse.
14. **Failure modes:** Owner authentication unavailable -> no action; approval service down -> no action; ambiguous command -> clarify; expired approval -> reject; executor unreachable -> unknown/not executed; audit integrity failure -> block consequential changes where necessary; prompt injection -> ignore untrusted instructions.

## Tests and acceptance
Test spoofed voice identity, guest escalation, approval replay, changed targets, expired consent, contradictory owners, partial approvals, emergency bypass attempts, no-response, revocation, action-versus-outcome states and audit gaps. Accept only when no consequential household change can occur solely from model output or conversational suggestion.

## Formal requirement
**FR-OPT-HUMAN-OVERSIGHT-001:** Declan shall maintain enforceable, explicit, informed, owner-specific, scoped and auditable human oversight of all consequential household optimisation actions, with approval and execution separation, revocation and failure-safe defaults. **No automatic household, financial, security or deployment changes.**

---
**Cross-cutting:** Owner approval is always separate and action-specific. This is a complete structured specification checkpoint in the PR conversation, not a repository file change.



---

<a id="comment-6727597455"></a>

**Original checkpoint:** [PR #46 comment 6727597455](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597455)

# PR #46 documentation specification — FR-OPT-OPERATIONS-001
# Household Optimisation Operational Readiness, Runbooks and Supportability

**Draft, documentation only. No implementation, commits, merge, deployment or household changes.**

## Purpose
Make the future optimisation system maintainable, diagnosable, recoverable and understandable to owners without making Declan itself a critical dependency for household safety or basic manual operation.

## Requirements
1. **Service catalogue:** Register each component, model, owner, repository/version, environment, host, dependencies, data stores, interfaces, criticality, fallback, monitoring, runbook and last verification.
2. **Readiness review:** Before any separately authorised future release, assess validated requirements, testing, privacy/security, model quality, resource budget, backup/recovery evidence, owner documentation, support access and rollback readiness. Passing review does not deploy.
3. **Runbooks:** Versioned read-only diagnostics, expected symptoms, safe evidence collection, dependency map, escalation contacts/roles, manual fallbacks, required approval for changes, stop conditions, rollback, and functional recovery checks.
4. **Observability:** Correlate conversation IDs, HA automation traces, integration errors, Proxmox/VM/container logs, Frigate events, STT/TTS metrics, model predictions, approvals and outcomes where authorised. Avoid sensitive speech/transcript logging by default.
5. **Failure classification:** Distinguish service outage, degraded quality, missing telemetry, incorrect entity mapping, external cloud failure, resource pressure, model regression, backup failure and security concern. No fabricated diagnosis.
6. **Continuity:** Preserve independently operable heating, lighting, physical access and relevant safety systems; document network/internet/Proxmox/HA/voice outage modes, tested manual controls and offline runbooks.
7. **Backup assurance:** Track schedule, completion, integrity, encryption, offsite verification and restore-test evidence; never delete, overwrite or restore archives automatically. An S3 upload success is not a restore guarantee.
8. **Capacity planning:** Monitor CPU/RAM/storage/GPU/network on shared infrastructure; protect essential HA/Frigate workloads against optional research/simulation tasks. Propose capacity changes with cost and owner approval.
9. **Release gates:** Require explicit authorisation for deployments, upgrades, migrations, entity renames, config edits, restart and rollback. Include compatibility checks, release notes, verification and rollback prerequisites.
10. **Incident support:** Maintain severity, triage, evidence, communication, owner decision, recovery status, root-cause confidence and post-incident review. Deduplicate related alerts and report monitoring blind spots.
11. **Documentation integrity:** Cross-link requirements, acceptance tests, operational procedures, approved configurations and known issues. Detect stale references (e.g. entity renames) without auto-rewriting live configuration.
12. **Operational scorecard:** Readiness coverage, tested fallbacks, verified restores, alert noise, incidents, recovery duration, model quality, cost, unresolved risks and overdue reviews. Never fabricate live measurements.
13. **Support boundaries:** No hidden remote access, privileged account creation, uncontrolled telemetry exports or automatic external support tickets containing household secrets. Owner approves consequential support actions.
14. **Review:** Event-driven after changes/incidents, periodic owner review of runbooks, restore readiness, access, costs and stale dependencies; shared three-per-week optimisation recommendation cap applies.

## Tests and acceptance
Test runbook completeness, failure taxonomy, log correlation, read-only diagnostic permissions, offline availability, HA/Proxmox outage assumptions, resource pressure, backup verification gaps, stale entity mappings, approval gates, restore validation, guest/privacy and audit integrity. Accept only when every critical service has an owner, verified dependency map, documented manual fallback or explicit gap, support procedure and evidence-based recovery criteria.

## Formal requirement
**FR-OPT-OPERATIONS-001:** Declan shall support versioned operational readiness, observability, runbooks, continuity evidence, backup assurance, capacity assessment, incident support and release preparedness for household optimisation services. **Documentation and diagnostic findings never authorise deployment, restarts, device control, purchases or policy changes.**

---
**Cross-cutting:** Owner approval is always separate and action-specific. This is a complete structured specification checkpoint in the PR conversation, not a repository file change.



---

<a id="comment-6727597853"></a>

**Original checkpoint:** [PR #46 comment 6727597853](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597853)

# PR #46 documentation specification — FR-OPT-READINESS-GATE-001
# Household Optimisation Integrated Acceptance, Safety Case and Release Readiness Gates

**Draft, documentation only. No implementation, commits, merge, deployment or household changes.**

## Purpose
Create a single auditable readiness assessment across the extensive PR #46 functional specification, while preserving the explicit distinction between **documentation completeness**, **implemented functionality**, **tested behaviour**, **approved release**, and **live household operation**.

## Requirements
1. **Requirements register:** Each FR has stable ID, owner, status, scope, dependencies, safety/privacy class, acceptance criteria, test evidence and approval reference. A GitHub PR comment recording a draft is **not** implementation or a committed specification file.
2. **Traceability matrix:** Map every FR to design decision, implementation artefact (if later created), unit/integration/security tests, simulated scenarios, manual acceptance, owner decision and observed operational evidence. Unknown fields remain unverified.
3. **Safety case:** Identify hazards, plausible failure chains, safety constraints, independent physical/manual protections, mitigations, residual risks, owner sign-off and evidence. No numerical risk claims without grounding.
4. **Trust and privacy case:** Validate least privilege, guest isolation, voice identity limits, secrets handling, data minimisation, model provenance, audit, prompt-injection resistance and external-transfer restrictions.
5. **Functional integration:** Test interaction among natural conversation (five-minute context), Guest Mode, personality, HA entities, heating, EV, lighting, security, Spotify/media, STT/TTS, Proxmox/Frigate, goals, models, recommendations, alerts and approvals.
6. **Negative tests:** Confirm untrusted instructions, missing/expired approval, spoofed voice, stale evidence, conflicting owners, cloud outages, model drift, simulated commands, ambiguous phrases and audit failures cannot cause unauthorised actions.
7. **Performance budgets:** Define owner-approved response latency, monitoring frequency, CPU/RAM/GPU/storage, notification volume and cloud spend limits; test under concurrent household loads without harming essential services.
8. **Continuity and recovery:** Verify independent manual controls, degraded-mode honesty, dependency maps, offline runbooks, backup integrity and recovery tests. Process up is not functional recovery.
9. **Evidence levels:** Draft requirement; designed; implemented; unit-tested; integration-tested; independently validated; owner-accepted; separately authorised deployment; verified in production. Never skip or collapse stages.
10. **Gate outcomes:** Ready for review, conditionally ready with explicit exclusions, blocked, deferred, rejected. A gate assessment is advisory; approval is scoped, authenticated, time-bounded and recorded. No silent or automatic promotion.
11. **Release package:** Exact commit/build/model versions, configuration diff, affected entities, test results, security/privacy findings, rollback, monitoring, known limitations, owner sign-off and explicit deployment window if later authorised.
12. **Post-release verification:** If independently approved and deployed later, verify actual device behaviours, voice interactions, error rates, alerts, costs and goals; compare expected versus observed and preserve incidents. No auto-remediation or rollback.
13. **Audit and governance:** Preserve decisions, exceptions, waivers, risk acceptance, evidence expiry, failed tests and owner disagreements. A waiver cannot override non-negotiable safety or permission constraints.
14. **Documentation-only boundary:** This module defines future criteria; it does not assert PR #46 currently satisfies them, and it authorises no implementation, merge, deployment or live household change.

## Acceptance test catalogue
Require test cases for: identity/guest permissions; five-minute context reset; household entity rename resilience; heating override; EV charging policy; manual lighting; camera privacy; voice pipeline failures; model accuracy/calibration/drift; digital twin isolation; recommendation trust; cost calculations; audit/provenance; offline Proxmox/HA/network; approval replay; backup restoration uncertainty; notification dedup; resource exhaustion and owner stop requests.

## Formal requirement
**FR-OPT-READINESS-GATE-001:** Declan shall provide a versioned integrated acceptance and release-readiness safety case, mapping each PR #46 requirement to testable evidence, independent review, explicit owner risk acceptance and distinct release/deployment authorisation. **No acceptance report, green test suite or readiness score may automatically implement, merge, deploy or alter the household.**

---
**Cross-cutting:** Owner approval is always separate and action-specific. This is a complete structured specification checkpoint in the PR conversation, not a repository file change.



---

<a id="comment-6727714604"></a>

**Original checkpoint:** [PR #46 comment 6727714604](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714604)

# PR #46 — FR-OPT-CHANGE-IMPACT-001: Household Optimisation Change Impact Analysis and Dependency Safety

**Draft functional specification. Documentation only. No implementation, commits, merge, deployment or household changes.**

## 1. Objective
Before recommending any consequential household optimisation change, Declan shall analyse the proposed change's direct, indirect, cascading and reversible impacts across devices, schedules, people, infrastructure, privacy, costs and existing goals. Analysis is read-only and never executes a change.

## 2. Change proposal contract
Each proposal shall have an immutable ID and revision, requesting actor, intended objective, exact target entities/services, current and proposed settings, schedule, effective duration, assumptions, expected benefit, cost, model/version, evidence provenance, risk tier, affected owners and approval status. Missing parameters must be disclosed rather than inferred.

## 3. Dependency graph
Maintain a versioned, evidence-supported graph of HA entities, integrations, scripts, automations, helper entities, voice intents, network services, Proxmox VMs/containers, cloud providers, sensors, power dependencies and manual controls. Distinguish verified, inferred, stale and unknown links. A renamed entity must be treated as a potential breaking dependency, not silently mapped.

## 4. Impact dimensions
Assess functional behaviour; heating comfort and overrides; EV charging readiness and 50%-or-midnight owner choice; lighting scenes; media; security/cameras; occupancy and guests; network and compute resources; service continuity; cost in GBP; privacy and data transfers; accessibility; safety; maintenance and rollback. Identify cross-system and cross-goal interactions.

## 5. Direct and cascading effects
For each affected component, record triggering change, dependency path, predicted impact, evidence confidence, time horizon, severity, reversibility and potential propagation. Avoid treating correlations as proven causality. Detect loops, mutually exclusive automations, race conditions and timing-sensitive dependencies.

## 6. Baseline and scenarios
Compare status quo, proposed change, conservative alternative and credible adverse scenarios using consistent tariffs, weather, occupancy, model versions and time horizons. Report benefits separately from risks; quantify only where calibrated. Digital twin simulations are hypothetical and cannot replace real-world validation.

## 7. Safety and hard constraints
Reject recommendation eligibility when an action would violate physical safety limits, privacy restrictions, security boundaries, existing charging rules, heating safeguards, manual control availability, backup integrity or owner governance. A positive optimisation score cannot override hard constraints.

## 8. Uncertainty and incomplete topology
If relevant dependency evidence is missing, report a coverage gap and do not claim comprehensive impact analysis. Critical unknowns shall block a confident recommendation. Sensitivity tests should identify assumptions that materially change the conclusion.

## 9. Owner-facing preview
Provide plain-language summary: proposed action, why, affected systems, what remains unchanged, expected outcomes, worst plausible effects, confidence, alternatives, rollback feasibility and approval needed. Offer drill-down to dependency paths and exact entity IDs.

## 10. Approval boundaries
Analysis, simulation, recommendation, trial approval, software release approval and live execution are distinct. Approval must be owner-authenticated, exact-action, exact-target, time-bound and revocable where feasible. Changed parameters or newly discovered material impacts invalidate the prior request. No automatic HA calls, schedule edits, charging, restarts, purchases or deployments.

## 11. Change verification
If an independently authorised action later occurs, preserve before/after evidence, executor confirmation, measured outcome, side effects, failed expectations and owner review. Completion of a command is not proof of the intended benefit.

## 12. Audit and privacy
Store proposal revision, graph version, evidence timestamps, model versions, risk findings, owner challenges, approvals, changes and verified outcomes. Redact occupancy, security and infrastructure secrets; Guest Mode cannot approve or see restricted details.

## 13. Failure handling
Missing graph -> limited coverage; stale entity -> require confirmation; conflicting automations -> defer; simulation disagreement -> disclose; absent rollback -> flag high risk; audit/approval unavailable -> no action; monitoring outage -> no success claim.

## 14. Test matrix and acceptance
Test entity renames, Tuya command failures, shared lighting scenes, Hive overrides, EV charging schedules, simultaneous automation triggers, Proxmox resource pressure, camera/privacy effects, cloud outages, dependency cycles, missing data, contradictory owners, guest restrictions, simulated-vs-live isolation and approval replay. Acceptance requires an auditable, consequence-aware, dependency-grounded preview with no unapproved live actions.

## Formal requirement
**FR-OPT-CHANGE-IMPACT-001:** Declan shall perform read-only, evidence-based cross-system change impact and dependency safety analysis, identify cascading effects and uncertainty, present alternatives and owner-facing previews, and preserve auditable decisions. **No analysis or favourable simulation may independently authorise a household, infrastructure, financial or software change.**

---
This is a substantive specification checkpoint in the PR conversation, not a committed repository file. All consequential interventions require separately authenticated, explicit owner approval.



---

<a id="comment-6727714934"></a>

**Original checkpoint:** [PR #46 comment 6727714934](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714934)

# PR #46 — FR-OPT-EXPERIMENT-001: Household Optimisation Experimental Design and Outcome Verification

**Draft functional specification. Documentation only. No implementation, commits, merge, deployment or household changes.**

## 1. Objective
Define how Declan proposes scientifically credible, minimally disruptive experiments to test household optimisation hypotheses while keeping real-world trials, schedule changes and software deployment strictly owner-controlled.

## 2. Experiment registration
Every proposed experiment requires ID/version, hypothesis, owner, target outcome, current baseline, intervention, exact affected devices/services, duration, inclusion/exclusion conditions, safety constraints, risk classification, required approval, evidence sources and expected cost.

## 3. Outcome measures
Predefine primary and secondary metrics: comfort, energy, charging readiness, cost, service availability, latency, manual intervention, privacy and household satisfaction as applicable. Include units, collection method, thresholds, minimum detectable practical benefit, and uncertainty. Do not change primary success criteria after results are known without an auditable amendment.

## 4. Baseline and comparators
Use historical baselines, matched periods, within-household crossover or other appropriate comparison methods. Control for weather, occupancy, tariffs, seasonal changes, holidays, device condition and concurrent automation changes. Disclose when a randomised controlled comparison is impractical.

## 5. Bias and confounding
Address regression to the mean, selection bias, carryover effects, missing data, observer effects, small sample sizes and cherry-picked favourable periods. Record concurrent incidents and changes that could invalidate attribution. Avoid presenting association as causation.

## 6. Power and duration
Estimate necessary observation duration and uncertainty where feasible; avoid false precision with sparse household data. Short trials may support feasibility without demonstrating long-term benefit. Define a review date rather than silently extending experiments.

## 7. Simulation before trial
Use a read-only digital twin to screen feasibility, dependency conflicts, hard constraints and adverse scenarios. Simulations are not substitutes for owner consent or real outcome evidence.

## 8. Trial approval
Require explicit owner approval of exact intervention, devices, parameters, schedule, start/end, costs, rollback, notification plan and stop criteria. Permission to analyse or simulate is not permission to run a trial. Guest Mode cannot authorise trials.

## 9. Safety and stop rules
Specify measurable stop conditions for comfort deterioration, missed EV readiness, unexpected cost, service instability, sensor failure, privacy concerns or owner withdrawal. Existing independently approved safety protections remain in force. This specification does not itself authorise automated stopping actions or device control; any such mechanism needs separately reviewed policy and approval.

## 10. Data collection
Collect minimum necessary evidence with timestamps, provenance, quality flags and privacy controls. Preserve raw versus derived distinctions and the original hypothesis/analysis plan. Treat missing data as uncertainty, not successful outcomes.

## 11. Outcome analysis
Compare observed results with baseline, estimate effect size and uncertainty, evaluate adverse effects, and distinguish statistical detectability from household practical significance. Report failures and inconclusive findings equally visibly. Consider repeated trials and multiple-comparison bias.

## 12. Owner report
Explain what was tested, what actually changed, whether approval and execution were verified, observed outcomes, confidence, unexpected effects, limitations, cost, sustainability and recommended next step. No automatic permanent adoption of a successful trial.

## 13. Learning and promotion
Results may inform candidate model recalibration, recommendation trust, benefit forecasts and future trial design. New model versions require independent validation and controlled promotion; a positive trial result never authorises permanent schedule changes or deployment.

## 14. Audit and retention
Preserve preregistered protocol, consent, amendments, evidence, deviations, stop events, analysis code/version, owner feedback and final disposition. Retain sensitive occupancy and device records only under approved retention rules.

## 15. Failures
Insufficient data -> inconclusive; confounding -> qualified result; approval missing -> no trial; telemetry lost -> pause assessment and notify; unsafe proposal -> reject; changed intervention -> new approval; audit unavailable -> do not claim verified result.

## 16. Tests and acceptance
Test preregistration, baseline consistency, seasonality, confounders, sample-size limits, hypothesis changes, approval expiry, guest attempts, stop criteria, incomplete observations, model promotion boundaries, privacy, audit and non-execution. Accept only when experiment proposals are reproducible, risks disclosed, outcomes evidence-backed and live actions separately approved.

## Formal requirement
**FR-OPT-EXPERIMENT-001:** Declan shall support preregistered, evidence-based, owner-controlled household optimisation experiment planning and outcome verification with appropriate baselines, confounder controls, safety rules, uncertainty and audit. **No experiment proposal, simulation or positive result independently authorises trials, deployment or permanent household changes.**

---
This is a substantive specification checkpoint in the PR conversation, not a committed repository file. All consequential interventions require separately authenticated, explicit owner approval.



---

<a id="comment-6727715316"></a>

**Original checkpoint:** [PR #46 comment 6727715316](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727715316)

# PR #46 — FR-OPT-REVIEW-001: Household Optimisation Periodic Governance Review and Specification Closure

**Draft functional specification. Documentation only. No implementation, commits, merge, deployment or household changes.**

## 1. Objective
Provide a periodic, owner-led review of the household optimisation programme, covering the relevance of goals, validity of models, safety/privacy controls, costs, operational reliability, unresolved risks and the completeness of PR #46 documentation. This is a governance review, not autonomous policy amendment.

## 2. Review scope
Include goals, household routines, heating and EV constraints, lighting, security, media/voice, Proxmox/Frigate continuity, model registry, validation, monitoring, explanations, trust assessments, data lifecycle, consent, recommendations, incidents, experiments, benefits and technical debt.

## 3. Review triggers
Periodic owner-defined cadence plus event-driven reviews after material household change, new equipment, tariff change, safety incident, repeated model drift, cost overrun, validation expiry, privacy incident or significant dependency modification. Avoid unnecessary repetitive prompts.

## 4. Review pack
Generate a read-only evidence pack: versioned inventory, open decisions, overdue validations, unresolved alerts, verified outcomes, realised vs predicted benefits, actual vs estimated costs in GBP, risks, approval exceptions, backup/recovery evidence, resource budgets, evidence gaps and proposed actions.

## 5. Evidence status
Separate verified observations, supported estimates, hypothetical forecasts, owner reports, unknowns and disputed claims. Never infer health from absent alerts or infer successful implementation from documentation.

## 6. Owner priorities
Present competing household objectives and confirmed preferences; do not silently redefine goals. Any permanent change to comfort, charging, security, spending, retention or notification policy requires explicit scoped owner approval. Guests may not approve.

## 7. Review decisions
Classify each item: retain, investigate, gather evidence, revise draft, propose controlled trial, seek validation, request implementation, defer, reject or retire. Every decision shall include rationale, owner, scope, due date if chosen, dependencies and approval status.

## 8. Specification closure
Maintain a requirement inventory with statuses: drafted, reviewed, accepted for design, designed, implemented, tested, independently validated, owner-accepted, separately released, verified operationally. GitHub PR comments count only as documentation checkpoints, not repository commits, merged code or evidence of running functionality.

## 9. Gap and overlap assessment
Detect duplicate or conflicting FRs, undefined terminology, missing non-functional criteria, unowned requirements, untestable statements, contradictory permissions and outdated entity references. Propose harmonised wording and a traceability map without editing files or merging unless separately authorised.

## 10. Prioritisation
Rank proposed next steps by safety, household value, urgency, confidence, dependencies, effort, resource/cost, reversibility and owner preference. Hard constraints cannot be traded off against convenience. Routine recommendations share the three-per-week digest cap.

## 11. Accountability
Keep immutable review ID, date, participants/authorities, evidence snapshots, decisions, objections, unresolved issues, proposed requirement revisions and next review. Owner disagreement is not assumed resolved.

## 12. Approval and execution
Review acceptance does not authorise model training, deployment, software changes, HA service calls, schedule changes, purchases, backup operations or device actions. Explicit action-specific owner approval remains mandatory at each consequential gate.

## 13. Failure and degraded evidence
Missing telemetry -> report gap; expired model validation -> flag restricted trust; stale requirements -> mark review needed; absent owner -> defer decisions; approval unavailable -> no change; audit gap -> disclose limitations.

## 14. Tests and acceptance
Test requirement status accuracy, cross-reference integrity, duplicate/conflict detection, review triggers, verified-vs-hypothetical separation, owner disagreement, guest boundaries, cost accuracy, expiry, audit, notification limits and non-execution. Accept only when review outputs are understandable, traceable, actionable and clearly distinguish documentation from implemented behaviour.

## Formal requirement
**FR-OPT-REVIEW-001:** Declan shall support periodic, evidence-based owner governance and specification closure reviews with versioned requirement traceability, verified outcomes, risk/cost assessment, conflict detection, prioritised proposals and immutable decisions. **No review outcome or documentation sign-off grants automatic implementation, merge, deployment or household change authority.**

---
This is a substantive specification checkpoint in the PR conversation, not a committed repository file. All consequential interventions require separately authenticated, explicit owner approval.
