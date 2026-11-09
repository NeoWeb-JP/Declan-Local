# NOW routine execution and outcome contract

**Status:** Draft for owner review. **Scope:** Documentation only; no Home Assistant scripts, integration code, permissions, or deployment are changed. This specification defines the proposed result contract for the NOW MVP routines: Good Morning, Good Night, and Movie Time.

## Purpose

Declan must report what a routine actually did, with evidence and uncertainty, instead of treating a successful Home Assistant service call as proof that every action completed. The same contract applies across the three routines, while each routine retains its own steps and safety conditions.

The existing owner-approved response direction is preserved: use concise, truthful outcome language and distinguish success, busy, failure, and uncertainty. This proposal adds an explicit partial outcome because Movie Time already distinguishes partial execution and the NOW acceptance scenario requires partial outcomes to remain visible. It does not decide that other scripts or automations are in scope.

## R-NOW-ROUTINE-01 — Supported routine scope

For this NOW specification, the candidate covered routines are:

- configured Good Morning routine;
- configured Good Night routine;
- configured Movie Time start and end routines.

A routine is eligible only when it is explicitly configured and available. Declan SHALL NOT infer a script name, substitute another automation, or expand the covered set based on similar names. The owner must approve any additional scripts or automations before they are treated as part of this contract.

**Open owner decision:** FR-064 leaves the exact covered script set unresolved. The three routines above are proposed as the NOW MVP scope because they are already named in its acceptance scenario.

## R-NOW-ROUTINE-02 — Structured result record

Each execution SHALL produce, or be adapted into, a result record correlated to that exact invocation. The record SHALL contain:

| Field | Requirement |
|---|---|
| `schema_version` | Version of the result contract. |
| `request_id` | Unique identifier for this invocation, used to reject stale or cross-run results. |
| `routine_id` | Configured routine identifier, not a guessed display-name match. |
| `outcome` | One of `success`, `partial`, `failed`, `busy`, or `unknown`. |
| `started_at`, `completed_at` | Timestamps when known; absence must not be filled with estimates. |
| `steps` | Per-step status and evidence for required and optional actions. |
| `reason_code` | Stable, non-sensitive explanation when the outcome is not success, where known. |

Every step record SHALL identify the step, whether it is required, its result (`confirmed`, `failed`, `unknown`, or `skipped`), and the evidence type and observation time where available. It MAY include a sanitized reason. It SHALL NOT include credentials, tokens, full provider error payloads, or private speech transcripts.

A script that cannot return a native record MAY use a routine-specific adapter only when that adapter can correlate evidence to the invocation. A service call being accepted is dispatch evidence only. If execution or completion cannot be established, the outcome SHALL be `unknown`, not success.

## R-NOW-ROUTINE-03 — Outcome meanings

| Outcome | Required meaning |
|---|---|
| `success` | Every required step has evidence meeting that routine's declared confirmation rule. Optional steps may be skipped only where the routine declares them optional. |
| `partial` | At least one required step is confirmed, and at least one other required step failed or remains unconfirmed. The result identifies affected steps where known. |
| `failed` | Execution is known to have failed and no required step is confirmed complete. A dispatch rejection before execution is a failure. |
| `busy` | The routine explicitly declined to start because it was already running or a declared concurrency condition prevented execution. No new routine run began. |
| `unknown` | A run may have started, but Declan cannot establish its final outcome. Examples include timeout after dispatch, missing/malformed results, lost correlation, or unavailable verification. |

The step-level evidence SHALL distinguish:

- request or service dispatch accepted;
- script-reported step completion;
- Home Assistant reported entity state observed after the action;
- requested content or target identity verified, where available;
- physical or audible completion, only when an independent sensor or provider explicitly reports it.

Home Assistant state is not physical proof. Declan SHALL describe the strongest evidence actually available and SHALL NOT imply that a command dispatch proves a light changed, a projector opened, music became audible, or a speaker played the requested content.

## R-NOW-ROUTINE-04 — Confirmation rules

Each configured routine SHALL declare required and optional steps and the evidence needed to confirm each required step. The confirmation rule SHALL be specific enough to test and SHALL use a bounded observation period. The period must be configurable or defined per routine; it must not keep an Assist response waiting indefinitely.

Where the target state already matches the requested state, the routine may report success only if its contract defines that state as sufficient evidence for the step. It must not claim the routine caused a new transition unless a transition was observed.

If result data conflicts with observed Home Assistant state, the affected step SHALL be treated as unconfirmed or failed according to the declared rule; Declan SHALL report the conflict without choosing the more favourable result. If the configured confirmation source is unavailable, the step is `unknown`.

## R-NOW-ROUTINE-05 — Partial failures and skipped steps

The result SHALL preserve each required step's outcome. A successful routine-level result MUST NOT hide a failed required action. If some required steps complete and others fail or cannot be verified, report `partial` and identify the material incomplete steps where possible.

A skipped step is acceptable only if it is declared optional or its documented condition says it should be skipped. An unexplained skipped required step cannot be counted as success.

The routine's individual action policy remains authoritative. This contract does not add retries, compensation actions, or rollback of completed household actions.

## R-NOW-ROUTINE-06 — Busy, timeout, duplicate request, and retry behaviour

A routine SHALL return `busy` only when it can establish that the new invocation did not start. If dispatch may have started but the result is absent, return `unknown`.

