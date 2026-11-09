# NOW — Code-versus-requirements audit (initial evidence pass)

**Date:** 9 November 2026. **Status:** Evidence-based initial audit, not a release sign-off. **Scope:** [NOW voice MVP](functional-now.md), not deferred homelab or optimisation work.

## Evidence and classification rules

Reviewed source in `NeoWeb-JP/Declan-Local` at `main` and PR #46's documented source branch `docs/functional-baseline-and-legacy-reference-audit`. Compared recursive Git trees and inspected key Python modules and existing tests. **No tests were run, no live HA configuration inspected and no deployment version verified.** A module's existence proves an implementation candidate, not correct behaviour. This report distinguishes branch presence, automated test existence and live verification.

- **Implemented:** source directly covers the reviewed requirement's stated NOW slice; still separately identify missing live verification.
- **Partially implemented:** source covers only a subset or there is an unresolved behaviour/contract gap.
- **Missing:** no implementation found for a specifically identified NOW behaviour in the inspected branch; further search may refine this.
- **Requires live testing:** implementation is present but the specific end-to-end hardware/provider/HA acceptance scenario has not been verified by evidence available to this audit.
- **Unknown:** cannot honestly determine from the inspected code and documents; do not equate unknown with missing.

## Audit matrix

| NOW slice and source IDs | PR #46 branch code assessment | Evidence | Next action |
| --- | --- | --- | --- |
| Assist wake, pipeline, voice output (FR-001–004, 070, 077) | **Partially implemented; requires live testing** | `custom_components/declan_local/agent.py`, `conversation.py`, `stt.py`, `tts.py` exist. Wake-word model and Assist pipeline configuration are external to this code review. | Record actual configured wake word, satellites, STT/TTS path, end-to-end command/response and outage behaviour. |
| Multi-satellite loudest capture (FR-045AP NOW slice) | **Missing from PR branch; implemented candidate on main; requires branch reconciliation and live testing** | `custom_components/declan_local/satellite_priority.py` exists on `main` but not on PR #46 branch's recursive tree. NOW doc reports three owner-passed hardware checks, without commit/CI provenance. | Identify the implementing commit and actual deployment branch; reconcile without copying runtime code into documentation PR; test failover separately. |
| Room control, brightness, ambiguity and correction (FR-020–021, 024, 026–027, 034) | **Partially implemented; requires live testing** | `agent.py`, `device_control.py`, `room_context.py`, `room_brightness.py`, `clarification.py`, `corrections.py`; `tests/test_device_control.py` and `tests/test_declan_corrections.py`. | Run real room/area, ambiguity, correction, renamed entity and partial-failure scenarios. |
| Five-minute follow-up and speaker/session isolation (FR-025, 028, 031–035, 040) | **Partially implemented; requires live testing** | `conversation_memory.py`, `followup.py`, `agent.py`, `tests/test_conversation_memory.py`, `tests/test_declan_followups.py`. NOW doc reports focused local patch checks; not equivalent to verified deployment. | Verify rolling expiry and conversation ID continuity on actual satellites, restart behaviour, anonymous/known speaker isolation. |
| Music Assistant/Spotify play and stop (FR-050, 054, 061) | **Partially implemented; requires live testing** | `music_assistant_voice.py`, `music_controller.py`, `satellite_stop.py`; `tests/test_music_dispatch_regression.py` explicitly checks non-blocking dispatch, not proof of actual audible playback. | Test start, verified playing state, correct speaker, transport, category, Stop and unavailable-provider errors. |
| Time/weather/status/timers (FR-060–062) | **Implemented candidate; requires live testing** | `information_dialogue.py`, `timers.py`, `tests/test_information_dialogue.py`, `tests/test_timers.py`. | Test timers through originating satellite, expiry/invalid durations, time/weather freshness and missing entities. |
| Good Morning/Good Night/Movie Time routine invocation and outcomes (FR-009, 022–023, 063–064) | **Partially implemented; decision open** | `agent.py` has routine handling; `tests/test_agent_routine_failures.py` includes Tuya failure classification; FR-063 standard outcome contract and FR-064 routine coverage are not fully closed. | Define supported routine inventory and machine-readable aggregate/partial outcomes; test each script including Tuya rejection. |
| Home/Guest persona, quiet hours, privacy, no speaker-as-authentication (FR-010–018, 020A, 071) | **Partially implemented; requires live testing** | `guest_authority.py`, `personality.py`, `audience.py`, `speaker_identity.py`; `tests/test_guest_authority.py`, `tests/test_audience.py`, `tests/test_brutal_personality.py`. | Test guest activation and privacy, unknown speaker, mode-unavailable fallback, quiet-hour volume and correct persona. |
| Offline local voice control | **Partially implemented / external dependency; requires live testing** | Local HA intent and device modules exist; `stt.py` exposes OpenAI STT; `tts.py` contains provider/cache/fallback paths that require reconciliation against the current ElevenLabs-only policy in FR-073. | Document installed pipeline, disconnect WAN, test local recognition/control and precisely which spoken responses remain available. |

## Prioritised development and verification backlog

| Order | Type | Work item | Exit evidence |
| --- | --- | --- | --- |
| P0-01 | Branch reconciliation | Determine why `satellite_priority.py` exists on `main` but not the PR #46 documentation branch; identify production version. | Commit references and branch/deployment matrix, no unsupported claim of missing functionality. |
| P0-02 | Live integration | End-to-end wake/STT/intent/TTS on kitchen and bedroom satellites, with explicit outage matrix. | Captured HA Assist traces and pass/fail per satellite. |
| P0-03 | Live integration / potential fixes | Room and device commands, ambiguity, correction, multiple commands and error truthfulness. | Repeatable scenario results, no unintended entity changes. |
| P0-04 | Live integration / potential fixes | Music Assistant playback verification and Stop on originating player. | Actual player state and audible playback, negative cases. |
| P0-05 | Specification + code gap | Close FR-063 partial outcome contract and FR-064 routine list, then exercise Good Morning, Good Night and Movie Time. | Documented contract, script traces, no false-success reports. |
| P1-01 | Live integration | Five-minute context, speaker/session isolation and conversation ID continuity. | Timed two-satellite evidence. |
| P1-02 | Live integration | Guest Mode, privacy, personality and quiet-hours behaviour. | Mode matrix and voice response evidence. |
| P1-03 | Live integration | Timers, weather/time/status and malformed inputs. | Per-intent positive/negative traces. |
| P1-04 | Documentation/policy | Resolve actual TTS fallback policy vs code and offline-first claim. | Signed-off dependency matrix; no false offline promise. |

## Audit limitations and next pass

This initial audit uses a targeted source inspection, file-tree comparison and test-file inventory. It is **not a line-by-line audit of every NOW requirement**, and test-file presence is not test success. It does not prove which commit is deployed in HA. Before changing code, obtain the installed integration version/commit, configured Assist pipeline, two-satellite traces, Music Assistant player states and CI outcomes; then classify each exact FR ID individually with source locations and executable acceptance tests.

**No code changes, CI execution, merge or deployment.**
