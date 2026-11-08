# Legacy Jarvis references: review inventory

**Status:** REVIEW REQUIRED. Based on `main` after PR #45 merged, 2026-11-08. This is a source-code inventory, **not** an assertion that any legacy HA entity still exists. The owner reports that **all live Home Assistant Jarvis references have been renamed to Declan**.

**Decision:** No Jarvis identifiers, storage keys, paths, protocol events or entity IDs are renamed in this documentation PR. Renaming them without checking the live registry, persistent data and bridge clients risks breaking installed integrations. The list below is for approval of a separate migration PR. Line numbers refer to `main` at audit time; use search for exact identifiers after edits.

## A. Runtime entity IDs and user-facing defaults: review first

| ID | File / approximate line | Legacy reference | Why it matters | Suggested action |
| --- | --- | --- | --- | --- |
| J-01 | `custom_components/declan_local/agent.py:46` | `_attr_unique_id = 'jarvis_local_test'` | Entity registry unique ID, not necessarily the current `entity_id` | Compare installed registry; migrate carefully if needed |
| J-02 | `custom_components/declan_local/panel.js:10,439,1119` | `conversation.jarvis_local_test` | Default conversation agent for sidebar and command UI | **Likely stale** given owner confirmation; replace with verified current entity ID or discover from config |
| J-03 | `custom_components/declan_local/panel.js:456` | `stt.jarvis_voice_bridge_test` | Friendly-name special case for bridge engine | Verify current bridge STT entity, then update |
| J-04 | `custom_components/declan_local/tts.py:25`; `config_flow.py:9`; `docs/voice-manager.md` | `tts.jarvis_xtts` | Default fallback provider | Confirm actual local TTS entity; change default with backwards-compatible settings handling |
| J-05 | `custom_components/declan_local/tts.py:158,172`; `voice_provider.py:25` | `tts.jarvis_voice_manager` | Recursion prevention for historical manager entities | Keep guard until old IDs proven absent; add/retain Declan equivalent |
| J-06 | `custom_components/declan_local/agent.py:204` | optional spoken `jarvis` alias | Backwards-compatible speech grammar | Ask whether to remove legacy voice alias; low risk but user-visible |
| J-07 | `custom_components/declan_local/agent.py:43`; `tts.py:44`; `config_flow.py:12`; `panel.js:1,1128` | `JarvisAgent`, `JarvisVoiceManager`, `JarvisConfigFlow`, `JarvisLocalPanel`, `jarvis-local-panel` | Python class names / frontend custom-element tag | Rename internally only after checking imports and UI registration |
| J-08 | `custom_components/declan_local/__init__.py:69,78,91` | sidebar route `jarvis-local-app`, custom element `jarvis-local-panel` | Browser URL / frontend registration | Migrate together with panel.js and navigation tests |
| J-09 | `custom_components/declan_local/panel.js:118,441,547-555` | `jarvis_local_voice_pipeline`, `jarvis_local_quick_commands_v1/v2` | Browser localStorage preference keys | Migrate saved preferences rather than dropping them |
| J-10 | `custom_components/declan_local/panel.js:230` | `jarvis_voice_clips` | Phrase pack format discriminator | Version or accept both formats during migration |

## B. Persisted storage and file paths: migration required

| ID | File | Legacy key/path | Migration consideration |
| --- | --- | --- | --- |
| J-11 | `settings.py` | `Store(..., 'jarvis_local.settings')`, `jarvis_local_settings.json` | Existing settings must remain readable; migrate to new key once with recovery |
| J-12 | `__init__.py`, `websocket.py` | `jarvis_local.debug`, `jarvis_local.learning_aliases` | Retain diagnostics and taught commands |
| J-13 | `learning.py` | `jarvis_local.learning_evidence`, `jarvis_local.learning_aliases` | Preserve learning data and deduplicate aliases |
| J-14 | `guest_authority.py` | `jarvis_local.guest_authority` | **High risk:** ownership records protect against unintended helper changes |
| J-15 | `music_controller.py` | `jarvis_local.spotify_categories`, `jarvis_local.music_history` | Preserve favourites, exclusions, history and weights |
| J-16 | `tts.py` | `jarvis_local.voice_usage` | Preserve durable daily credit/character accounting |
| J-17 | `tts.py`, `docs/voice-manager.md` | `/config/jarvis_voice_cache` | Preserve cached audio and billing avoidance |
| J-18 | `__init__.py`, `websocket.py`, `voice_profiles.py` | `/config/jarvis_voice_id.json`, temporary prefix `.jarvis_voice_id_` | Preserve enrolled speaker profiles and secret |
| J-19 | `voice_cache.py` | temporary prefix `.jarvis-` | Low-risk cosmetic filename, but verify cleanup tests |
| J-20 | `docs/declan-local-migration.md` | historical `jarvis_local` domain/registry entries | **Historical migration instructions**, not a current entity to rename blindly; add completion note |

