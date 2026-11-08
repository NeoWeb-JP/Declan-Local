# Declan functional specification and roadmap

**Draft 0.2 — for owner review, NOT approved.** Source: `main` after PR #45 merged, 8 November 2026. This document defines the candidate requirements baseline and planned direction. No code change or live HA deployment is authorised by approving a document PR alone.

**Status key:** **Source** = implemented in repository, subject to test/live verification; **Planned** = proposed future behaviour; **Decision** = requires explicit owner agreement. An implemented module does not prove it is deployed, configured or working in the household.

## 1. Product, identity and configuration

- **FR-001 [Source]** Home Voice Assistant shall register with Home Assistant under the `declan_local` integration domain and expose a conversation agent, settings and administrator panel.
- **FR-002 [Source]** The assistant shall be called Declan. Its personality and display branding shall be distinct from stable HA entity IDs and storage identifiers.
- **FR-003 [Source]** Device control shall use existing HA entities, exposed areas, services and scripts; it shall not silently create or replace household YAML or automations.
- **FR-004 [Source]** Optional mappings for switches, satellites, music players, car sensors, thermostat, weather and guest helpers shall validate entity type and configured availability.
- **FR-005 [Decision]** All remaining Jarvis references shall be reviewed using [the audit](legacy-jarvis-reference-audit.md), not assumed necessary for compatibility. The owner reports that all live HA Jarvis references have already been renamed.
- **FR-006 [Planned]** Future migrations shall preserve settings, voice caches, speaker profiles, learning history and guest-authority ownership, with upgrade/rollback tests.

### Portability and native Home Assistant configuration (new candidates; Phase 1 audit)

- **FR-007 [Planned]** A clean HA installation shall be able to configure Declan without editing integration source code or inheriting another household's person, camera, device, network or script identifiers. Missing optional features shall not block core setup.
- **FR-008 [Planned]** Declan shall discover available HA entities/areas and offer native HA selectors for mappings. The native options flow and Declan dashboard shall share one authoritative persisted configuration, with validation and clear missing-entity handling.
- **FR-009 [Planned]** Declan shall route configurable routines to user-selected native HA scripts or automations; optional examples/blueprints shall not be installed or enabled silently. Execution results shall follow FR-063 when that contract is approved.
- **FR-086 [Planned]** Declan shall support versioned configuration export/import with schema validation, dry-run preview, entity remapping, explicit conflict approval and rollback. Default exports shall exclude credentials, tokens, speaker biometrics, private learning evidence and personal playback history.
- **FR-087 [Planned]** Persisted storage and registry migrations shall be idempotent and non-destructive, retaining legacy reads until verified. A clean install and an upgrade from an existing household shall both pass acceptance tests.
- **FR-088 [Planned]** Optional integrations (cameras, Frigate, Music Assistant/Spotify, EV, guest helpers) shall be individually configurable and safely unavailable when absent.

**Evidence:** [Phase 1 portability audit](portability-hardcoded-values-audit.md) is an initial targeted scan on `main`; full repository coverage and acceptance tests remain open. Settings dashboard work is separate draft PR #49; portability audit is draft PR #50. These requirements are proposed, not approved or implemented.

## 2. Personality and privacy