After `unknown`, Declan SHALL NOT automatically dispatch the same state-changing routine again. It SHALL explain that completion could not be confirmed and, where useful, offer a status check. A separately spoken retry is a new invocation and must be validated against current conditions; it must not be presented as continuation of the earlier run.

Results SHALL be correlated by `request_id`. A delayed result from an earlier run SHALL NOT overwrite or confirm a newer run. Duplicate Assist deliveries or arbitration retries SHALL NOT silently start duplicate routines.

## R-NOW-ROUTINE-07 — Speech, Stop, and delivery failures

The spoken response SHALL match the structured outcome:

- `success`: concise confirmation, only to the evidence level supported;
- `partial`: state that the routine partly completed and name the unresolved material steps where known;
- `failed`: state that it failed without claiming completion;
- `busy`: state that it did not start because the routine was busy;
- `unknown`: state that it may have started but completion could not be confirmed.

The current Home/Guest personality may shape wording, but SHALL NOT alter the outcome, disclose private information to guests, or turn failures and uncertainty into jokes that obscure the facts.

A Stop request SHALL stop speech according to the existing Stop behaviour. It SHALL NOT be described as cancellation of a running routine, reversal of completed steps, or proof that pending steps stopped. Cancellation of a routine is a separate capability and is outside this proposal.

Failure to synthesize or play the response SHALL NOT change the routine outcome. Routine execution status and response-delivery status SHALL be recorded separately where diagnostics are enabled.

## R-NOW-ROUTINE-08 — Missing or legacy result handling

If a routine returns no structured result, returns an invalid result, or uses an uncorrelated legacy response, Declan SHALL NOT infer success from the absence of an error. It SHALL use verified step evidence only if a reviewed adapter exists; otherwise the final outcome is `unknown`.

Adapters SHALL be routine-specific, versioned, and tested against the actual script contract. An adapter SHALL NOT convert “service call accepted” into “all actions completed.” Existing HA scripts and helpers remain owner-managed; Declan SHALL NOT create or rewrite them under this specification.

## Acceptance scenarios

Each scenario SHALL be exercised through the configured Assist pipeline. Record the transcript, parsed routine, request ID, service dispatch result, structured or adapted result, relevant entity states before/after, spoken response, and response-delivery status. Remove secrets and private transcript material from retained diagnostics.

| ID | Scenario | Acceptance |
|---|---|---|
| AT-NOW-ROUTINE-01 | Each of the three configured routines completes all required steps with confirming evidence. | Correlated `success`; response matches observed evidence. |
| AT-NOW-ROUTINE-02 | A routine has confirmed required steps and a failed required step. | `partial`; completed and incomplete steps remain distinguishable. |
| AT-NOW-ROUTINE-03 | Dispatch is rejected before the routine starts. | `failed`; no success wording and no automatic retry. |
| AT-NOW-ROUTINE-04 | Routine explicitly declines a second invocation as already running. | `busy`; no second run is started. |
| AT-NOW-ROUTINE-05 | Dispatch is accepted, then the result times out or is unavailable. | `unknown`; no automatic redispatch and no success claim. |
| AT-NOW-ROUTINE-06 | The result reports success but required observed state contradicts it. | Conflict is surfaced; affected step is not counted as confirmed success. |
| AT-NOW-ROUTINE-07 | A delayed result for an earlier request arrives after a newer invocation. | Earlier result cannot confirm or overwrite the newer invocation. |
| AT-NOW-ROUTINE-08 | A required step is skipped without its documented skip condition. | The routine cannot report `success`. |
| AT-NOW-ROUTINE-09 | Declan receives Stop while a routine is running. | Speech stops; Declan does not claim the routine was cancelled or roll back completed actions. |
| AT-NOW-ROUTINE-10 | Routine succeeds but TTS generation or playback fails. | Routine outcome remains `success`; response delivery is separately reported/diagnosed. |
| AT-NOW-ROUTINE-11 | Routine result is missing, malformed, or from an unreviewed legacy script. | `unknown` unless a reviewed adapter supplies sufficient evidence; no inferred success. |
| AT-NOW-ROUTINE-12 | Guest Mode is on or unavailable during a routine outcome response. | Same factual outcome and privacy boundary; only permitted Guest wording is used. |

Tests must include success, negative, timeout, partial, busy, malformed-result, stale-result, duplicate-delivery and response-delivery failure cases. Source implementation, CI, isolated tests, live verification, deployment and owner approval remain separate status claims.

## Boundaries and unresolved decisions

- **Partially decided, not final schema approval:** existing decision notes approve truthful responses and propose `success/busy/failed/unknown`; this document proposes `partial` and the fields above for review.
- **Open scope decision:** whether scripts beyond Good Morning, Good Night and Movie Time are covered.
- **Routine-specific confirmation criteria:** required/optional step lists and evidence sources must be documented for each configured routine before it can claim `success`.
- **No implementation authority:** this specification authorises no code changes, HA configuration changes, merging, or deployment.

**References:** NOW MVP [run household routines](functional-now.md); archived baseline FR-022–023 and FR-063–064; Release 0.52.0 gap analysis [NOW-GAP-03](functional-now-release-052-gap-analysis.md); owner decision register [OD-04](functional-requirements-reconciliation.md#comment-6732459211).