## C. Bridge and speaker event protocol: coordinate across components

| ID | File(s) | Legacy reference | Required review |
| --- | --- | --- | --- |
| J-21 | `deployment/voice-bridge/custom_components/jarvis_voice_bridge/` | package path and `domain = 'jarvis_voice_bridge'` | Separate HA integration migration, including config entries and HACS lifecycle |
| J-22 | `custom_components/declan_local/websocket.py:266` | `async_entries('jarvis_voice_bridge')` | Discovery of bridge integration |
| J-23 | `deployment/voice-bridge/custom_components/jarvis_voice_bridge/stt.py`; `deployment/voice-bridge/voicepipeline/wyoming_server.py`; `wyoming_speaker_stt.py` | Wyoming event `jarvis-speaker` | Producer and all consumers must migrate atomically or support dual event types |
| J-24 | `speaker_identity.py:50,104` | transcript metadata `jarvis_speaker` | Dual-read support while speaker pipeline transitions |
| J-25 | `deployment/voice-bridge/install-ha-bridge.sh` | `jarvis_voice_bridge` install/backup folders, `.jarvis-bridge.*` temp names | Installer/rollback compatibility and preserved backups |
| J-26 | `deployment/wyoming-gateway/README.md`, `docs/integrated-speaker-bridge.md` | `jarvis-speaker` event and `jarvis_voice_id.json` | Update documentation only after event/path migration |
| J-27 | `deployment/voice-bridge/custom_components/jarvis_voice_bridge/manifest.json` | old `NeoWeb-JP/Jarvis-Local` URLs | Update repository links independently of domain migration |
| J-28 | `deployment/voice-bridge/experiments/`, `experiments/voice-bridge/`, `voice-id-test/` | historic Jarvis paths/names | Treat snapshots/fixtures as historical; do not bulk-replace |

## D. Outdated documentation and repository URLs

| ID | Location | Current issue | Proposed action |
| --- | --- | --- | --- |
| J-29 | `custom_components/declan_local/manifest.json:16,18` | Documentation and issue URLs still point to `NeoWeb-JP/jarvis-local` | Update to `NeoWeb-JP/Declan-Local` after confirming intended canonical repository |
| J-30 | `README.md` HACS instructions | Previously pointed to `NeoWeb-JP/jarvis-local` | **Corrected in this PR** |
| J-31 | `README.md`, `docs/guest-persona.md` | Visitor presence incorrectly described as persona selector | **Corrected in this PR** |
| J-32 | `docs/guest-persona.md` | Quiet hours incorrectly described as plain-response override | **Corrected in this PR** |
| J-33 | `docs/branding-declan.md` | Claims both domains and all IDs must remain Jarvis; claims direct commits to main | **Corrected in this PR** |
| J-34 | `docs/voice-manager.md`, `docs/voice-settings-0.27.0.md` | Legacy fallback TTS ID and cache path | Mark as migration candidates until current HA IDs verified |
| J-35 | `docs/declan-local-migration.md` | Historical domain migration, with example `conversation.jarvis_local_test` | Retain as archive for pre-migration installations; annotate for current state |
| J-36 | `voice-id-test/README.md`, bridge experiments | Historical Jarvis-era instructions | Label legacy/experimental; avoid treating as current deployment guide |

## E. Verification required before a migration PR

1. Export **entity IDs and unique IDs** for conversation agent, Voice Manager TTS, XTTS fallback and bridge STT from the current HA entity registry. These are not necessarily equal.
2. Confirm whether the separate `jarvis_voice_bridge` integration is installed or the integrated Wyoming speaker STT has replaced it.
3. Check the actual storage files in `/config/.storage/`, existing `/config/jarvis_voice_cache` and speaker-profile JSON. **Do not delete or rename until a verified migration exists.**
4. Inventory all producers and consumers of `jarvis-speaker` and `jarvis_speaker` (gateway, bridge, HA integration and VoicePipeline).
5. Confirm whether the old `jarvis` spoken alias should be removed or left as a transitional alias.
6. Require a backup, idempotent migration, tests for upgraded and clean installations, and a rollback before changing keys, domains or unique IDs.

**Scope limit:** This inventory covers source files and the main runtime/bridge/docs references inspected on the merged main branch. Test fixtures and archived experiments contain additional historical Jarvis strings; the migration PR should run a full case-insensitive repository search and classify every remaining match. No live HA registry or configuration was accessible for validation.

## F. Live HA registry evidence (owner-supplied, 2026-11-08)

The owner ran a read-only query of `/config/.storage/core.entity_registry` and `core.config_entries` on Home Assistant OS 18.4 / Core 2026.11.0. **Registry existence does not prove a provider is used in an Assist pipeline.**

