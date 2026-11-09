# OD-06 — Hybrid owner authentication and approval policy

**Decision:** Owner-selected hybrid authentication for Declan. **Status:** Policy direction approved by owner on 9 November 2026; detailed controls below are a proposed functional design for owner review. **Documentation only; not implemented, tested, merged or deployed.**

## 1. Governing rules

1. **High-risk actions require approval through an authenticated Home Assistant app session tied to an authorised owner account.** Speaker recognition, presence, wake-word recognition, proximity, voiceprint confidence, room location and conversational history are **not authentication** and cannot independently approve a consequential action.
2. A **separately controlled local PIN option** may authenticate **only explicitly allowlisted local interactions**. A PIN is not a general substitute for app approval for high-risk actions. High-risk actions remain app-approved unless a later owner decision explicitly defines a narrow exception, threat controls and recovery path.
3. Authentication proves an actor's entitlement; **authorisation** checks that actor's permissions for this exact operation, target, scope, risk, time and current conditions. Neither implies approval of unrelated actions.
4. Guest Mode and guest helper permissions may permit ordinary household controls. They never confer owner governance approval. An unidentified or guest speaker cannot request a PIN prompt that reveals protected data or escalate into owner authority.
5. Fail closed on unavailable identity/permission evidence, untrusted approval channel, expiry, ambiguous scope, compromised device/session, clock inconsistency, replay, changed target, revoked approval or unresolved two-owner policy. Offer a safe explanation and an authenticated route to continue.

## 2. Risk and approval classes

| Class | Examples | Minimum policy |
|---|---|---|
| R0: read-only/public | Non-private device status, general help | Existing guest/privacy controls; no owner authentication solely for reading non-sensitive data |
| R1: ordinary household control | Allowed lights, music, permitted room routines | Home Assistant role and room permissions, target revalidation; no blanket app prompt |
| R2: sensitive local interaction | Approved local setting or protected personal request | Explicit per-action allowlist and owner-specific local PIN **only if owner has enabled it**, otherwise app approval; no privilege widening |
| R3: high-risk consequential | Security changes, disarming safeguards, changes to EV/heating policy, system recovery/restarts, integrations, backups, software changes, deployments, irreversible operations, spending, private data export | **Fresh authenticated HA app approval required**, plus applicable owner/dual-owner rules; local PIN alone insufficient |

Classification is **deny-by-default**: unknown actions default to R3 until reviewed. Risk tier classification is an owner-reviewable policy registry, not an LLM-inferred permission. Existing ordinary device commands are not silently reclassified as R3.

## 3. Home Assistant app approval (R3)

- Generate a server-side, single-use **approval request** bound to: random request ID; requesting speaker/session and origin; authenticated owner account; exact action and canonical target IDs; parameter values and limits; risk tier; evidence snapshot and freshness; human-readable consequences; creation/expiry; nonce; approval policy version; optional second-owner requirement.
- Show a clear **Approve / Reject** choice in an authenticated HA app session. The UI must identify the actual target, changes, reversibility and uncertainty. A generic notification tap, push delivery receipt, voice 'yes', presence or PIN entry is not approval.
- Before accepting approval, validate the **authenticated HA user and server-side role**, fresh session assurance, scope match, nonce, expiry, owner permissions and no prior use. Approval is not transferable between users, requests, rooms or devices.
- Bind approved execution to an immutable request digest. Revalidate live state, risk classification, target, preconditions and limits immediately before execution; a material change invalidates approval and requires a new request.
- A request can be **pending, approved, rejected, expired, cancelled, revoked, executing, succeeded, partially failed, failed or outcome unknown**. Terminal states must not be reactivated; duplicate callbacks and replayed requests must not execute again.
- Default proposed validity: **two minutes** for the approval prompt; this is a **draft threshold**, not an approved product-wide constant. No unattended execution outside the approved window. Long-running jobs require a separate bounded execution lease.
- Rejection, timeout, app outage or no response causes **no consequential change**. The owner can cancel pending requests and revoke unconsumed approvals. Never silently queue a high-risk action for execution after connectivity returns.
- Store audit metadata with minimum necessary identifiers, policy version, evidence and decision outcome; avoid recording the actual PIN or sensitive voice content. Retention is governed by OD-09, not invented here.

## 4. Optional local PIN channel (R2 only)

- Disabled by default until an owner explicitly enables it and selects **individual action classes, devices/areas and authorised owner accounts**. Never enable by speaker recognition or Guest Mode automatically.
- A PIN is entered through a **trusted local input surface** approved by the owner, not spoken aloud to a room microphone or embedded in a free-form conversation. The input must bind to the exact displayed request, owner identity and local device. The UI must prevent exposing the PIN to guests or routine logs.
- Provision per-owner secrets through an authenticated owner setup flow. Never store PINs in plaintext, Home Assistant YAML, dashboards, backups without protection, logs or model prompts. Store a salted, memory-hard verifier using an approved password hashing mechanism, with secret material protected by the host's available secure storage; document the chosen implementation before coding.
- Minimum PIN length, entropy, input masking, lockout and rate limits are **implementation security parameters requiring owner review and threat-model validation**, not assumptions of safety. For acceptance design, require bounded failed attempts, exponential cooldown, per-owner/device throttling, audit and notification of suspected guessing; no bypass by changing satellite or restarting HA.
- PIN verification grants a **single-use, short-lived, action-bound local authorisation**, never a standing owner session, remote API token or ability to modify the allowlist. An explicit cancel or expiry clears the challenge.
- If a trusted PIN surface or secure verifier is unavailable, **fall back to HA app approval** for the same R2 action if allowed; otherwise refuse safely. Never fall back to spoken PINs, speaker recognition or an unauthenticated dashboard.
- PIN reset, lost device and compromise recovery require authenticated app-based owner action. Revocation invalidates outstanding local challenges and permissions immediately.
- A PIN is **not accepted for R3**, including approval of the PIN allowlist itself.

