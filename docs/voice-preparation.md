# Reviewed recordings and daily usage controls (0.39.0)

The Voice Manager reuses your configured HA TTS provider. No ElevenLabs key,
account password, speaker model or duplicate TTS integration is required.

## Review, then prepare

1. Install the updated integration and restart HA. Keep the existing Assist
   pipeline until manual playback succeeds.
2. In **Voice cache → Prepare Home and Guest recordings**, select one or both
   catalogues and click **Review recordings and estimated usage**.
3. Review every sentence, the primary provider, selected voice/cache revision,
   saved/missing count and maximum characters. Review is read-only: no paid
   generation, playback or household action is requested.
   Where written and spoken text differ, the review shows both. Newly generated
   Edd is pronounced Ed; cache labels and existing recordings stay unchanged.
4. Tick approval and click **Prepare missing recordings** only if you want to
   request the missing audio. Provider credits may be used. The catalogue
   contains approved static acknowledgements only, not live readings or
   personalized profile text. Template placeholders and factual categories
   are rejected.
5. One missing sentence is requested at a time. Already saved audio is reused.
   **Stop after current recording** prevents the next request; it cannot undo
   a request already sent or its provider charge. Completed audio is kept.

Reviews expire after 15 minutes and are invalidated by relevant voice,
catalogue or cost-setting changes. The server accepts only missing sentences
from its own reviewed plan, never arbitrary browser-supplied text. Failed
attempts require a fresh review before retrying; there are no automatic paid
retries. Insufficient storage stops preparation. If audio could not be saved,
preparation stops rather than silently continuing to spend credits.

Prepared whole sentences use the same exact text/provider/voice/revision/
language/settings/format identity as normal TTS. Concurrent runtime and
catalogue requests for an identical sentence coalesce into one request. Existing
ElevenLabs and XTTS caches remain separate; Guest fallback alternatives remain
within the Guest catalogue. No factual reading is substituted by a static reply.

## Daily local character limit

In the integration's voice options, set **Daily primary character limit**.
Zero retains the previous unlimited behavior. A positive limit reserves the
exact text length before a new primary request, across normal speech, phrase
clips, sentence saving and catalogue preparation. Concurrent requests cannot
overspend the local allowance. Existing cached primary audio and the configured
fallback remain available when the primary allowance is exhausted.

Counters are stored privately in HA storage and survive integration reload
and HA restart. The UTC day resets the allowance; moving the clock backwards
cannot reset it again. Failed or interrupted provider requests are not refunded
because the provider might have billed them. If accounting storage is corrupt
or cannot save a reservation, new primary requests are blocked before calling
the provider. Repair storage and reload the integration; local fallback is not
blocked by the primary allowance. Do not delete accounting storage to work
around a limit.

This is a **local primary character guard**, not your account balance or an
account-wide ElevenLabs quota. HA may serve some requests from its own cache,
so reserved characters/attempts are conservative estimates. Calls made directly
to ElevenLabs by other HA scripts, integrations or clients bypass this wrapper
and are not counted. Configure account/provider spending restrictions separately
where available. A fallback pointing to a paid cloud provider can also incur
charges; the fallback should be the independently configured local XTTS entity
for this intended setup.

## Estimated credits and diagnostics

Set **Estimated credits per primary character** only when you know the rate
for your selected provider/model. Zero means unknown, not zero-cost. The Voice
cache screen shows the persisted day's reserved primary requests/characters,
remaining local allowance and optional credit estimate, alongside per-process
cache reuse, source counts, provider failures and storage use. Counters retain
no speech, audio, credentials or provider error text. Actual account usage is
authoritative; model rates, normalization, retries and provider caching may
make the estimate differ from billing.

When changing the voice/model in the underlying HA provider, update the cache
revision before reusing or preparing recordings. The wrapper does not inspect
or duplicate your provider's private configuration or infer an unchanged model.

## Live acceptance checklist

- Confirm the actual primary and independent XTTS entities exist and can speak.
- Generate a short reviewed sentence, repeat it, and inspect the Voice cache
  and authoritative provider account for reuse/no repeat billing.
- Restart HA and repeat the sentence to verify persistence and voice identity.
- With primary unavailable or its local allowance exhausted, request an
  uncached sentence and confirm local fallback playback. Cached primary audio
  should retain the preferred voice.
- Confirm concurrent identical requests generate once and different satellites
  retain normal Assist playback. Stop routing/barge-in are separate tests.
- Review Home and Guest text, explicitly prepare the desired recordings, and
  verify the Guest pool never selects private Home alternatives.
- Only after playback tests, select the existing Voice Manager entity in the
  desired Assist pipeline. Roll back by reselecting the previous TTS entity;
  keep the cache and provider configuration intact.

Automated tests exercise the actual wrapper/cache/API boundaries using controlled
HA fixtures, budget storage failures/restarts, concurrent reservations and
preparation review/approval. They do not prove live acoustic playback or billing.
The available connected HA tools did not expose TTS entities during development;
no paid generation, live deployment, pipeline switch or speaker playback was
performed to claim those checks complete.