| Domain | Entity ID | Registry platform / config-entry title | Initial classification |
| --- | --- | --- | --- |
| Conversation | `conversation.declan` | `declan_local` / Home Voice Assistant | Current Declan agent; retain |
| Conversation | `conversation.jarvis_local_test` | `conversation` / no entry title | Potential legacy orphan; investigate before removal |
| Conversation | `conversation.google_ai_conversation` | Google Generative AI | Independent provider; do not remove without usage check |
| Conversation | `conversation.ollama_conversation` | Ollama | Independent provider; do not remove without usage check |
| STT | `stt.declan_openai_transcription` | `declan_local` / Home Voice Assistant | Declan provider; retain pending pipeline check |
| STT | `stt.declan_wyoming_speaker_recognition` | `declan_local` / Home Voice Assistant | Declan speaker-aware STT; retain pending pipeline check |
| STT | `stt.elevenlabs_speech_to_text` | ElevenLabs | Independent provider |
| STT | `stt.faster_whisper` | Wyoming / Whisper | Verify endpoint and pipeline usage |
| STT | `stt.faster_whisper_2` | Wyoming / faster-whisper | Verify endpoint and pipeline usage |
| STT | `stt.faster_whisper_3` | Wyoming / faster-whisper | Verify endpoint and pipeline usage; possible duplicate |
| STT | `stt.google_ai_stt` | Google Generative AI | Independent provider |
| STT | `stt.home_assistant_cloud` | Home Assistant Cloud | Independent provider |
| STT | `stt.voice_pipeline` | Wyoming / voice-pipeline | Verify endpoint and pipeline usage |
| TTS | `tts.declan_voice_manager` | `declan_local` / Home Voice Assistant | Current Declan manager; retain |
| TTS | `tts.elevenlabs_text_to_speech` | ElevenLabs | Potential primary provider |
| TTS | `tts.google_ai_tts` | Google Generative AI | Independent provider |
| TTS | `tts.google_translate_en_com` | Google Translate | Independent provider |
| TTS | `tts.home_assistant_cloud` | Home Assistant Cloud | Independent provider |
| TTS | `tts.piper` | Wyoming / Piper | Local provider; retain pending usage check |

**Confirmed mismatch:** `panel.js` still defaults to `conversation.jarvis_local_test`, while the live registry has `conversation.declan`. Source fallback/default should be updated to the real Declan entity after confirming the relevant Assist and sidebar configuration. The legacy conversation registry entry should not be deleted until its references are checked.

**Important fallback mismatch:** Source currently defaults to `tts.jarvis_xtts`, which is absent from the owner-supplied TTS registry list. Do **not** assume `tts.piper` is an equivalent fallback; inspect configured TTS provider and actual pipeline settings before selecting a replacement.

**Next evidence needed:** Read-only export of `/config/.storage/assist_pipeline.pipelines` (or the applicable pipeline storage file) listing pipeline name, conversation agent, STT and TTS entity IDs, with secrets omitted. Also check any `declan_local` TTS fallback setting and Wyoming config-entry endpoint titles. No deletions or runtime renames approved.

## G. Assist pipeline evidence (owner-supplied, 2026-11-08)

Read-only export from `/config/.storage/assist_pipeline.pipelines`:

| Pipeline | Conversation | STT | TTS | Assessment |
| --- | --- | --- | --- | --- |
| Declan | `conversation.declan` | `stt.declan_wyoming_speaker_recognition` | `tts.declan_voice_manager` | Primary Declan pipeline; preserve |
| Voice enrolment | `conversation.declan` | `stt.declan_wyoming_speaker_recognition` | `tts.declan_voice_manager` | Same provider selections; preserve until purpose confirmed |
| Jarvis Isolated Test | `conversation.jarvis_voice_bridge_test_2` | `stt.jarvis_voice_bridge_test_2` | `tts.home_assistant_cloud` | Legacy test pipeline; retirement candidate, **not approved for deletion** |
| Home Assistant Cloud | `conversation.home_assistant` | `stt.home_assistant_cloud` | `tts.home_assistant_cloud` | Independent fallback; preserve |

**Confirmed:** The main Declan and Voice enrolment pipelines both reference correctly named Declan entities. No need to rename those pipeline provider IDs. The source `panel.js` default `conversation.jarvis_local_test` is inconsistent with the main pipeline and the actual Declan registry entity. The legacy isolated-test pipeline references `*_jarvis_voice_bridge_test_2` entities absent from the supplied registry inventory, so it may be stale; some providers may be dynamically exposed, so do not delete without checking. The source default `tts.jarvis_xtts` is not in the registry inventory; actual Voice Manager fallback configuration remains unverified.

