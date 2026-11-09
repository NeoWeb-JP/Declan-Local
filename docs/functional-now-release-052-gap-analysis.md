# Release 0.52.0 — NOW implementation gaps versus live acceptance failures

**Audit date:** 9 November 2026. **Baseline:** owner-confirmed installed Release 0.52.0 from `main`. **Scope:** [NOW MVP](functional-now.md). **Evidence:** targeted inspection of `main` source files; no CI run, no live HA trace captured, no implementation or deployment.

## Verified code-level findings

| ID | Classification | Finding and evidence in `main` | Required next action |
| --- | --- | --- | --- |
| NOW-GAP-01 | **Partially implemented: genuine configuration gap** | `custom_components/declan_local/music_assistant_voice.py` defines a fixed `ROOMS` dictionary mapping kitchen, bedroom, lounge, downstairs and everywhere to literal `media_player.*` IDs. `_player` rejects any other room. This prevents configuration-driven discovery and portability for this voice music path. | Make room/player mappings configurable from HA entities/areas, preserve existing mappings through migration and test renamed/unavailable players. |
| NOW-GAP-02 | **Partially implemented: genuine playback-confirmation gap** | `agent.py` uses `play_verified_playlist` for playlist-type `music_assistant_play`, but dispatches non-playlist `music_assistant_play` with `blocking=False` and a request-only reply. `music_category` dispatches `declan_local.play_music_category` with `blocking=False`. `media_control` reports request sent, not resulting playback. | Define consistent request/verified/unverified/failed semantics for track, album, artist, playlist and category playback; verify the requested player and report uncertainty truthfully. Avoid blocking the Assist response indefinitely. |
| NOW-GAP-03 | **Partially implemented: routine result contract not uniform** | `verify.py:movie_result` understands `success/partial/failed/busy/unknown`. `agent.py` has a special Movie Time branch, while Good Morning and Good Night use different response logic; generic routine paths may return request-oriented speech. | Standardise routine outcome reporting across the three NOW routines; preserve per-device partial failure and never claim full completion from service dispatch alone. |
| NOW-GAP-04 | **Potential robustness gap: arbitration without comparable capture data** | `satellite_priority.py:allow` returns `True` when satellite or `SpeakerTranscript` capture metadata is missing. Arbitration therefore cannot suppress duplicates in that path. This is a documented behaviour, **not proof of a live duplicate-command defect**. | Specify and test a safe fallback when capture data is unavailable; distinguish unavoidable lack of comparison from a production regression. |

## Already implemented, not to be rebuilt

- **Satellite loudest-capture arbitration**: `satellite_priority.py` on `main`, invoked by `agent.py:async_process`. Owner-reported three successful hardware checks; other edge cases pending.
- **Lighting state/error accounting**: `device_control.py:apply_lighting` separates succeeded, failed and unverified; `verify.py:verify` polls reported HA state. HA-reported state is not physical proof.
- **Playlist-specific verification**: `verify.py:play_verified_playlist` checks `playing` and playlist identity and handles timeout/failure/unverified, but only for that playback path.
- **Movie Time outcome handling**: `verify.py:movie_result` maps success, partial, failed, busy and unknown.
- **Timer handling**: `timers.py` parses, persists and schedules timer requests, announces on the originating satellite when available, and falls back to a persistent notification on announcement failure. Live checks remain outstanding.
- **Conversation context and speaker separation**: `conversation_memory.py`, `agent.py` and related tests exist. Owner-reported local context tests do not replace end-to-end verification.

## Prioritised backlog

| Priority | Work type | Task | Acceptance |
| --- | --- | --- | --- |
| P0 | Code gap | NOW-GAP-02: consistent music verification and truthful outcome semantics | Track, album, artist, playlist and category tests distinguish verified playback, failed dispatch and unverified outcome; correct player; no false success. |
| P0 | Code gap/spec | NOW-GAP-03: unify Good Morning/Good Night/Movie Time result contract | Partial device failures visible; busy/unknown handled; no false success. |
| P0 | Live verification | End-to-end wake → STT → intent → HA service → TTS on Release 0.52.0 | Kitchen/bedroom Assist traces, local vs external provider dependency matrix. |
| P0 | Live verification | Device/room controls, corrections, Stop, playback on mapped player | Repeatable pass/fail traces, no unintended device changes. |
| P1 | Code gap | NOW-GAP-01: remove fixed music player mappings | New/renamed HA room/player configured without editing integration Python. |
| P1 | Edge case | NOW-GAP-04: capture-metadata-missing arbitration | Duplicate command safety and response behaviour explicitly tested. |
| P1 | Live verification | Five-minute context, Guest Mode, quiet hours, timer and offline paths | Timed multi-satellite, persona and WAN-disconnect results. |

## What remains unknown

No source inspection can confirm the current Home Assistant configuration, runtime provider health, actual audible playback, microphone wake performance, or whether every relevant test passes. Do **not** mark a user-observed failure as a missing implementation until the exact Assist trace and installed version are correlated with the code. No code was changed by this audit.
