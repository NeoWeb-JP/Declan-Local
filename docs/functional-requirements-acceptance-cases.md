# PR #46: Post-migration reference audit and exemplar acceptance tests

**Draft documentation only.** Audited `docs/functional-requirements.md` at PR HEAD after the eight definition-ID renames. Test cases below are **specifications for future isolated tests, not tests executed or passing**.

## Inbound reference audit
Eight original IDs were ambiguous. The baseline's old-ID usages were checked as whole identifiers, not prefix matches (so `FR-045` does not match `FR-045CY`).

| Original ID | Remaining occurrences | Non-definition references | Resolution |
|---|---:|---:|---|
| FR-040 | 7 | 6 | Seven references to original context meaning, including corrected guest reference to FR-GUEST-040 |
| FR-041 | 4 | 3 | No remaining ambiguous references; original meaning retained |
| FR-042 | 1 | 0 | No remaining ambiguous references; original meaning retained |
| FR-043 | 1 | 0 | No remaining ambiguous references; original meaning retained |
| FR-044 | 1 | 0 | No remaining ambiguous references; original meaning retained |
| FR-045 | 1 | 0 | No remaining ambiguous references; original meaning retained |
| FR-045CY | 1 | 0 | No remaining ambiguous references; original meaning retained |
| FR-050 | 1 | 0 | No remaining ambiguous references; original meaning retained |

The Guest Mode handover reference in the baseline's conflict-reconciliation section was corrected from `FR-040` to `FR-GUEST-040`. **No other old-ID reference in the baseline was found to require changing.** External docs, PR comments and test files have not yet undergone exhaustive reference migration.

## Reusable acceptance-case templates
### AT-CONV-001: Speaker-scoped five-minute context
- **Fixture/trigger:** Recognised speaker A starts a command; speaker B speaks within five minutes; then A follows up.
- **Expected:** A follow-up resolves only A's valid context; B cannot access A's context; after five minutes ambiguity is clarified.
- **Forbidden:** No cross-speaker private detail, no guessing or stale execution.
- **Execution:** Not run; future test design only.

### AT-CONV-002: Multiple actions and partial failure
- **Fixture/trigger:** Three distinct HA actions; second simulated unavailable.
- **Expected:** Independent target resolution and per-action outcome; only successful actions claimed.
- **Forbidden:** No global success claim, no automatic unsafe retry.
- **Execution:** Not run; future test design only.

### AT-CONV-003: Delayed/conditional commands
- **Fixture/trigger:** Schedule action, simulate restart, change entity/permission before trigger.
- **Expected:** Durable authorised request, duplicate prevention and revalidation; reject unsafe stale target.
- **Forbidden:** No execution based on expired authority.
- **Execution:** Not run; future test design only.

### AT-GUEST-001: Guest Mode privacy and handover
- **Fixture/trigger:** Toggle guest helper; simulate visitor and owner presence.
- **Expected:** Only Guest Mode selects persona; automatic handover requires eligible state and consent.
- **Forbidden:** No private Home jokes in Guest Mode; no inferred guest owner authority.
- **Execution:** Not run; future test design only.

### AT-GUEST-002: Automatic handover ownership
- **Fixture/trigger:** Manually grant authority then simulate automatic eligibility loss.
- **Expected:** Only controller-owned changes reverted; manual grants preserved.
- **Forbidden:** No overwriting manually owned helper state.
- **Execution:** Not run; future test design only.

### AT-GUEST-003: Guest departure and owner welcome
- **Fixture/trigger:** Explicitly clear staying status; return owners.
- **Expected:** No departing-guest farewell; owner return response follows active persona and privacy.
- **Forbidden:** No unsolicited private speech to remaining guests.
- **Execution:** Not run; future test design only.

### AT-MEDIA-001: Playback verification
- **Fixture/trigger:** Request playlist with player unreachable after command dispatch.
- **Expected:** Report not started/unknown unless state verifies playback.
- **Forbidden:** No false claim that music is playing.
- **Execution:** Not run; future test design only.

### AT-MEDIA-002: Blacklist and positive weighting
- **Fixture/trigger:** Blacklist track then select category; positively rate playlist.
- **Expected:** Blacklisted track excluded; weights adjusted only with authorised feedback.
- **Forbidden:** No repeat of banned track or silent provider changes.
- **Execution:** Not run; future test design only.

### AT-ROUTINE-001: Machine-readable routine result
- **Fixture/trigger:** Simulate busy, failed, unknown, partial script outcomes.
- **Expected:** Correct distinct result and spoken summary with evidence.
- **Forbidden:** No success based on script dispatch alone.
- **Execution:** Not run; future test design only.

### AT-ROUTINE-002: Tuya partial failure
- **Fixture/trigger:** First light succeeds, second Tuya action rejects.
- **Expected:** Record partial state and stop unsafe retries; explain which actions succeeded.
- **Forbidden:** No automatic repeated state changes.
- **Execution:** Not run; future test design only.

### AT-VOICE-001: Voice entity availability
- **Fixture/trigger:** Configured STT/TTS unavailable; test isolated pipeline.
- **Expected:** Graceful truthful fallback/diagnostics according to approved provider policy.
- **Forbidden:** No fabricated fallback or paid generation.
- **Execution:** Not run; future test design only.

### AT-VOICE-002: Speaker identity authority
- **Fixture/trigger:** Speaker recognised but requests owner-only change.
- **Expected:** Identity may personalise but cannot itself authorise high-risk action.
- **Forbidden:** No privilege escalation.
- **Execution:** Not run; future test design only.

### AT-OPT-001: Read-only household scenario
- **Fixture/trigger:** Simulate heating, EV and lighting trade-offs with conflicting goals.
- **Expected:** Explain evidence, uncertainty, costs, dependencies and owner choices.
- **Forbidden:** No device changes or spending.
- **Execution:** Not run; future test design only.

### AT-OPT-002: Model drift and quality alert
- **Fixture/trigger:** Inject drift/accuracy degradation and resource pressure in isolated fixtures.
- **Expected:** Prioritised alerts, advisory eligibility restrictions and audit.
- **Forbidden:** No automatic model deploy, HA changes or service restarts.
- **Execution:** Not run; future test design only.

### AT-OPT-003: Owner approval state machine
- **Fixture/trigger:** Replay, revoke and expire proposal-bound approval.
- **Expected:** Reject reused/expired/mismatched approval; auditable outcomes.
- **Forbidden:** No consequential execution without fresh valid consent.
- **Execution:** Not run; future test design only.

### AT-GOV-001: Release evidence gate
- **Fixture/trigger:** Present spec-only requirement with no CI/live evidence.
- **Expected:** Gate remains blocked and distinguishes draft/implemented/verified/deployed.
- **Forbidden:** No release inferred from documentation.
- **Execution:** Not run; future test design only.

### AT-GOV-002: Privacy and retention
- **Fixture/trigger:** Simulate guest, owner and audit data retention requests.
- **Expected:** Correct scope, privacy, deletion restrictions and auditable decisions.
- **Forbidden:** No unauthorised exposure or silent audit deletion.
- **Execution:** Not run; future test design only.


## Acceptance evidence status
- 273 unique baseline definition IDs, with a proposed `AT-<requirement ID>` mapping in [traceability matrix](functional-requirements-traceability.md).
- 17 **illustrative cross-cutting acceptance cases** above; not 273 fully specified independent tests.
- FR-OPT modules in committed appendices need their own source-to-test links and concrete fixtures.
- Test isolation, owner approval, privacy, cost and non-production execution remain mandatory.

**No implementation, merge, deployment or Home Assistant changes.**