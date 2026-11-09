# NOW music reliability — Release 0.52.0 implementation specification

**Priority:** P0, since owner estimates music is ~80% of Declan use. **Status:** source-confirmed defects and proposed acceptance tests. **Scope:** local voice → Music Assistant → Spotify → configured player. **No code or deployment changes in this documentation commit.**

## Verified implementation facts (main / Release 0.52.0)

1. `music_assistant_voice.py` uses fixed `ROOMS` entity IDs and returns `music_assistant_play` for song, album, artist and ordinary playlist requests; named household categories instead return `music_category`.
2. `agent.py` uses `play_verified_playlist` only when `media_type == 'playlist'`. For track/album/artist, it calls `music_assistant.play_media` with `blocking=False` and responds that the request was made. The category path invokes `declan_local.play_music_category` with `blocking=False`.
3. `music_controller.py:play` selects a category playlist, dispatches `music_assistant.play_media` asynchronously, and **immediately persists the playlist to play history**, without checking that playback started. Thus a failed start may count as a played selection.
4. `verify.py:play_verified_playlist` requires the player's reported state to be `playing` **and** an exact playlist identity attribute match. If the player is already playing the same playlist, the function may remain `unverified` even after a successful request, because it requires a transition away from the previous match. A provider/player that reports `playing` without the expected playlist identity is also `unverified`; neither condition proves audio is absent.
5. `tests/test_music_dispatch_regression.py` asserts that `music_assistant.play_media` calls in `agent.py` are non-blocking, but `play_verified_playlist` internally uses a bounded blocking service call. Any proposed change must preserve a strict response-time budget and reconcile these test expectations, not introduce indefinite blocking.

## Proposed priority fixes (separate implementation PR)

| ID | Proposed change | Acceptance |
| --- | --- | --- |
| MUSIC-P0-01 | Introduce shared playback outcome states `verified_playing`, `request_sent`, `failed`, `unverified`, `timeout` across artist/track/album/playlist/category. | Never speak a verified-success claim solely because a service call was accepted. |
| MUSIC-P0-02 | Implement bounded, cancellation-safe player-state observation after dispatch; distinguish target player `playing` from evidence that the requested content actually started. | Fast voice response even on provider failure; no duplicate dispatch on timeout; no false claims about song identity. |
| MUSIC-P0-03 | Return a result from category service or track an asynchronous operation; only record category play history after a defensible success criterion, with explicit handling of unverified state. | Failed category requests do not poison rotation history; favourites/exclusions and weighting unchanged. |
| MUSIC-P0-04 | Improve playlist verification when same playlist is already active and when Music Assistant does not expose playlist identity. | Idempotent replay is not misreported as failure; unknown identity is reported as unverified rather than fabricated success. |
| MUSIC-P1-01 | Replace hardcoded `ROOMS` mapping with validated configurable player mapping, preserving household defaults during migration. | Adding/renaming a speaker does not require source edits; missing player produces a safe error. |
| MUSIC-P1-02 | Add per-command diagnostics with request type, player, provider service outcome, observed HA state, identity evidence, elapsed time and reason for uncertainty; no credentials or private transcript leakage. | A failed playback trace can be classified without guesswork. |

## Release 0.52.0 live test matrix

Run on **kitchen**, **bedroom**, and **everywhere** separately, noting Spotify's single-stream limitation and current Music Assistant grouping. Do not interpret different speakers simultaneously playing separate Spotify streams as a requirement.

| Scenario | Spoken request example | Evidence to capture |
| --- | --- | --- |
| Track | “Play Coward of the County in the kitchen” | Assist transcript, target player, state, title/artist, audible result |
| Artist | “Play Dolly Parton in the bedroom” | Selection, playback target and actual playing state |
| Album | “Play the album [known album] in the kitchen” | Provider response and player media metadata |
| Playlist | “Play the playlist [known playlist] in the kitchen” | Playlist URI/name identity where exposed; distinguish unknown identity |
| Category | “Play some Afrikaans music everywhere” | Selected playlist, history update timing, player state |
| Stop | “Stop the music” at the originating satellite | Only intended output stops; unrelated output unaffected |
| Negative | Unavailable target player or Spotify/Music Assistant failure | Clear spoken error or uncertainty; no false success, no unwanted retry |
| Repeat | Request the playlist that is already playing | No duplicate playback or false failure |
| Follow-up | “Skip this”, “Turn it up”, “Never play this song again” | Correct current target, state and household preference/blacklist update |

## Evidence needed to distinguish code defect from integration failure

For each failure, record the Assist trace (utterance, parsed intent/steps, service call and result), `media_player` states/attributes before and after, Music Assistant queue/player state, and relevant Home Assistant/MA logs. Do not include Spotify credentials or tokens. Compare against Release 0.52.0 source; do not assume a successful dispatch means audible playback.

**Implementation, merging, CI execution and deployment require a separate code workflow.**
