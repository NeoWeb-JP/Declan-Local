# Home Voice Assistant: Declan character and generic software branding

## Branding (approved)

- **Software / integration:** Home Voice Assistant (generic, reusable).
- **Assistant character and wake word:** Declan.
- **Voice:** male; continue using configured ElevenLabs male voice, with cached ElevenLabs responses and isolated local XTTS fallback.
- **Internal compatibility:** keep existing `jarvis_local` and `jarvis_voice_bridge` integration domains, entity IDs, configuration keys, file paths, service identifiers and existing web routes until a tested migration. Do not rename them merely for branding. Existing YAML and Assist pipelines rely on these identifiers.
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

1. Both repositories retain their legacy domains and registration identities. New displays are Declan, Declan Voice Manager, Home Voice Assistant Speech and Home Voice Assistant Bridge Check. Existing Assist selections remain tied to their existing IDs; fresh installations may receive newly suggested IDs from HA.
2. Home and Guest catalogues are implemented, with private Home banter isolated from Guest speech. Social/default morning replies use original butler wording; Guest policy still suppresses private names and custom morning profiles. Errors and factual answers remain direct.
3. Leading and applicable trailing Declan aliases work in local conversation, social replies, status questions, information follow-ups and Stop; legacy Jarvis aliases remain accepted. They do not claim either hardware wake word is installed.
4. Written Edd is retained. Through Declan Voice Manager, newly synthesized speech sends Ed to the provider for pronunciation, while cache labels and configuration stay unchanged. A review shows differing spoken text. Set a voice profile's display name to Edd if desired, leaving its enrollment key and person.eddy untouched. Existing cached recordings are preserved; change the cache revision if you want recordings regenerated, which may use credits. Pipelines using another TTS entity bypass this pronunciation adapter.
5. The text-free house/voice icon was visually audited and retained as generic software branding. It contains no assistant name or character portrait. No voice model, protected-character likeness or copied TV dialogue was introduced.
6. No owned STT initial_prompt or LLM system prompt exists to rename in the local agent or bridge. The Wyoming server/recognition model and speaker-event metadata are unchanged. If your separate provider supports a vocabulary hint, review Declan, Jaco, Edd, Finn and Tux there; this repository does not silently alter provider settings.
7. Live personality YAML, HA scripts, dashboards and existing announcements are outside this source migration and were not rewritten. Their display/speech labels require a live audit while retaining IDs. The bundled bridge installer keeps exact known-version checks, backup and idempotence; the separate bridge release retains its own HACS lifecycle.
8. Changes are committed directly to main under owner authorization. The owner controls releases.

## Separate hardware acceptance

Declan wake-word installation on both Muse satellites and microphone barge-in
remain unverified. Confirm the wake-word engine/model actually installed on each
device and test it during normal listening and playback before claiming support.
No new wake-word/voice model, live deployment, paid generation, pipeline change
or physical device behavior is implied by this repository migration.