- **FR-010 [Source]** **Only Guest Mode selects the persona**: `off` = savage Home; `on` = playful Guest; missing/unknown/unavailable = privacy-safe Guest.
- **FR-011 [Source]** Visitors, speaker identity, owner presence and quiet hours shall not directly choose a persona. **Owner-approved change:** a confirmed overnight-staying declaration shall enable the configured Guest Mode helper, which then selects the Guest persona; the declaration itself does not become an independent persona selector. Automatic handover may also change the helper under its own eligibility rules.
- **FR-012 [Source]** Home speech may include strong personal banter for Jaco and Edd; Guest speech may roast visitors lightly but shall avoid private host details, intimate jokes and personalised host greetings.
- **FR-013 [Source]** Serious safety, security, medical, operational failure and factual messages shall be clear, accurate and not replaced by jokes.
- **FR-014 [Source]** Quiet hours shall not turn off sass or override Guest Mode. Any volume/delivery policy shall be defined separately.
- **FR-015 [Source]** Confirmations, social greetings, corrections, clarification and cached category alternatives shall respect the effective Guest/Home persona, without changing the factual outcome or exposing private Home audio in Guest Mode.
- **FR-016 [Source]** Speaker identity may personalise suitable Home greetings, but shall never confer permissions or independently select persona.
- **FR-017 [Owner-approved policy; implementation pending]** During configurable quiet hours, Declan shall lower spoken output volume and shorten non-critical responses while retaining the persona selected solely by Guest Mode. Quiet-hours settings shall default to **23:00–05:00 local Home Assistant time** (crossing midnight), while allowing the user to edit the schedule, reduced volume and concise-response policy. **Owner-approved default quiet reply volume: 25%**, configurable per installation. Before applying a temporary quiet reply volume, capture the originating output player's current volume and restore that previous value after the response finishes, including on error or cancellation where technically possible; do not overwrite a volume change made by the user in the meantime. Define safe behaviour for players that cannot report/set volume, overlapping playback and announcements during implementation. Safety-critical information must remain clear and audible; exact defaults and volume restoration behaviour require implementation design and tests.
- **FR-019 [Owner-approved behaviour; feasibility pending]** When the originating voice input is reliably detected as whispered, Declan shall treat **that interaction** as quiet regardless of the clock: reply locally at reduced volume and with a shorter non-critical response, without changing the configured quiet-hours schedule, global announcement routing, or Guest/Home persona. Whisper detection must use an explicit, tested signal or classifier with a confidence threshold; do not infer whispering merely from low microphone amplitude, which varies with distance, microphone gain and noise reduction. If whisper detection is unavailable or uncertain, fall back to the ordinary schedule and local reply policy. Do not persist quiet mode beyond the interaction solely because of a whisper. Safety-critical responses remain intelligible. Detection approach, thresholds and device support are implementation decisions.
- **FR-018 [Owner-approved policy; implementation pending]** Quiet-hours proactive announcements and broadcast responses shall be restricted to a user-configurable allowlist of one or more Home Assistant announcement-capable media players/Shows. For the owner’s household, the intended initial selection is the **master-bedroom Echo Show only**; this is a household setting, never a hardcoded default for other installations. Settings shall offer native HA device/entity selection, validate availability, and avoid silently rerouting to unselected devices. The policy applies only to proactive/unsolicited announcements and broadcasts. **Owner-approved direct-request exception:** a voice request made at any Assist satellite during quiet hours shall receive its spoken response locally at that originating satellite, at reduced quiet-hours volume, rather than being redirected to the announcement allowlist. Direct requests shall remain usable in other rooms; the announcement allowlist must not suppress or reroute their local replies. Empty or unavailable allowlists must fail safely without broadcasting house-wide.

## 3. Local command interpretation and actions

- **FR-020 [Source]** Commands shall be parsed and validated before actions; unknown or ambiguous devices shall not be guessed.
- **FR-021 [Source]** Lighting, brightness, areas and configured switch-as-light aliases shall support room-aware commands and bounded follow-ups.
- **FR-022 [Source]** Good Morning, Good Night and Movie Time shall invoke the corresponding configured HA routines when available.
- **FR-023 [Source]** Movie Time responses shall distinguish confirmed action from unknown/unconfirmed outcome; no false claim of projector success.
- **FR-024 [Source]** In-sentence corrections shall execute only the final validated request, not superseded commands.
- **FR-025 [Source]** Follow-up references shall be conversation-scoped, time-bounded and revalidated.
- **FR-031 [Owner-approved policy; implementation pending]** Declan shall retain active conversational context for **five minutes after the most recent interaction** in that conversation, resetting the inactivity timeout on each subsequent interaction. Within that window, context may resolve relevant follow-up references (for example, “turn on the lounge lights” followed by “actually, dim them to 30%”), provided the referent remains unambiguous and the target and action are revalidated before execution. After five minutes without an interaction, the active context shall expire; Declan must not silently apply expired context to a new request. Context retention shall not grant permissions, override Guest Mode privacy restrictions, or bypass command validation. Context scope across rooms/speakers, persistence across restart, and long-term learning remain separate decisions. Add acceptance tests for follow-ups within the window, inactivity expiry, timeout reset, ambiguous references and security boundaries.
- **FR-026 [Source]** Previews shall be side-effect-free; incomplete or unsafe requests shall run nothing.
- **FR-027 [Source]** Unsupported single requests may fall back to built-in HA conversation without recursion; only confirmed success may be reported as success.
- **FR-028 [Source]** Stop requests shall target the media player explicitly mapped to the originating satellite and avoid guessed destinations or spoken confirmations.
- **FR-030 [Owner-approved requirement; implementation pending]** Declan shall treat incidental punctuation in recognised/transcribed voice commands as insignificant for intent matching. For example, `Play, country music` and `play country music` shall resolve to the same music-play intent, subject to identical authorisation, target resolution and validation. Command normalisation shall be case-insensitive where appropriate and tolerate commas, full stops, question marks and similar transcription punctuation without changing meaningful words, quoted values, entity identifiers or structured arguments. Punctuation removal must not join words, create new commands, or bypass security checks; preserve the original utterance for diagnostics. Add regression tests for equivalent punctuated/unpunctuated commands across music, device control and routines, plus tests for punctuation-sensitive values.
- **FR-029 [Planned]** Generate a machine-readable command/phrase catalogue linked to parser branches, scripts and regression tests.

