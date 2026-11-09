# PR #46: Optimisation module to acceptance evidence traceability

**Documentation-only draft.** This register lists independently headed PR #46 specification/checkpoint comments, including governance and audit checkpoints. A comment's presence in a committed appendix is **documented provenance**, not proof that every earlier conversation requirement or acceptance case is complete.

## Module/checkpoint inventory
| ID | Domain | Relevant baseline family (candidate, verify exact semantic link) | Proposed acceptance case | Evidence status | Original source |
|---|---|---|---|---|---|
| FR-OPT-VALIDATION-001 | Model assurance | FR-045*, FR-080–085 | AT-OPT-MODULE-001 | **Not specified/tested** | [PR comment 6727463290](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727463290) |
| FR-OPT-MODEL-GOV-001 | Model assurance | FR-045*, FR-080–085 | AT-OPT-MODULE-002 | **Not specified/tested** | [PR comment 6727483039](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727483039) |
| FR-OPT-MONITOR-001 | Model assurance | FR-045*, FR-080–085 | AT-OPT-MODULE-003 | **Not specified/tested** | [PR comment 6727547284](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727547284) |
| FR-OPT-EXPLAIN-001 | Model assurance | FR-045*, FR-080–085 | AT-OPT-MODULE-004 | **Not specified/tested** | [PR comment 6727561377](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727561377) |
| FR-OPT-TRUST-001 | Model assurance | FR-045*, FR-080–085 | AT-OPT-MODULE-005 | **Not specified/tested** | [PR comment 6727596152](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596152) |
| FR-OPT-DECISION-001 | Evidence and owner control | FR-031–043, FR-045*, FR-080–085 | AT-OPT-MODULE-006 | **Not specified/tested** | [PR comment 6727596493](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596493) |
| FR-OPT-DATA-LIFECYCLE-001 | Evidence and owner control | FR-031–043, FR-045*, FR-080–085 | AT-OPT-MODULE-007 | **Not specified/tested** | [PR comment 6727596846](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727596846) |
| FR-OPT-HUMAN-OVERSIGHT-001 | Evidence and owner control | FR-031–043, FR-045*, FR-080–085 | AT-OPT-MODULE-008 | **Not specified/tested** | [PR comment 6727597202](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597202) |
| FR-OPT-OPERATIONS-001 | Safety and resilience | FR-045*, FR-060–064, FR-080–085 | AT-OPT-MODULE-009 | **Not specified/tested** | [PR comment 6727597455](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597455) |
| FR-OPT-READINESS-GATE-001 | Delivery and acceptance | FR-083–085 | AT-OPT-MODULE-010 | **Not specified/tested** | [PR comment 6727597853](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727597853) |
| FR-OPT-CHANGE-IMPACT-001 | Safety and resilience | FR-045*, FR-060–064, FR-080–085 | AT-OPT-MODULE-011 | **Not specified/tested** | [PR comment 6727714604](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714604) |
| FR-OPT-EXPERIMENT-001 | Planning and optimisation | FR-045FW–FR-045GD and other FR-045* | AT-OPT-MODULE-012 | **Not specified/tested** | [PR comment 6727714934](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727714934) |
| FR-OPT-REVIEW-001 | Delivery and acceptance | FR-083–085 | AT-OPT-MODULE-013 | **Not specified/tested** | [PR comment 6727715316](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727715316) |
| FR-OPT-CONSOLIDATION-001 | Reconciliation and governance | FR-001–088, FR-GUEST-*, FR-MAINT-RECOVERY-001 | AT-OPT-MODULE-014 | **Not specified/tested** | [PR comment 6727739848](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727739848) |
| FR-OPT-CONTRACTS-001 | Evidence and owner control | FR-031–043, FR-045*, FR-080–085 | AT-OPT-MODULE-015 | **Not specified/tested** | [PR comment 6727758036](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758036) |
| FR-OPT-ROADMAP-001 | Delivery and acceptance | FR-083–085 | AT-OPT-MODULE-016 | **Not specified/tested** | [PR comment 6727758667](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727758667) |
| FR-OPT-OWNER-DECISIONS-001 | Evidence and owner control | FR-031–043, FR-045*, FR-080–085 | AT-OPT-MODULE-017 | **Not specified/tested** | [PR comment 6727777320](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727777320) |
| FR-OPT-MASTER-INDEX-001 | Reconciliation and governance | FR-001–088, FR-GUEST-*, FR-MAINT-RECOVERY-001 | AT-OPT-MODULE-018 | **Not specified/tested** | [PR comment 6727781069](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727781069) |
| FR-OPT-RECONCILE-001 | Reconciliation and governance | FR-001–088, FR-GUEST-*, FR-MAINT-RECOVERY-001 | AT-OPT-MODULE-019 | **Not specified/tested** | [PR comment 6727820375](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727820375) |
| FR-OPT-RECONCILE-002 | Reconciliation and governance | FR-001–088, FR-GUEST-*, FR-MAINT-RECOVERY-001 | AT-OPT-MODULE-020 | **Not specified/tested** | [PR comment 6727825353](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727825353) |
| FR-OPT-CROSSWALK-001 | Reconciliation and governance | FR-001–088, FR-GUEST-*, FR-MAINT-RECOVERY-001 | AT-OPT-MODULE-021 | **Not specified/tested** | [PR comment 6732456287](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6732456287) |
| FR-OPT-OWNER-DECISIONS-002 | Evidence and owner control | FR-031–043, FR-045*, FR-080–085 | AT-OPT-MODULE-022 | **Not specified/tested** | [PR comment 6732459211](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6732459211) |
| FR-OPT-TRACEABILITY-AUDIT-001 | Reconciliation and governance | FR-001–088, FR-GUEST-*, FR-MAINT-RECOVERY-001 | AT-OPT-MODULE-023 | **Not specified/tested** | [PR comment 6732486467](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6732486467) |