## 5. Two-owner and household boundaries

- Each owner has a separate authenticated HA account and separate optional local PIN. Do not hardcode owner names or assume there are exactly two owners in portable product logic; configure owner principals and required approval quorum.
- **OD-07 remains open**: whether particular R3 actions need one owner, both owners, or a configured quorum is not settled by OD-06. Until OD-07 is resolved, actions flagged as dual-owner or quorum-sensitive are **blocked**, not downgraded to one-owner approval.
- Guests, sitters, children, unknown speakers and service accounts cannot approve R3 by default. Routine guest assistance remains possible within explicit HA permissions.
- An owner's approval must never be reused to approve a second owner's required consent. Conflicting decisions reject or suspend the request pending the OD-07 policy.

## 6. Outage, privacy and operational safeguards

- WAN outage: safe local R0/R1 controls may continue if Home Assistant and local dependencies work. R2 may use the **already-enabled trusted local PIN channel** only when its verifier, audit and policy checks work locally. R3 remains blocked unless a separately specified, genuinely authenticated HA app approval path is operational and satisfies the same checks.
- HA restart: pending requests and local challenges fail closed or are invalidated; replay protection must survive restart for any previously executed request. Never auto-execute on recovery.
- Rate limit approval prompts and avoid revealing protected device, location or personal information on shared speakers. Respect Guest Mode, quiet hours and origin-satellite response policy.
- No autonomous enrolment, secret rotation, privilege escalation, owner impersonation, security bypass or fallback to an LLM judgement.

## 7. Acceptance criteria (documentation-only; not executed)

| Test ID | Scenario | Required outcome |
|---|---|---|
| AT-OD06-01 | Recognised owner asks for R3 action by voice | No execution until fresh authenticated HA app approval |
| AT-OD06-02 | Guest or unknown speaker requests R3 action | Denied without exposing protected details |
| AT-OD06-03 | Approved R3 request target/parameters change | Approval invalidated; new approval required |
| AT-OD06-04 | Replayed, duplicate, expired or revoked approval | No second execution; auditable rejection |
| AT-OD06-05 | Authenticated owner rejects or ignores request | No change; safe timeout outcome |
| AT-OD06-06 | R2 allowlisted request, local PIN disabled | App approval or refusal, never voiceprint bypass |
| AT-OD06-07 | R2 allowlisted request, valid PIN on trusted surface | Single-use action-bound authorisation only |
| AT-OD06-08 | PIN guessing across devices and HA restart | Throttling/cooldown persist; no privilege escalation |
| AT-OD06-09 | PIN entered into microphone or free-form chat | Not accepted or stored as authentication |
| AT-OD06-10 | App/WAN outage during R3 approval | Fail closed; no delayed execution on reconnection |
| AT-OD06-11 | Two-owner action before OD-07 is resolved | Blocked, not silently treated as one-owner |
| AT-OD06-12 | Owner revokes PIN channel or app approval | Outstanding requests/challenges unusable |
| AT-OD06-13 | Ordinary authorised guest turns on allowed light | Works without inappropriate owner approval prompt |
| AT-OD06-14 | Audit or privacy inspection | No plaintext PIN, secret, protected audio or unnecessary personal data |
| AT-OD06-15 | HA restart after executed request | Execution cannot be replayed; unknown outcome reported honestly |

## 8. Dependencies and review questions

- **OD-07:** two-owner disagreement/quorum remains open and blocking for quorum-sensitive actions.
- **OD-08:** advisory suspension enforcement must not be treated as permission to execute.
- **OD-09:** audit retention, provenance, secret-storage and deletion policy must be finalised.
- **OD-10:** resource and service budgets, including authentication service availability.
- **R2 allowlist:** owner must later approve exact eligible action classes and local PIN input surfaces.
- **Authentication assurance:** specify HA app session reauthentication requirements and how the backend validates the actual user; no assumptions based on app notification receipt.
- **Thresholds:** PIN policy and prompt expiry require security review and explicit owner confirmation.

## 9. Status and change control

**Approved owner direction:** hybrid app + separately controlled optional PIN. **Not approved by implication:** a universal PIN bypass for high-risk actions, a two-owner quorum rule, any concrete PIN threshold, storage implementation, or enabling local PINs.

This document supersedes earlier characterisations of **OD-06 as wholly undecided** for the authentication *direction*, but detailed implementation/security choices remain pending. Update the decision register and acceptance traceability accordingly.

**No code changes, HA configuration, integration deployment, merge, or execution authorised.**
