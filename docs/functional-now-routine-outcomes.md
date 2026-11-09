# NOW routine execution and outcome contract

**Status:** Draft for owner review. **Scope:** Documentation only; no Home Assistant configuration, integration code, permissions, or deployment are changed. This contract applies generically to routines selected from native Home Assistant scripts or automations, as required by FR-003, FR-004, and FR-007–009. Good Morning, Good Night, and Movie Time are examples for acceptance scenarios when configured by the owner; they are not a fixed list in Declan.

## Purpose

Declan must report what a selected Home Assistant routine actually did, with evidence and uncertainty, instead of treating a successful service call as proof that every action completed. Routine entities, action sequences, conditions, targets, and routine-specific requirements remain in Home Assistant. Declan invokes the user-selected HA entity and interprets the common result contract.

The existing owner-approved response direction is preserved: use concise, truthful outcome language and distinguish success, busy, failure, and uncertainty. This proposal adds an explicit partial outcome because the existing Movie Time handling distinguishes partial execution and NOW acceptance requires partial outcomes to remain visible. The result contract is generic and does not add routine names, entity IDs, automations, or action sequences to Declan's source.

## Governing Home Assistant configuration requirement

- FR-003 requires device control to use existing HA entities, exposed areas, services, and scripts. Declan must not silently create or replace household YAML or automations.
- FR-004 requires optional entity mappings to be configured and validated.
- FR-007–008 require portability, entity/area discovery, and native HA selectors sharing one authoritative persisted configuration.
- FR-009 requires configurable routines to route to user-selected native HA scripts or automations. Optional examples or blueprints must not be installed or enabled silently. Execution results follow FR-063 when approved.

Accordingly, Declan SHALL NOT contain hardcoded household entity IDs, routine names, script/automation IDs, action lists, or per-routine outcome mappings. The options flow and dashboard SHALL use native HA selectors and the authoritative HA integration configuration. If a legacy routine needs a wrapper to return a structured result, that wrapper SHALL be an owner-managed HA script or automation selected through the same configuration. Declan SHALL NOT generate or install it.

## R-NOW-ROUTINE-01 — Configured routine selection

A routine SHALL be eligible only when an administrator explicitly selects an existing HA script or automation using the native selector and the selected entity is available and valid for the configured role. Declan SHALL resolve and validate the selected entity through configuration; it SHALL NOT infer a routine from a display name, scan for similarly named automations and choose one, or fall back to another entity.

The set of configured routines SHALL be determined by HA configuration, not a fixed list in Declan. Missing, deleted, wrong-domain, disabled, or unavailable selections SHALL be reported clearly and SHALL NOT cause a guessed alternative to run. Any role-specific labels (for example, morning, bedtime, or movie mode) are configuration labels only; they SHALL map to an explicitly selected HA entity and SHALL NOT embed household action logic in Declan.

## R-NOW-ROUTINE-02 — Generic structured result record

Each configured routine invocation SHALL produce, or cause the selected HA routine to produce, a result record correlated to that exact invocation. Declan SHALL consume the same generic schema for every configured routine. It SHALL NOT use a household-specific adapter keyed by routine name or entity ID.

| Field | Requirement |
|---|---|
| `schema_version` | Version of the common result contract. |
| `request_id` | Unique identifier for this invocation, used to reject stale or cross-run results. |
| `routine_id` | The selected HA entity identifier used for this invocation, taken from validated configuration. |
| `outcome` | One of `success`, `partial`, `failed`, `busy`, or `unknown`. |
| `started_at`, `completed_at` | Timestamps when known; absence must not be filled with estimates. |
| `steps` | Per-step status and evidence produced by the HA routine, for its required and optional actions. |
| `reason_code` | Stable, non-sensitive explanation when the outcome is not success, where known. |

The selected HA routine SHALL identify any step, whether it is required, its result (`confirmed`, `failed`, `unknown`, or `skipped`), and evidence type and observation time where available. It MAY include a sanitized reason. It SHALL NOT include credentials, tokens, full provider error payloads, or private speech transcripts. Declan SHALL validate and interpret these fields generically without maintaining a separate step list or entity mapping for each household.

A service call being accepted is dispatch evidence only. If the selected routine does not return a valid, correlated result and completion cannot otherwise be established through the declared generic evidence contract, the outcome SHALL be `unknown`, not success. If an existing HA routine cannot return the common result, an optional HA-owned wrapper may be configured; absence of a wrapper does not justify a Declan-specific adapter.

## R-NOW-ROUTINE-03 — Outcome meanings

