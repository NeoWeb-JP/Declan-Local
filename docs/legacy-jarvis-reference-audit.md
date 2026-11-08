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