## 4. Guest handover and authority

- **FR-040 [Source]** Staying declarations, manual guest handover, status and cancellation shall remain separate from the personality selector. A confirmed overnight-staying declaration now enables the existing Guest Mode helper for privacy-safe speech, but **does not grant guest authority**, populate the names-in-charge helper or invoke a manual/automatic handover.
- **FR-047 [Owner-approved policy; implementation pending]** On an explicit, confirmed declaration that named guests are staying overnight (for example, “Mike and Kathy are staying with us”), Declan shall record the staying guests using the configured staying helpers and **automatically turn on Guest Mode** so the Guest persona and privacy safeguards apply immediately, even while owners are home. This action shall not authorise guests, populate or overwrite the names-in-charge helper, trigger an authority handover or weaken restricted-action policies (FR-046). Track whether Guest Mode was enabled by the staying declaration so that clearing staying guests can release only that declaration-owned change; never switch off Guest Mode that was independently enabled or is still needed by an active manual/automatic handover. Preserve ownership across restart and failed helper writes, and require explicit owner-approved semantics for overlapping causes before implementation. Unavailable helpers must fail safely and be reported without claiming success.
- **FR-048 [Owner-approved policy; implementation pending]** Overnight guest-staying status shall remain active until an **explicit user command** clears it (for example, “guests have left” or “Mike and Kathy have gone home”). Declan shall not infer departure or automatically clear staying guests based on time, overnight expiry, presence detection, owner return or absence of activity. Upon an explicit clear, remove the applicable staying declaration and release only the Guest Mode activation owned by that declaration, preserving Guest Mode if independently enabled or still required by an active handover. Clearing staying status shall not silently cancel a separately established manual handover; use the existing explicit handover-cancellation command for that. Resolve ambiguous partial departures before clearing all guests, and report helper failures without claiming successful clearance.
- **FR-049 [Owner-approved policy; implementation pending]** When an explicit manual guest handover is successfully confirmed (for example, “We're going out and Mike and Kathy are in charge”), Declan shall welcome the named guests, briefly confirm that they are in charge of ordinary household controls, and explain in friendly terms that he is available to help while security-sensitive actions, private household information and configuration remain restricted (FR-046). The welcome shall use the privacy-safe Guest persona with playful, mildly reluctant humour, such as: “Welcome, Mike and Kathy. I'm here if you need a hand with the house, although I was rather hoping for a break myself. Lights, music and the usual comforts are yours to command; security and private matters are staying off the menu.” Exact wording may vary to avoid repetition, but must remain warm, concise and guest-appropriate. Speak this welcome only once per successful handover, not on repeated status queries, reconciliation or restart; never claim handover succeeded if helper writes failed. Use an appropriate available announcement destination under the configured delivery and quiet-hours policies, without broadcasting to unselected devices. Do not expose private host details or imply guests can operate restricted functions.
- **FR-050 [Owner-approved policy; implementation pending]** Declan shall **not** give departing guests a farewell announcement when the owner explicitly clears their staying status or turns off Guest Mode. Instead, once guests have left and Guest Mode is off, Declan may give the returning owners a short, deliberately rude/savage but affectionate **welcome-home** response in the Home persona when an actual owner homecoming is detected or an explicit welcome-home interaction occurs. Example: “Oh, you're back. There goes the peace and quiet. I was just starting to enjoy having competent company.” Vary wording and avoid repetitive announcements; do not trigger a welcome-home speech solely because a guest declaration was cleared, or falsely claim an owner has arrived. Honour quiet hours, configured announcement destinations and speech privacy. Do not expose private jokes or host details while Guest Mode remains on. Exact trigger and deduplication rules remain implementation decisions.
- **FR-041 [Source]** Automatic handover shall remain opt-in and require healthy distinct helpers, confirmed staying guests and both owners `not_home` for at least 120 seconds.
- **FR-042 [Source]** The automatic controller shall copy authorised guest names, raise the dedicated away-simulation suspension signal and enable Guest Mode, rechecking eligibility between writes.
- **FR-043 [Source]** On owner return or loss of eligibility, only automatically owned authority and suspension changes shall be revoked; manual handover shall survive.
- **FR-044 [Source]** Restart/reconfiguration shall preserve ownership provenance and avoid deleting manually set authority.
- **FR-045 [Decision]** The external occupancy-simulation automation must independently respect the suspension helper; verify this in the live HA configuration.

- **FR-046 [Owner-approved policy; implementation pending]** Guest Mode shall permit ordinary household controls, including lights, music, television/media, heating and ordinary routines, subject to existing Home Assistant permissions and configured device availability. Guest Mode shall **not** by itself authorise security-sensitive actions, access to private or sensitive household information, or changes to Declan/Home Assistant settings. Security controls, sensitive information and configuration changes shall remain restricted; an explicit guest handover shall not implicitly override those restrictions. Guest Mode selects persona/privacy policy, while guest authority and any future per-action authorisation remain separate concerns. Enforcement, trusted-user identification and acceptance tests are future implementation work; this requirement does not assert that access control is already enforced.

## 5. Music and media

- **FR-050 [Source]** Music playback shall use configured Music Assistant players and Spotify playlist URIs, with category, artist/title, room, transport and volume handling where supported.
- **FR-051 [Source]** Playlist selection shall avoid unnecessary repetition and preserve favourites, exclusions, feedback weights and history.
- **FR-052 [Source]** Spotify discovery shall support configured categories, bounded selection, manual refresh and weekly scheduled refresh; discovery results are not guaranteed accurate.
- **FR-053 [Source]** A household-wide blacklist shall prevent repeat selection of banned tracks and skip detected excluded tracks where possible.
- **FR-054 [Source]** A request-dispatched acknowledgement shall not claim music has begun unless playback was verified.
- **FR-055 [Source]** Media search shall distinguish HA/Jellyfin/local results from streaming-catalogue listings; search does not automatically start a film or guarantee subscription availability.
- **FR-056 [Planned]** Provide consistent playback outcome/health telemetry for voice feedback and troubleshooting.

## 6. Information, routines and timers

- **FR-060 [Source]** Status, weather, forecast, time, climate and car responses shall be derived from current configured HA data and indicate unavailable data rather than invent it.
- **FR-061 [Source]** Contextual follow-up questions shall reuse bounded context and refresh current facts.
- **FR-062 [Source]** Timers shall be associated with the originating satellite when known and validate requested durations.
- **FR-063 [Planned; response policy approved]** HA scripts invoked by Declan shall return a standard machine-readable result: `success`, `busy`, `failed`, `unknown`, action type and safe spoken summary. For **confirmed successful** routines, Declan shall give a **short, personality-driven confirmation** consistent with the effective Home/Guest persona and privacy rules. For **partial failures**, Declan shall give a **short spoken warning** without claiming complete success, and record actionable failure details in diagnostics. An unconfirmed or unknown outcome must not be presented as success. The exact result schema, diagnostics fields and script coverage remain implementation/review items; this approval does not mean the behaviour is implemented or verified.
- **FR-064 [Decision]** Agree which existing household routines are in scope for this script-response contract and which remain external HA-managed features.

**Owner decision (2026-11-08):** Routine success speech is concise and personality-driven, respecting Guest Mode. Partial failures receive a brief warning; technical details belong in diagnostics, not the spoken response. This is a specification decision only, not a claim of live implementation. Acceptance tests must cover confirmed success, partial failure and unknown outcomes, including truthful spoken status and diagnostic capture.

## 7. Speech, speaker identity and TTS

- **FR-070 [Source; live configuration verified]** Declan shall use its active Assist speech entities and configured Wyoming speaker-aware bridge. Live options point to `192.168.0.43:10301`; OpenAI STT is enabled with model `gpt-transcribe`. The bridge's downstream dependencies have not been established.
- **FR-071 [Source]** Speaker recognition shall not be used as authentication and shall avoid guessing unknown speakers.
- **FR-072 [Decision; pending PR #47]** Voice Manager shall cache ElevenLabs audio by exact synthesis identity and retain phrase assembly and cached category alternatives. The owner has chosen to remove the secondary TTS provider; PR #47 proposes the implementation.
- **FR-073 [Decision; pending PR #47]** ElevenLabs shall be the sole synthesis provider. Existing exact cached audio may be reused; where configured, an approved cached category alternative may be used after primary generation fails. If no suitable cache entry exists and ElevenLabs is unavailable or blocked by a configured allowance, speech generation shall fail clearly, without trying a secondary provider.
- **FR-074 [Source]** Static catalogue generation shall require review and explicit approval; cache hits shall not trigger unnecessary paid generation.
- **FR-075 [Source]** Persistent daily usage counters are local estimates/guards, not the provider's authoritative billing.
- **FR-076 [Planned]** Speaker gateway and camera-assisted identification shall have separately versioned acceptance tests for microphone quality, identity confidence, privacy and end-to-end playback.
- **FR-077 [Verified live; code change pending PR #48]** Active Assist pipeline uses `conversation.declan`, `stt.declan_wyoming_speaker_recognition` and `tts.declan_voice_manager`. Sidebar default cleanup is proposed in PR #48, not yet deployed.

## 8. Learning, resilience and governance

- **FR-080 [Source]** Learning suggestions and corrections shall be reviewable, validated and constrained to safe command forms.
- **FR-081 [Source]** Settings, voice data, usage budgets and learning evidence shall remain private and survive integration updates.
- **FR-082 [Source]** Read-only reviews shall not perform household actions or trigger paid TTS requests without explicit approval.
- **FR-083 [Planned]** Each new requirement shall have an ID, acceptance criteria, traceable tests and a documented failure/rollback case.
- **FR-084 [Planned]** Track independently: implemented in source, passed CI, verified on real HA devices, and deployed to production.
- **FR-085 [Planned]** New PRs shall reference changed requirement IDs and update the spec/roadmap when behaviour changes; owner approval is required for merge and deployment.

## 9. Proposed roadmap (not implemented by this specification)

| Roadmap ID | Candidate feature | Dependency / acceptance gate |
| --- | --- | --- |
| RM-01 | Complete Jarvis-to-Declan reference migration | Approve inventory; inspect live registry and storage; idempotent migrations and rollback |
| RM-02 | Standardise all routine outcomes | Agree result schema; test Movie Time, Good Morning/Night and errors |
| RM-03 | Improve command recognition and multi-turn corrections | Repeatable voice transcripts, regression suite and no unintended actions |
| RM-04 | Improve speaker identification on all satellites | Verify bridge/gateway deployment, confidence, unknown-speaker handling and privacy |
| RM-05 | Expand music preferences and household feedback | Verify blacklist/weighting against live Music Assistant playback |
| RM-06 | Improve local STT from consented correction evidence | Review data provenance, privacy, evaluation metrics and rollback |
| RM-07 | Dashboard for requirements, diagnostics and test coverage | Stable feature inventory, automated traceability and owner review |
| RM-08 | End-to-end Home Assistant acceptance suite | Explicit hardware/provider tests beyond mocked CI |
| RM-09 | Portable configuration and native HA routines | Complete Phase 1 audit, define migration/export contracts, test fresh install and existing-home upgrade |

## 10. Conflicts reconciled in this documentation PR

- **C-01** Visitor presence was incorrectly documented as a direct persona selector. **Reconciled by owner decision**: only the Guest Mode helper chooses persona; a confirmed overnight-staying declaration shall now turn that helper on without granting authority (FR-011, FR-040, FR-047). Existing guest-persona guide still describes the prior declaration behaviour and must be updated during implementation/documentation alignment.
- **C-02** Quiet hours were incorrectly documented as forcing plain replies. **Resolved by owner decision**: retain Guest/Home persona, reduce volume and shorten non-critical speech; restrict proactive announcements/broadcasts to configurable selected Shows (initially master-bedroom Echo Show only). Implementation remains to be verified; direct requests are explicitly answered on the originating satellite at reduced volume (FR-017–018).
- **C-03** Old branding docs claimed Jarvis domains/IDs must always remain and that work is committed directly to main. **Resolved**: active integration is `declan_local`; remaining references are inventoried for a later controlled migration, and work uses PRs.
- **C-04** Source implementation and live deployment are not equivalent. **Resolved in this draft** by separate status categories; live verification is still outstanding.
- **C-05** Routine response policy **partially resolved by owner decision**: short personality-driven confirmations on confirmed success; short warnings with diagnostic details for partial failure (FR-063). **Still open:** final machine-readable schema, handling of `busy`/`failed`/`unknown`, and which routines are covered (FR-064).
- **C-06** Speaker bridge/gateway experiments have different maturity. **Open**: verify deployed components and classify each before acceptance.
- **C-07** FR-072 and FR-073 previously required a secondary TTS provider, contradicting the owner's decision to remove it. **Reconciled in this draft**; implementation remains pending in draft PR #47.
- **C-08** The owner disabled unused STT/TTS integrations and reports Declan routines still work. This is operational evidence, not proof of startup behaviour or absence of all dependencies. Keep disabled entries recoverable until a normal restart and observation period.

## 11. Owner review checklist
- **Overnight guests approved:** confirmed staying declarations automatically enable Guest Mode without granting authority or overriding names in charge (FR-047); staying status persists until explicitly cleared, not automatically inferred (FR-048). Implement and test provenance-safe release and overlapping reasons for Guest Mode; align existing guest-persona guide later.

1. Approve Guest Mode-only persona and privacy-safe fallback.
2. Approve automatic guest handover remaining opt-in and able to toggle Guest Mode.
3. **Quiet-hours policy approved:** lower volume, shorter non-critical speech and a configurable allowlist of announcement destinations (initial household selection: master-bedroom Echo Show). **Direct-request routing approved:** reply locally on the originating satellite at reduced volume, while proactive announcements remain limited to selected Shows. **Default schedule approved:** 23:00–05:00 local HA time. **Whisper-triggered quiet replies approved** for the individual interaction, subject to reliable detection (FR-019). **Default reduced volume approved: 25%**, configurable, with previous player volume restored after the response (FR-017). Whisper detection approach and edge-case volume restoration tests remain open.
4. Review [Jarvis inventory](legacy-jarvis-reference-audit.md), especially conversation, TTS, STT and voice bridge IDs.
5. **Response style approved:** short personality-driven confirmations on confirmed success and short warnings with diagnostic details on partial failure (FR-063). Finalise the machine-readable result schema and whether external HA scripts are included (FR-064).
6. Confirm which speaker/voice subsystems are live versus experimental.
7. Agree requirement governance and release/rollback gates.
8. Review portability requirements FR-007–009 and FR-086–088, including native HA routine ownership, settings source of truth, and import/export privacy defaults.

**Baseline remains DRAFT until explicitly approved.** Once agreed, mark the approved revision and record change decisions; do not silently change requirements to match future implementation.

### Source index
`custom_components/declan_local/`: `agent.py`, `audience.py`, `personality.py`, `guest_authority.py`, `planner.py`, `parser.py`, `music_controller.py`, `music_blacklist.py`, `spotify_discovery.py`, `voice_cache.py`, `voice_budget.py`, `speaker_identity.py`, `websocket.py`, `settings.py`; `tests/`; `deployment/voice-bridge/`; `deployment/wyoming-gateway/`; `docs/`.
 

**Operational note (2026-11-08):** Owner disabled all separate HA Wyoming integration entries and deleted all Assist pipelines except `Declan`; normal Declan commands/routines continue working. This supports direct bridge operation but does not prove startup behaviour or exercise OpenAI STT. Do not restore removed test pipelines as a migration prerequisite.