| Outcome | Required meaning |
|---|---|
| `success` | Every required step has evidence meeting the confirmation rule declared in the selected HA routine. Optional steps may be skipped only where that HA routine declares them optional. |
| `partial` | At least one required step is confirmed, and at least one other required step failed or remains unconfirmed. The result identifies affected steps where known. |
| `failed` | Execution is known to have failed and no required step is confirmed complete. A dispatch rejection before execution is a failure. |
| `busy` | The selected routine explicitly declined to start because it was already running or a declared concurrency condition prevented execution. No new run began. |
| `unknown` | A run may have started, but its final outcome cannot be established. Examples include timeout after dispatch, missing/malformed results, lost correlation, or unavailable verification. |

The step-level evidence SHALL distinguish:

- request or service dispatch accepted;
- HA routine-reported step completion;
- Home Assistant reported entity state observed after the action;
- requested content or target identity verified, where available;
- physical or audible completion, only when an independent sensor or provider explicitly reports it.

Home Assistant state is not physical proof. Declan SHALL describe the strongest evidence actually available and SHALL NOT imply that a dispatch proves a light changed, a projector opened, music became audible, or a speaker played requested content.

## R-NOW-ROUTINE-04 — HA-owned confirmation rules

Required and optional steps, action sequences, conditions, targets, and evidence needed for confirmation SHALL be defined in the selected HA routine or its HA-managed configuration. Declan SHALL NOT maintain a parallel routine definition or household-specific required-step list in integration source.

Each HA routine SHALL use a bounded observation period for any state verification it performs. The period SHALL be declared in HA configuration or the routine definition and SHALL NOT cause Declan's Assist response to wait indefinitely. The result record SHALL identify the evidence actually collected.

Where a target state already matches the requested state, the HA routine may report its step as confirmed only if its declared rule treats that state as sufficient. It must not claim the routine caused a new transition unless a transition was observed.

If result data conflicts with observed Home Assistant state, the affected step SHALL be treated as unconfirmed or failed according to the HA-declared rule; Declan SHALL report the conflict without choosing the more favourable result. If a configured confirmation source is unavailable, that step is `unknown`.

## R-NOW-ROUTINE-05 — Partial failures and skipped steps

The HA routine result SHALL preserve each required step's outcome. A successful routine-level result MUST NOT hide a failed required action. If some required steps complete and others fail or cannot be verified, report `partial` and identify the material incomplete steps where possible.

A skipped step is acceptable only if the HA routine declares it optional or its documented condition says it should be skipped. An unexplained skipped required step cannot be counted as success.

The routine's HA-defined action policy remains authoritative. This contract does not add retries, compensation actions, or rollback of completed household actions.

## R-NOW-ROUTINE-06 — Busy, timeout, duplicate request, and retry behaviour

A selected routine SHALL return `busy` only when it can establish that the new invocation did not start. If dispatch may have started but the result is absent, return `unknown`.

After `unknown`, Declan SHALL NOT automatically dispatch the same state-changing routine again. It SHALL explain that completion could not be confirmed and, where useful, offer a status check. A separately spoken retry is a new invocation and must be validated against current conditions; it must not be presented as continuation of the earlier run.

Results SHALL be correlated by `request_id`. A delayed result from an earlier run SHALL NOT overwrite or confirm a newer run. Duplicate Assist deliveries or arbitration retries SHALL NOT silently start duplicate routines.

## R-NOW-ROUTINE-07 — Speech, Stop, and delivery failures

The spoken response SHALL match the structured outcome:

- `success`: concise confirmation, only to the evidence level supported;
- `partial`: state that the routine partly completed and name unresolved material steps where known;
- `failed`: state that it failed without claiming completion;
- `busy`: state that it did not start because the routine was busy;
- `unknown`: state that it may have started but completion could not be confirmed.

The current Home/Guest personality may shape wording, but SHALL NOT alter the outcome, disclose private information to guests, or turn failures and uncertainty into jokes that obscure facts.

A Stop request SHALL stop speech according to the existing Stop behaviour. It SHALL NOT be described as cancellation of a running routine, reversal of completed steps, or proof that pending steps stopped. Cancellation of a routine is a separate capability and is outside this proposal.

Failure to synthesize or play the response SHALL NOT change the routine outcome. Routine execution status and response-delivery status SHALL be recorded separately where diagnostics are enabled.

## R-NOW-ROUTINE-08 — Missing or legacy result handling

If a selected HA routine returns no structured result, returns an invalid result, or uses an uncorrelated legacy response, Declan SHALL NOT infer success from the absence of an error. It SHALL use generic verified evidence only if the common contract defines that evidence; otherwise the final outcome is `unknown`.

