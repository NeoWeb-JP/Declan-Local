# Music playback reliability — implementation checklist

Target: Declan `main` Release 0.52.0. Separate from documentation-only PR #46.

## First implementation slice

- [ ] Add a shared, bounded playback observation API that returns `verified_playing`, `request_sent`, `unverified`, `failed` or `timeout`, with an explicit evidence reason.
- [ ] Route track, album, artist, playlist and category requests through the shared result handling, preserving the Assist response-time budget and avoiding duplicate dispatch.
- [ ] Ensure the category playlist history is not updated on failed dispatch; define and test handling of accepted-but-unverified playback.
- [ ] Handle requesting an already-playing playlist without incorrectly treating lack of a state transition as failure.
- [ ] Add tests for playing state, missing metadata, wrong target player, delayed provider, timeout, failed dispatch, repeated request, category history and Stop.
- [ ] Preserve Spotify single-stream semantics and existing favourite/exclusion/weighting behaviour.
- [ ] Confirm kitchen, bedroom and Everywhere against the actual Home Assistant and Music Assistant entities.

## Follow-up slice

- [ ] Replace hardcoded `ROOMS` mappings with validated Home Assistant configuration and safe migration.
- [ ] Add diagnostics for dispatch, selected player, observed state, media identity, timing and uncertainty without leaking credentials.

## Safety and release gates

No merging or deployment without owner approval. Run automated tests and CI, review existing `test_music_dispatch_regression.py` latency expectations, and then gather real Assist traces. Do not equate a dispatched request or a Home Assistant `playing` state with proof of audible output.

Specification: [PR #46 music reliability](https://github.com/NeoWeb-JP/Declan-Local/blob/docs/functional-baseline-and-legacy-reference-audit/docs/functional-now-music-reliability.md).
