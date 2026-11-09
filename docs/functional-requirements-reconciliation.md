# Requirements index, reconciliation and owner decision registers

> **PR #46 draft, documentation only. Not approved for implementation, merge or deployment.**
>
> This file preserves the complete text of the cited PR conversation checkpoints, including their original caveats. Early grouped checkpoints are summaries of earlier conversations, **not verified verbatim transfers of every historical discussion**. Later reviews and decision corrections take precedence where they explicitly identify an earlier misclassification. No household action is authorised by this documentation.
>
> Existing baseline: [functional-requirements.md](functional-requirements.md). This appendix does not replace it.

## Source contents

- [GitHub comment 6727820375](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727820375) — PR #46 — FR-OPT-RECONCILE-001: Verified Repository-to-Discussion Reconciliation (Initial Pass)
- [GitHub comment 6727825353](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727825353) — PR #46 — FR-OPT-RECONCILE-002: PR HEAD Cross-File Consistency Check
- [GitHub comment 6732456287](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6732456287) — PR #46 — FR-OPT-CROSSWALK-001: Baseline-to-Optimisation Requirement Crosswalk and Decision Corrections
- [GitHub comment 6732459211](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6732459211) — PR #46 — FR-OPT-OWNER-DECISIONS-002: Annotated Owner Decision Register, Reconciled with Existing Baseline

---


---

<a id="comment-6727820375"></a>