If compatibility support is needed, an HA-owned wrapper may be configured through the native selector. Any wrapper SHALL be visible, owner-managed, and tested against the common result contract. It SHALL NOT be created, installed, or selected silently by Declan. Declan SHALL NOT contain routine-specific adapters or hardcoded references to household scripts and automations.

## Acceptance scenarios

Apply these scenarios to each routine selected in HA, including Good Morning, Good Night, or Movie Time only when the owner has configured those roles. The scenario suite SHALL obtain the active entity IDs from HA configuration; tests SHALL NOT rely on household IDs embedded in source. Record the parsed role, resolved configured entity, request ID, dispatch result, HA-produced result, relevant entity states before/after, spoken response, and response-delivery status. Remove secrets and private transcript material from retained diagnostics.

| ID | Scenario | Acceptance |
|---|---|---|
| AT-NOW-ROUTINE-01 | Each configured routine completes all HA-declared required steps with confirming evidence. | Correlated `success`; response matches observed evidence. |
| AT-NOW-ROUTINE-02 | A routine has confirmed required steps and a failed required step. | `partial`; completed and incomplete steps remain distinguishable. |
| AT-NOW-ROUTINE-03 | Dispatch is rejected before the routine starts. | `failed`; no success wording and no automatic retry. |
| AT-NOW-ROUTINE-04 | Routine explicitly declines a second invocation as already running. | `busy`; no second run is started. |
| AT-NOW-ROUTINE-05 | Dispatch is accepted, then the result times out or is unavailable. | `unknown`; no automatic redispatch and no success claim. |
| AT-NOW-ROUTINE-06 | The HA result reports success but required observed state contradicts it. | Conflict is surfaced; affected step is not counted as confirmed success. |
| AT-NOW-ROUTINE-07 | A delayed result for an earlier request arrives after a newer invocation. | Earlier result cannot confirm or overwrite the newer invocation. |
| AT-NOW-ROUTINE-08 | A required step is skipped without its HA-declared skip condition. | The routine cannot report `success`. |
| AT-NOW-ROUTINE-09 | Declan receives Stop while a routine is running. | Speech stops; Declan does not claim the routine was cancelled or roll back completed actions. |
| AT-NOW-ROUTINE-10 | Routine succeeds but TTS generation or playback fails. | Routine outcome remains `success`; response delivery is separately reported/diagnosed. |
| AT-NOW-ROUTINE-11 | Routine result is missing, malformed, or uncorrelated. | `unknown` unless a configured HA-owned wrapper or generic evidence supplies sufficient data; no inferred success. |
| AT-NOW-ROUTINE-12 | Guest Mode is on or unavailable during a routine outcome response. | Same factual outcome and privacy boundary; only permitted Guest wording is used. |
| AT-NOW-ROUTINE-13 | A household uses different entity IDs and different HA-selected routines from the reference household. | Configuration works through native HA selectors without editing Declan source or embedding household IDs. |
| AT-NOW-ROUTINE-14 | A configured entity is deleted, unavailable, disabled, or has the wrong domain. | Clear configuration/execution error; no guessed fallback and no unrelated routine runs. |
| AT-NOW-ROUTINE-15 | An optional HA-owned wrapper is selected for an existing routine. | Wrapper is visible in HA configuration, returns the same generic contract, and is not installed or enabled by Declan. |

Tests must include success, negative, timeout, partial, busy, malformed-result, stale-result, duplicate-delivery, missing-entity, alternate-household configuration, and response-delivery failure cases. Source implementation, CI, isolated tests, live verification, deployment, and owner approval remain separate status claims.

## Boundaries and unresolved decisions

- **Partially decided, not final schema approval:** existing decision notes approve truthful responses and propose `success/busy/failed/unknown`; this document proposes `partial` and the generic result fields above for review.
- **Routine selection and storage:** FR-007–009 define native HA configuration and user-selected scripts/automations. This contract adds no Declan-owned household routine registry.
- **Routine-specific steps and evidence:** defined in the selected HA routine or HA-managed wrapper, not hardcoded in Declan.
- **No implementation authority:** this specification authorises no code changes, HA configuration changes, merging, or deployment.

**References:** [FR-003–004 and FR-007–009](functional-requirements.md#portability-and-native-home-assistant-configuration-new-candidates-phase-1-audit); NOW MVP [run household routines](functional-now.md); archived baseline FR-022–023 and FR-063–064; Release 0.52.0 gap analysis [NOW-GAP-03](functional-now-release-052-gap-analysis.md); owner decision register [OD-04](functional-requirements-reconciliation.md#comment-6732459211).
