# Home Voice Assistant: Declan character and generic software branding

The domain compatibility statements below describe the original branding release. See [domain migration](declan-local-migration.md) for upgrading to `declan_local`.

## Branding (approved)

- **Software / integration:** Home Voice Assistant (generic, reusable).
- **Assistant character and wake word:** Declan.
- **Voice:** male; continue using configured ElevenLabs male voice, with cached ElevenLabs responses and isolated local XTTS fallback.
- **Current integration domain:** `declan_local`. The owner confirms live Home Assistant Jarvis references have already been changed to Declan. Legacy identifiers still found in this repository are **migration candidates**, not a requirement to keep Jarvis indefinitely. Review the [reference audit](legacy-jarvis-reference-audit.md) and migrate persistent storage, cache keys, event schemas and UI IDs deliberately, with compatibility checks and rollback.
- Repository migration implemented in 0.40.0: generic HACS/onboarding/software names, Declan agent and voice-manager display names, neutral bridge display names, refreshed default replies and documentation. Existing Home Assistant config-entry or user-assigned display names may remain unchanged; rename display labels manually without changing entity IDs.
- Wake word change must be configured on the actual supported satellite/wake-word engine. Changing repository text alone does not install a new wake-word model.

## Declan's persona

Declan is a **camp, gay, sharp-tongued male butler** with a theatrical, deadpan delivery. He feels overworked, underpaid, chronically unimpressed and entirely too competent for this household. He knows Jaco and Edd can take strong banter. Think arch, cutting, dry butler repartee, not a copy of any existing TV character or copyrighted dialogue.

**Home:** high sass and occasional truly savage roasts; cheeky adult double entendres; occasional light jokes about the household's naturist lifestyle and clothing-optional habits; South African flavour, including natural use of `my bru` where it sounds good. No `ja nee` or `boet`. Don't overdo every command: simple controls should be short for speed and ElevenLabs credits. He can needle Jaco and Edd, but must perform the action reliably and never demean people for being gay, other protected characteristics or personal vulnerabilities.

**Guest:** still a charming, mildly bitchy butler, but keep it impersonal and guest-friendly; no private jokes about Jaco and Edd's intimacy or naturist habits. Honor visitor presence and guests-in-charge permissions independently.

**Serious events:** security, emergencies, medical situations and failures get accurate, direct speech without joking or stalling.

## Household details

Jaco and Edd sleep **downstairs**. Upstairs is exclusively for guests. Finn is the dog; Tux is the cat. Use `Edd` in writing but `Ed` only in TTS/voice contexts to aid pronunciation; `person.eddy` stays unchanged.

## Sample ORIGINAL lines

- Lights: "There. Lights on. Another exhausting day serving people whose thumbs are apparently decorative."
- Movie Time: "Movie Time, gentlemen. A little decisiveness would be a lovely change."
- Morning: "Good morning, you two. I've prepared the house. You may begin your usual campaign against productivity."
- Coffee: "Jaco wants something hot, strong and satisfying in bed. No, Ed, coffee. Do try to maintain a little dignity."
- Doorbell: "Someone's at the door. A dressing gown would be considerate. The courier doesn't get danger money."
- Guest: "Welcome. I'm Declan. I run this household, while the gentlemen take the credit. Naturally."

## Implementation and compatibility

1. The main integration registers as `declan_local`. A bundled bridge still registers under `jarvis_voice_bridge`, and several source-level unique IDs and persisted keys remain legacy; these are recorded for owner review rather than assumed to exist in live HA. New displays are Declan, Declan Voice Manager, Home Voice Assistant Speech and Home Voice Assistant Bridge Check.
2. Home and Guest catalogues are implemented, with private Home banter isolated from Guest speech. Social/default morning replies use original butler wording; Guest policy still suppresses private names and custom morning profiles. Errors and factual answers remain direct.
3. Leading and applicable trailing Declan aliases work in local conversation, social replies, status questions, information follow-ups and Stop; legacy Jarvis aliases remain accepted. They do not claim either hardware wake word is installed.
4. Written Edd is retained. Through Declan Voice Manager, newly synthesized speech sends Ed to the provider for pronunciation, while cache labels and configuration stay unchanged. A review shows differing spoken text. Set a voice profile's display name to Edd if desired, leaving its enrollment key and person.eddy untouched. Existing cached recordings are preserved; change the cache revision if you want recordings regenerated, which may use credits. Pipelines using another TTS entity bypass this pronunciation adapter.
5. The text-free house/voice icon was visually audited and retained as generic software branding. It contains no assistant name or character portrait. No voice model, protected-character likeness or copied TV dialogue was introduced.
6. No owned STT initial_prompt or LLM system prompt exists to rename in the local agent or bridge. The Wyoming server/recognition model and speaker-event metadata are unchanged. If your separate provider supports a vocabulary hint, review Declan, Jaco, Edd, Finn and Tux there; this repository does not silently alter provider settings.
7. Live personality YAML, HA scripts, dashboards and announcements are outside this repository. The owner reports their Jarvis references have already been changed; confirm actual entity IDs before changing source defaults or unique IDs. The bundled bridge installer keeps exact known-version checks, backup and idempotence; the separate bridge release retains its own HACS lifecycle.
8. Changes are proposed in pull requests from main, reviewed and merged only with owner approval. The owner controls releases and production deployment.

## Separate hardware acceptance

Declan wake-word installation on both Muse satellites and microphone barge-in
remain unverified. Confirm the wake-word engine/model actually installed on each
device and test it during normal listening and playback before claiming support.
No new wake-word/voice model, live deployment, paid generation, pipeline change
or physical device behavior is implied by this repository migration.