## Coverage interpretation
- **23 independently headed checkpoints** are indexed above. Grouped early checkpoints additionally mention more proposed modules than they fully specify in stand-alone form. Those need expansion and separate acceptance criteria, not automatic classification as complete.
- Each `AT-OPT-MODULE-...` is a **traceability placeholder** only. The [acceptance-case catalogue](functional-requirements-acceptance-cases.md) supplies 17 cross-cutting illustrative scenarios, but these are not one-to-one verified tests for every module.
- Candidate baseline families are navigation pointers, not proven semantic matches. Specific requirement IDs must be linked by human-reviewed evidence.
- Original [functional requirements](functional-requirements.md) and [optimisation appendices](functional-optimisation-requirements.md) / [governance appendix](functional-optimisation-governance.md) remain authoritative source text.
- For earlier ID collisions, use [the migration register](functional-requirement-id-migration.md).

## Required acceptance case shape
For each substantive requirement: **preconditions; actor and permission; trigger/input; evidence sources and freshness; normal expected outcome; negative and ambiguous outcomes; prohibited side effects; audit record; notification/quiet-hours treatment; resource and cost ceilings; test isolation; measurable pass/fail; rollback or recovery; source/PR revision; owner decision status.**

## Gaps requiring deliberate work
1. **Early grouped checkpoints:** unpack goal optimisation, policy assurance, risk forecasting, incident response, continuity, twin, strategic planning, research, benefits and portfolio management into uniquely numbered acceptance statements.
2. **Models:** concrete accuracy/drift thresholds, data sufficiency, confidence, provenance, alert priority and owner-approved remediation cases.
3. **Execution boundary:** distinguish safe read-only previews from consequential approvals, guest controls, scheduled commands and software deployment.
4. **Historical conversations:** full equivalence not yet verified; do not claim closure based on keyword presence.
5. **Evidence:** no passing CI, isolated, real HA, resource/cost or production verification supplied by this document.

**No implementation, merge, deployment, household or paid service changes authorised.**