**Original checkpoint:** [PR #46 comment 6727820375](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727820375)

# PR #46 — FR-OPT-RECONCILE-001: Verified Repository-to-Discussion Reconciliation (Initial Pass)

**Documentation-only review; no repository modifications, code, merge or deployment.**

## Sources actually inspected
- PR #46 changed filenames: README.md, docs/branding-declan.md, docs/declan-local-migration.md, docs/functional-requirements.md, docs/guest-persona.md, docs/legacy-jarvis-reference-audit.md.
- **PR HEAD**, via `refs/pull/46/head`: `docs/functional-requirements.md` (480,537 characters; 356 physical lines, including unusually long individual requirement lines), and `docs/legacy-jarvis-reference-audit.md` (19,344 characters). The latter enumerates 36 classified legacy-reference entries per PR description.
- **Default branch `main`**: README.md, docs/branding-declan.md, docs/guest-persona.md and docs/declan-local-migration.md. These default-branch versions **must not be treated as PR HEAD**; review the changed PR versions separately before declaring cross-file contradictions.
- Existing PR #46 conversation comments and owner decision/master index checkpoints.

## Confirmed content in PR HEAD functional-requirements.md
- The branch **does contain an extensive draft baseline**, not an empty placeholder: FR-001 onward, 105 distinct FR-style identifiers identified by a targeted token scan, with sections covering identity, personality/privacy, local commands, guest authority, music/media, routines/timers, speech, learning/resilience/governance, roadmap, conflicts and owner review.
- The file explicitly states **Draft 0.2, owner review, NOT approved**, distinguishes Source/Planned/Decision and cautions that repository implementation is not proof of live deployment.
- Explicit requirements already in the branch include five-minute rolling context (FR-031), speaker-specific cross-room context (FR-032), unknown-speaker room isolation (FR-033), corrections (FR-034), interruption (FR-035), controlled long-term learning (FR-036–038), proactive help (FR-039), restart context reset (FR-040), multi-action requests (FR-041), delayed commands (FR-042), conditional requests (FR-043), Guest Mode-only persona (FR-010–016), quiet-hour details (FR-017–019), and a draft routine outcome contract (FR-063).
- The document includes **owner-approved** policy text on quiet hours: default 23:00–05:00 local HA time, 25% temporary reply volume with restoration, local response at originating satellite, and master-bedroom Echo Show as the household's intended initial proactive announcement destination. These are not the same as a completed implementation.
- **No `FR-OPT-...` identifiers** were found in the targeted scan of the branch functional requirements file. Therefore the many new optimisation modules in PR comments are **not yet incorporated under their IDs into that main specification file**.
- The baseline notes a prior owner change disabling separate HA Wyoming entries and retaining a Declan Assist pipeline. This is a documented owner report, **not a live verification performed in this review**.

## Confirmed compatibility and migration concerns
- PR HEAD legacy audit warns that renaming identifiers without checking registry/persistent data/bridge clients is dangerous; it identifies conversation, STT, TTS, entity, storage, guest-authority, music and Wyoming speaker protocol dependencies.
- The default-branch branding document states that legacy Jarvis speech aliases are accepted and some internal IDs retained for compatibility. The owner decision on whether to continue aliases is still open in the consolidation register.
- Default-branch guest-persona text describes visitor/staying privacy and automatic handover; PR HEAD functional requirements describes Guest Mode-only persona selection and owner-approved overnight-staying behaviour. **A true contradiction assessment requires the PR HEAD version of guest-persona.md**, not the default-branch version alone.
- Default-branch README references a legacy HACS URL and compatibility guidance; PR description says README HACS URL is corrected in this PR. Do not raise this as an unresolved PR defect without inspecting the PR version.

## Reconciliation verdict
**Confirmed present in PR branch:** a substantial, detailed baseline of conversational, persona, music, guest, voice and household control requirements.
**Confirmed missing from the main baseline under their identifiers:** the recently drafted `FR-OPT-...` optimisation modules, currently recorded in PR discussion comments.
**Not yet verified:** complete sentence-by-sentence transfer of all earlier long-form planning conversation drafts; PR HEAD alignment of all six changed files; actual live HA configuration and installed bridge; all future acceptance cases.
**Therefore: no claim that the main document contains every requirement discussed.**

## Recommended documentation-only next steps
1. Fetch **PR HEAD versions** of all six changed files, not `main`, and compare consistency.
2. Build a line/FR-ID crosswalk from the main baseline to the optimisation comment index; mark present, partial, comment-only, conflicting, and unknown.
3. Extract exact owner-approved choices from FR-001–... before presenting the decision register, to avoid reopening already settled policies. Distinguish **approved behaviour** from unresolved **implementation mechanism**.
4. Prepare a proposed consolidated table of contents and versioned appendix for `FR-OPT-...` modules; do not commit it until the owner authorises documentation edits.
5. Require owner review before any statement of completeness or readiness.

## Formal requirement
**FR-OPT-RECONCILE-001:** Repository-level completeness claims must be supported by source-specific, ref-specific comparison and a traceable crosswalk. Comment-only requirements must remain visibly distinct from committed branch requirements. No documentation review authorises code or household changes.



---

<a id="comment-6727825353"></a>

**Original checkpoint:** [PR #46 comment 6727825353](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6727825353)

# PR #46 — FR-OPT-RECONCILE-002: PR HEAD Cross-File Consistency Check

**Documentation-only follow-up to FR-OPT-RECONCILE-001. No repository edits or live changes.**

## Verified sources
Fetched all **six** PR #46 changed files from the actual PR head ref `refs/pull/46/head`: README.md, docs/branding-declan.md, docs/declan-local-migration.md, docs/functional-requirements.md, docs/guest-persona.md and docs/legacy-jarvis-reference-audit.md. This resolves the earlier limitation where some contextual reads were from default-branch `main`.

## Findings
1. **Guest Mode persona alignment: PASS at documented policy level.** PR HEAD README and guest-persona.md both state that only Guest Mode selects Home/Guest persona, with privacy-safe Guest fallback when helper is unavailable. Visitor presence, staying status, owner presence, speaker identity and quiet hours do not directly select persona. Automatic handover may change the Guest Mode helper under its own rules. This aligns with functional requirements FR-010–016. No contradiction established from these docs.
2. **Quiet-hours personality: aligned at policy level.** PR HEAD guest-persona.md explicitly says quiet hours do not change Home/Guest personality; functional requirements FR-014, FR-017–019 describe volume, delivery, whisper behaviour and owner-approved future policy. **Implementation status and device-specific behaviour remain unverified.**
3. **HACS URL: corrected in PR HEAD README.** It uses `https://github.com/NeoWeb-JP/Declan-Local`. The old `NeoWeb-JP/jarvis-local` URL seen in `main` is not a current PR-head defect.
4. **Historical migration guide: clarified.** PR HEAD `docs/declan-local-migration.md` is titled `Historical migration: jarvis_local to declan_local`; do not treat historical instructions as a request to redo an already-completed migration.
5. **Branding/compatibility:** PR HEAD branding-declan.md acknowledges existing owner-renamed HA Jarvis references while still requiring actual ID verification before source default/unique ID changes. This is compatible with the PR-head legacy audit's non-destructive migration posture.
6. **Main requirements coverage:** `docs/functional-requirements.md` contains extensive FR-numbered baseline but no identified `FR-OPT-...` modules; newer optimisation requirements are still comment-only. This remains the main completeness gap.

## Outstanding verification
- This was a targeted cross-file policy and identifier check, **not a full sentence-level semantic diff** across all ~480k characters of the functional requirements file.
- No live HA registry, bridge installation, STT/TTS provider IDs, wake word, speaker recognition, automation or release status verified.
- Need source-to-target crosswalk for detailed earlier conversation requirements and comment-only FR-OPT modules.
- Need owner review of approval mechanisms, open decisions and eventual versioned file consolidation.

## Result
**No demonstrated PR HEAD contradiction** in the checked Guest Mode persona policy, quiet-hours persona boundary, HACS repository URL or historical migration designation. **Full requirements completeness remains unverified.** No code, merge, deployment, purchase or household change authorised.



---

<a id="comment-6732456287"></a>

**Original checkpoint:** [PR #46 comment 6732456287](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6732456287)

# PR #46 — FR-OPT-CROSSWALK-001: Baseline-to-Optimisation Requirement Crosswalk and Decision Corrections

**Documentation-only, read-only review of `docs/functional-requirements.md` at PR HEAD (`refs/pull/46/head`). No file edits, merge, implementation or deployment.**

## Verified baseline coverage
The main functional specification is substantial (about 480k characters) and has explicit owner-approved policies and some reported live verification. Its numbered baseline and PR-comment optimisation modules must remain **distinct but linked**.

| Existing baseline IDs | Established subject | New module cross-reference | Assessment |
|---|---|---|---|
| FR-001–009, FR-086–088 | Integration identity, configuration portability, migration, native selectors | FR-OPT-CHANGE-IMPACT-001, FR-OPT-ROADMAP-001 | Existing baseline, new change-impact depth comment-only |
| FR-010–020A | Guest/Home persona, quiet hours, whisper, privacy | FR-OPT-HUMAN-OVERSIGHT-001, FR-OPT-OWNER-DECISIONS-001 | Existing detailed owner policy; do not reopen approved defaults |
| FR-020–043 and additional conversation requirements | Intent parsing, five-minute context, corrections, multi-action, scheduling and conditional requests | FR-OPT-CONTRACTS-001, FR-OPT-E2E-TEST-001 | Baseline detailed; shared record/execution contracts comment-only |
| FR-046 and guest authority section | Guest control boundaries and handover | FR-OPT-HUMAN-OVERSIGHT-001 | Existing detailed baseline; avoid treating all guest controls as prohibited |
| FR-050–056 | Music Assistant/Spotify, discovery, feedback, blacklist and verified playback | FR-OPT-OPERATIONS-001, FR-OPT-E2E-TEST-001 | Existing baseline; new monitoring/test detail comment-only |
| FR-060–064 | Household status, routines, timers, script result contract | FR-OPT-CONTRACTS-001, FR-OPT-EXPLAIN-001 | Response policy partly approved, precise schema/scope still pending |
| FR-070–077 | Active voice/speaker/TTS components and planned provider changes | FR-OPT-OPERATIONS-001, FR-OPT-ROADMAP-001 | Some exact identifiers and live status recorded; distinguish source claims from independent verification |
| FR-080–085 | Learning, privacy, review, traceability, CI/live/release statuses | FR-OPT-DATA-LIFECYCLE-001, FR-OPT-READINESS-GATE-001 | Existing baseline, new specialised governance modules comment-only |
| No equivalent FR-OPT identifiers in baseline | Model registry, validation, drift, trust, explainability, risk, digital twin, ROI, portfolio, trials, cross-system optimisation | FR-OPT-VALIDATION-001 through FR-OPT-ROADMAP-001 and grouped checkpoints | **Comment-only under their FR-OPT IDs; requires future file consolidation** |

## Important corrections to earlier open-decision register
1. **OD-01 (voice IDs) is NOT wholly open in the branch documentation.** FR-077 records the owner's active Assist pipeline as `conversation.declan`, `stt.declan_wyoming_speaker_recognition`, `tts.declan_voice_manager`, with code cleanup pending PR #48. FR-070 also records active bridge configuration. Mark **documented owner-reported/live-verified-at-prior-time; revalidation needed before migration**, not “unknown”.
2. **OD-05 (quiet hours) is PARTIALLY DECIDED, not wholly open.** FR-017–019 record owner-approved default **23:00–05:00**, temporary **25%** volume with restoration, whisper-triggered quiet interaction, local direct-request replies and master-bedroom Echo Show as intended initial proactive destination. Remaining work: implementation design, edge cases, delivery escalation and acceptance.
3. **OD-04 (routine outcomes) is PARTIALLY DECIDED.** FR-063 records approved response style and proposed machine-readable `success/busy/failed/unknown` contract. FR-064 leaves scope of existing household routines as a decision. Do not discard approved semantics.
4. **OD-03 (Jarvis aliases):** baseline and branding docs describe compatibility; changing/removing aliases still needs an explicit owner decision.
5. **OD-06/07 (approval/authority):** existing FR-046 permits ordinary Guest Mode controls within configured HA permissions. The optimisation high-risk approval boundary must not incorrectly ban all ordinary guest assistance; distinguish allowed routine commands from consequential owner-only governance actions.
6. **FR-072–073:** the baseline documents owner-chosen future ElevenLabs-only synthesis changes pending PR #47. Do not treat older local TTS fallback notes as a definitive future policy without reconciling versions.
7. **FR-077:** records active identifiers and PR #48 work. Do not assert PR #48 merged or deployed merely because it is referenced.

## Required reconciliation status vocabulary
**In PR HEAD baseline; owner policy approved** / **In PR HEAD baseline; implementation pending** / **In PR HEAD baseline; reported live verified** / **In PR comment only** / **Needs design decision** / **Needs live revalidation** / **Conflicting** / **Superseded**. Each entry must include an exact source and time, not simply OPEN or DONE.

## Remaining tasks
- Parse the complete baseline requirement set and map each to an optimisation module without losing the original owner-approved wording.
- Reconcile the early detailed conversation drafts against both baseline and PR comments.
- Prepare a future versioned appendix or files for FR-OPT modules with exact acceptance tests and traceability.
- Reissue an **annotated** decision register reflecting decisions already made, rather than asking the owner to decide them twice.
- No automatic PR file changes, model implementation, HA action, merge or deployment.

## Formal requirement
**FR-OPT-CROSSWALK-001:** Maintain a source- and version-specific crosswalk between baseline FR identifiers and newer FR-OPT modules, preserving owner-approved choices, avoiding duplicated governance contracts and making comment-only requirements visible until transferred into versioned repository documentation.



---

<a id="comment-6732459211"></a>

**Original checkpoint:** [PR #46 comment 6732459211](https://github.com/NeoWeb-JP/Declan-Local/pull/46#issuecomment-6732459211)

# PR #46 — FR-OPT-OWNER-DECISIONS-002: Annotated Owner Decision Register, Reconciled with Existing Baseline

**Documentation-only correction/supplement to FR-OPT-OWNER-DECISIONS-001.** Checked PR HEAD `docs/functional-requirements.md` and changed documentation. This does not overwrite earlier comments, edit repository files, implement, merge or deploy.

## Status definitions
**Approved policy / implementation pending** = owner choice documented, not proof of running behaviour. **Documented live status / reverify** = earlier baseline records a live check, not a fresh production check. **Partially decided** = policy set but technical detail outstanding. **Open** = requires explicit owner choice. **Deferred** = not ready for decision. **Superseded** = prior question was answered by a later documented choice.

| Earlier ID | Corrected status | Grounded decision / outstanding question |
|---|---|---|
| OD-01 | **Documented live status / reverify** | FR-077 identifies `conversation.declan`, `stt.declan_wyoming_speaker_recognition`, `tts.declan_voice_manager`. FR-070 describes bridge configuration. Verify current state before any migration; do not ask owner to rediscover IDs already documented. |
| OD-02 | **Partially decided / reverify** | FR-070 and FR-077 describe the configured Wyoming speaker-aware bridge; confirm installation boundaries, separate integration release and dependencies before future design. |
| OD-03 | **Open** | Retain or retire legacy spoken Jarvis aliases; current docs describe support. |
| OD-04 | **Partially decided** | FR-063 approves response style and proposes `success/busy/failed/unknown`; FR-064 leaves which external scripts/routines participate unresolved. Define detailed structured execution/outcome contract. |
| OD-05 | **Approved policy / implementation pending; escalation open** | FR-017–019: 23:00–05:00, 25% temporary reply volume with restoration, whispered interactions quiet individually, local direct-request reply, master-bedroom Echo Show as intended initial proactive destination. Remaining: device edge cases and urgent escalation. |
| OD-06 | **Open** | Strong owner authentication for high-risk actions, exact risk tiers and enforcement point. Speaker recognition alone insufficient. |
| OD-07 | **Open** | Dual-owner conflict/authority policy for consequential changes. Do not infer consent. |
| OD-08 | **Open design** | How to restrict advisory eligibility safely without restarting, deploying or modifying household systems. |
| OD-09 | **Open design** | Canonical records, retention schedules and privacy/audit reconciliation; draft proposed under FR-OPT-CONTRACTS-001. |
| OD-10 | **Open design** | Resource budgets and isolated test environment; protect HA, Frigate and essential services. |
| OD-11 | **Open** | Implementation sequencing priorities after review; proposed roadmap is not approval. |
| OD-12 | **Open** | Which modules are accepted for design; PR remains Draft 0.2 owner-review. |
| OD-13 | **Policy recorded / verify implementation details** | One-hour manual heating override requirement; confirm exact schedule/override behaviour and target integration in future design. |
| OD-14 | **Policy recorded / verify implementation details** | EV: no automatic top-up solely below 50%; plug-in owner choice top to 50% or charge until midnight; verify stop logic and existing midnight/overnight scheduling. |
| OD-15 | **Policy substantially documented** | FR-010–016, FR-046 and guest authority section: Guest Mode-only persona, owner/guest boundaries and handover. Validate welcome/return specifics against detailed conversation drafts and acceptance tests. |
| OD-16 | **Policy substantially documented / implementation details open** | FR-050–056: household blacklist, positive weighting, Spotify discovery, playback verification; clarify exact scope, reversal UX and provider availability. |
| OD-17 | **Open verification task** | Detailed conversation drafts, PR comments and PR HEAD baseline not yet proven completely reconciled. |

## Additional owner-approved decisions not to reopen casually
- FR-020A: frustration/troubleshooting does not silently reduce sass; serious facts and failures remain accurate.
- FR-031–033: rolling five-minute context, recognised-speaker cross-room isolation, unknown-speaker satellite isolation.
- FR-034–043: corrections, interruption, controlled preference learning, proactive suggestions, restart reset, multi-action, delayed and conditional commands with documented authorisation boundaries.
- FR-072–073: owner-chosen future ElevenLabs-only synthesis changes pending separate PR #47, distinct from older current/fallback implementation.
- FR-077: current voice entity IDs and separate pending PR #48 cleanup.
- FR-083–085: explicit requirement tests, separate CI/live/deployed statuses and owner approval for release.

## Recommended first owner review later
**Decide only genuinely open matters**: high-risk authentication and two-owner conflict policy (OD-06/07); legacy alias future (OD-03); advisory eligibility suspension enforcement (OD-08); scope of routine result contract (OD-04). Technical schema and resource choices can be proposed for review without requiring immediate owner decisions.

## Acceptance
Future decision summaries must cite exact FR IDs, show source/version and distinguish approved behaviour, implementation status, verification and unresolved mechanisms. No unanswered question may be silently converted to consent.

**No household, software, security, financial or deployment changes authorised.**
