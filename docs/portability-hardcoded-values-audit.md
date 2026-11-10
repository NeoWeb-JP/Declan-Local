# Declan portability audit — Phase 1

Status: initial source audit, 2026-11-08. Baseline: `main`. **Documentation only; no runtime changes.**

## Goal and scope

A new household must be able to install Declan without editing source code or inheriting another household's entities, identities, cameras, scripts, network addresses, or private data. Audit findings are based on source inspection, not runtime confirmation. This is an initial targeted scan of 18 integration files, not yet an exhaustive proof of absence elsewhere.

## Findings and actions

| Priority | Source | Finding | Classification | Proposed remedy / acceptance test |
|---|---|---|---|---|
| P0 | `frigate_faces.py:11` | `ALLOWED = {"jaco": "Jaco", "edd": "Edd"}` | Household-specific identity | Discover configured face identities or opt-in person mapping. Fresh install exposes no named people. Existing installations retain mappings through migration. |
| P0 | `show_cameras.py:18` | `BEDROOM_CAMERA = "camera.master_bedroom_master_bedroom_echo_show_camera_camera"` | Household-specific entity | User-selectable camera mapping or discovery. Missing camera degrades gracefully. |
| P0 | `panel.js:10,439,1119` | Default `conversation.jarvis_local_test` | Legacy entity assumption | Resolve active config entry's conversation entity via registry; preserve registered unique IDs through migration. |
| P1 | `settings.py:8,40,43,102` | `jarvis_local.settings` storage and `jarvis_local_settings.json` legacy import | Persisted storage compatibility | Versioned, idempotent copy-and-verify migration; no destructive rename or loss of existing settings. |
| P1 | `__init__.py:28,31,39` | `jarvis_local.debug`, `jarvis_local.learning_aliases`, `jarvis_voice_id.json` | Persisted data / biometric sensitivity | Keep backward reads during migration, protect speaker identity data from default exports. |
| P1 | `guest_authority.py:10` | `jarvis_local.guest_authority` | Persisted household state | Migrate without re-enabling guest mode or transferring another household's authority. |
| P1 | `music_controller.py:22-24,33` | Legacy music category/history stores, Declan preferences, optional playlist file | Persisted preferences / file coupling | Define optional, portable settings and per-household defaults; do not export playback history by default. |
| P1 | `media_search_config.py:5` | `jarvis_local.media_search` | Persisted provider settings | Versioned storage migration; exclude TMDB credentials from default exports. |
| P1 | `config_flow.py:9,60-66` | Default fallback `tts.jarvis_xtts`; bridge port default `10300` | Obsolete dependency / configurable network | Reconcile with draft PR #47 before changing. Keep host optional and user-configured; no forced Wyoming integration. |
| P1 | `websocket.py:245,256,266` | Legacy voice file, debug store, `jarvis_voice_bridge` integration lookup | Data / compatibility | Migrate persisted data; distinguish optional compatibility detection from mandatory dependency. |
| P2 | `panel.js:118,441,547-555` | Legacy browser localStorage keys for pipeline and quick commands | Per-browser preferences | Preserve or migrate client state without resetting favourites; don't assume one pipeline globally. |
| P2 | `speaker_identity.py:50,104` | `jarvis_speaker` transcript metadata | Wire-format compatibility | Keep until producer and consumer support versioned protocol; no blind rename. |
| P2 | `voice_profiles.py:55` | `.jarvis_voice_id_` temporary filename prefix | Internal compatibility | Low priority; change only after verifying atomic write and migration tests. |
| P2 | `personality.py:207` | Bundled `responses.json` | Default content, not necessarily household-specific | Retain generic defaults, add configurable overrides later. |

## Native Home Assistant design decisions to assess

1. Keep Declan responsible for language understanding, dialogue, personality and routing; map routines to user-selected native HA scripts or automations. Do not ship an automatically enabled set of household actions.
2. Use HA config/options flows and selectors for integration-level settings; use the Declan dashboard for detailed optional feature configuration. Do not duplicate competing sources of truth.
3. Export a versioned, validated **Declan-only** configuration package. Default export excludes secrets, tokens, speaker biometrics, learning transcripts and personal history. Native HA automations/scripts remain owned by HA; offer optional blueprints or explicit export references.
4. Import uses dry-run preview, schema version checks, missing-entity remapping, explicit approval and rollback; never silently overwrite existing HA automations.
5. Optional integrations (Frigate, Spotify, Music Assistant, cameras, EV) must not prevent setup when absent.

## Follow-up audit work

- Expand repository-wide scan to all Python, JavaScript, YAML, JSON and documentation, including scripts and automation examples; record exact paths and references.
- Classify each finding: true household hardcoding vs safe generic default vs protocol compatibility vs historical/test fixture.
- Produce fresh-install test matrix and existing-household upgrade/rollback matrix.
- Coordinate with draft PR #47 (voice fallback), #48 (sidebar entity) and #49 (settings dashboard); avoid conflicting edits.

## Guardrails

This phase does not modify Home Assistant, production settings, entity IDs, persisted storage, STT/TTS, automations or scripts. No merges or deployments without approval.
