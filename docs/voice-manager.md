# Declan Voice Manager: persistent cache and fallback

## Configuration

The integration provides a Declan Voice Manager TTS entity. It uses the
existing Home Assistant TTS integrations, not an additional ElevenLabs API key.

Default providers:
- **Primary:** `tts.elevenlabs_text_to_speech`
- **Fallback:** `tts.jarvis_xtts` (the existing GPU XTTS Home Assistant entity)

The entity can be tested after deploying the updated source and restarting
Home Assistant. Do not switch the Muse Assist pipeline until manual speech
generation succeeds.

## Cache

Audio is stored persistently at `/config/jarvis_voice_cache` (outside the
GitHub-managed custom component). For each request, the manager:

1. Checks a format-aware cache keyed by exact text, provider, revision,
   language and synthesis options.
2. On miss, asks Home Assistant's provider TTS media-source API for audio
   with its own built-in cache enabled, and stores valid audio atomically.
3. If ElevenLabs generation fails, tries the **separate** XTTS cache/provider.
4. Never mixes the fallback voice into the ElevenLabs cache.

Identical concurrent requests are coalesced for a single manager instance.
Cached recordings can be used even if ElevenLabs is temporarily offline.

**Important:** The provider voice/model currently configured in Home
Assistant is not directly discoverable from this cache's metadata.
Change `cache_revision` in the Home Voice Assistant integration options to a new value
if you change voices or ElevenLabs synthesis settings, or remove the
cache directory, to avoid returning recordings in the previous voice.
The options flow provides this setting.

## Live acceptance still required

- Validate against the installed Home Assistant version (entity registration,
  ElevenLabs media-source output and Muse playback).
- Verify fallback entity `tts.jarvis_xtts` actually exists and works.
- Confirm provider failures beyond the handled exceptions and TTS format
  compatibility. Test failed and concurrent generations end-to-end.
- Review and explicitly prepare the selected static Home/Guest catalogue
  after installing 0.39.0; this can use provider credits. The preparation UI
  and durable local character guard are implemented; see the guide below.
- Check authoritative account usage and provider-side spending restrictions.
  Local estimates cannot establish actual billing or enforce a cap on calls
  made directly to the provider by other integrations.
- Avoid assuming saved audio is encrypted: treat the cache as private
  household data and exclude it from public repositories.

## Reviewed preparation and usage controls (0.39.0)

See [catalogue preparation and daily usage controls](voice-preparation.md).
Opening a review never generates speech. It shows exact approved static text,
saved/missing state, selected voice and a maximum character estimate. Preparing
requires explicit approval and stores whole sentences in the primary voice's
normal persistent cache. It plays no audio and runs no household actions.

All primary generation paths through this wrapper share a durable UTC-day
character allowance. Cache hits consume no allowance; failed provider attempts
remain reserved conservatively. Optional estimated credits use your explicitly
configured rate. Existing provider credentials and entity/unique IDs are retained.

## Provider reliability (0.35.1)

The default local fallback `tts.jarvis_xtts` is allowed. Earlier versions
mistakenly rejected every entity beginning `tts.jarvis_`, preventing this
fallback from generating new audio. The guard now rejects the registered
Voice Manager itself (including a renamed entity) and legacy Voice Manager
names, while allowing the independent XTTS integration.

Each provider audio request has a 30-second deadline. A stalled primary
provider therefore allows the fallback to run; cancellation from the caller
still propagates immediately. Both providers failing produces a direct
error. Provider exception details are excluded from logs because they may
contain private speech or credentials.

The Voice cache screen reports per-process primary/fallback failure counts
and the percentage of successful requests that used cached audio. Failed
attempts are counted separately from successful speech. These are local
diagnostics, not ElevenLabs billing or credit measurements. Home Assistant's
own cache may satisfy a request that this integration counts as generated.

Tests exercise the real provider boundary with simulated Home Assistant
audio responses, including the default XTTS entity, a hung primary, separate
fallback cache reuse, renamed-wrapper recursion and cancellation. They do
not establish live speaker playback, GPU health or account billing.

## Deploy/test

1. Update Home Voice Assistant from GitHub main using your chosen deployment method.
2. Restart Home Assistant and confirm Declan Voice Manager exists.
3. Use a manual TTS test with a short phrase; verify ElevenLabs playback.
4. Repeat the exact phrase and confirm a hit via debug logs and no new
   ElevenLabs usage. Check files under `/config/jarvis_voice_cache`.
5. Test fallback by temporarily making ElevenLabs unavailable without
   clearing its cache and using a **new uncached phrase**.
6. Once verified, select Declan Voice Manager in the Assist pipeline.
7. Rollback: reselect the previous ElevenLabs entity in Assist, then
   restore the previous Home Voice Assistant release if needed.

All changes currently sit on `main`, per owner preference. The owner
controls releases. No production Home Assistant deployment was performed.


## Preferred voice consistency (category fallback)

When ElevenLabs is unavailable, Declan now attempts this order:

1. Exact cached ElevenLabs audio (including when ElevenLabs is offline).
2. If exact generation fails: a **previously cached ElevenLabs line in the same approved personality response category** (same action, same Guest/Home privacy pool).
3. Existing local XTTS TTS entity for the original requested text.
4. Report TTS failure if no provider works.

Only exact entries in `responses.json` are eligible for alternate wording.
The implementation currently recognises `general`, `on`, `off`,
`brightness` and `morning`; Home uses Home,
Guest uses Guest alone. The candidate must already exist in the persistent
ElevenLabs cache, with matching provider, revision, language and settings.
No paid request is made to generate an alternate when ElevenLabs is down.
This may not cover phonetic-script transformations or future unified persona
catalogues until they are integrated. Since 0.36.0, the shared visitor-aware
speech privacy policy selects Home or Guest; unavailable signals use Guest.

**Never substitute** dynamic weather, temperature, time, status details,
security/error messages, or unknown text. A cached light-on reply cannot
replace a light-off confirmation. The actual audio can differ from the
original TTS-request text for approved category alternates; this should be
reviewed before production rollout.

These paths require unit and end-to-end playback tests before deployment.

## Reusable clips and cache screen (0.28.0)

The sidebar now has an administrator-only **Voice cache** screen with saved
phrase previews, explicit clip/whole-sentence preparation, storage usage and
per-process source counters. Music responses can reuse genre and room clips,
decoded once and joined into a single WAV. Exact whole-sentence audio takes
precedence. See [Reusable voice phrases](phrase-library.md) for limits and tests.