**Proposed next review:** Identify whether the isolated-test pipeline is still used by any satellite or manual test; inspect configured Voice Manager fallback provider. Do not remove providers merely because they are not selected by these four pipelines.

## H. Owner decision: active pipeline (2026-11-08)

The owner confirmed **only the Assist pipeline named `Declan` is used**. Therefore:

- **Retain as active:** `Declan` → `conversation.declan` / `stt.declan_wyoming_speaker_recognition` / `tts.declan_voice_manager`.
- **Mark for retirement (not yet removed):** `Jarvis Isolated Test`, `Voice enrolment`, and `Home Assistant Cloud` Assist pipelines.
- **Do not equate unused pipelines with unused providers:** Keep underlying STT/TTS integration entities until dependencies, fallback settings and any direct service calls have been checked.
- **Implementation follow-up:** Remove the hardcoded `conversation.jarvis_local_test` sidebar fallback in favour of the confirmed `conversation.declan` or a validated configured agent; do not change registry unique IDs in a documentation-only PR.
- **Operational boundary:** No HA pipeline, entity, provider or automation has been deleted or disabled by this PR. Any actual cleanup requires a separate approved change in the live HA environment.

## I. Live Declan Voice Manager options (owner-supplied, 2026-11-08)

Read-only inspection of `core.config_entries` for the `declan_local` entry titled `Home Voice Assistant` confirmed that its `data` has no TTS options, but its **options** explicitly specify:

| Setting | Live value | Decision |
| --- | --- | --- |
| `primary_tts` | `tts.elevenlabs_text_to_speech` | Retain |
| `fallback_tts` | `tts.jarvis_xtts` | Broken/stale candidate: absent from supplied entity registry; validate replacement |
| `cache_enabled` | `True` | Retain |
| `category_fallback` | `True` | Retain |

Source `tts.py` and `config_flow.py` both also default to `tts.jarvis_xtts`. The live options override defaults, so **changing the source default alone will not repair the existing HA installation**. The registered `tts.piper` is a potential local fallback, subject to successful playback and compatibility test. Owner has not yet approved or performed a live option change. Preserve caching and category fallback settings. Avoid editing `.storage` directly while Home Assistant runs; use the integration's supported options flow.

## J. Wyoming/STT endpoint audit (owner-supplied, 2026-11-08)

Home Assistant `wyoming` config entries:

| Entry | Endpoint | Classification |
| --- | --- | --- |
| Piper | `core-piper:10200` | Unused by active Assist pipeline; removal candidate pending other dependencies |
| openWakeWord | `core-openwakeword:10400` | Wake-word service; **not** STT/TTS cleanup candidate without satellite check |
| Whisper | `core-whisper:10300` | Not selected by active pipeline; removal candidate pending other dependencies |
| voice-pipeline | `192.168.0.43:10300` | Investigate separate VoicePipeline service |
| faster-whisper | `192.168.0.53:10300` | Investigate distinct port/service |
| faster-whisper | `192.168.0.53:10301` | Investigate distinct port/service |

Live `declan_local` options: `wyoming_bridge_enabled=True`, `wyoming_bridge_host=192.168.0.43`, `wyoming_bridge_port=10301`, `openai_stt_enabled=True`, `openai_stt_model=gpt-transcribe`. Source `wyoming_speaker_stt.py` directly connects via `AsyncTcpClient(self.host,self.port)` and consumes the legacy `jarvis-speaker` event. Thus the active Declan pipeline does not directly select any separately registered Wyoming STT entity; **do not infer** that the service at `192.168.0.43:10301` is independent of downstream Whisper/VoicePipeline services. Check VoicePipeline deployment topology before removing any server or HA integration. OpenAI STT is enabled but whether its API key is configured or it is used as a fallback is not established by this evidence.

## K. Owner-confirmed cleanup state (2026-11-08)

The owner reports **all separately registered Home Assistant Wyoming integrations disabled**, with Declan's ordinary voice commands and routines still working. All other Home Assistant Assist voice-assistant pipelines have been **deleted**, leaving only the active `Declan` pipeline. These reports supersede the earlier inventory's provisional instructions to preserve the legacy test, Cloud, and Voice enrolment pipelines; they are historical entries, not active configuration. The direct Declan speaker-aware Wyoming client remains configured at `192.168.0.43:10301` and must **not** be confused with the disabled HA Wyoming integrations. The external bridge service must remain available. Do not infer that OpenAI STT was exercised, that wake-word startup/reboot has been tested, or that disabled integrations can safely be uninstalled from the reported success alone.

**Migration implication:** do not spend implementation effort migrating deleted Assist pipelines or resurrecting obsolete HA Wyoming config entries. Keep active `conversation.declan`, `stt.declan_wyoming_speaker_recognition`, and `tts.declan_voice_manager` stable; inspect persistent storage and source protocol compatibility before changes.
