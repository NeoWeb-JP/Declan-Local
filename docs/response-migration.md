# Local response ownership and legacy script review

Declan chooses correction, clarification, unmatched-request and music acknowledgments locally. Exact questions, error details and request facts remain in the response. Guest wording never uses the Home-only pool. Quiet hours suppress optional banter; serious, security, device and partial-execution warnings remain direct.

Successful routine actions still call the configured Home Assistant scripts. Their external response text is not treated as a privacy-reviewed acknowledgement: Declan selects a local response. A routine may still speak internally, so review its TTS actions separately to avoid duplicate or private announcements.

## What can be retired

| Legacy component | Condition before retiring |
| --- | --- |
| Duplicate sentence-trigger automations for phrases handled by Declan | Confirm the installed pipeline reaches this agent, all original phrases/rooms remain covered, and the automation contains no unique physical actions. Disable only the duplicate trigger wrapper. |
| An external script used only to select response wording | Clear its `personality_script` setting only after configuring a separate, working `quiet_hours` helper and equivalent time/startup handling. First migrate every other script, automation and dashboard caller. |
| Old personality selector helpers | Retire only when no remaining caller uses them. Local Home/Guest policy does not replace unrelated automation dependencies. |
| Legacy music voice wrappers | Require the music-control update, verified player/room mapping and live playback tests first. Check for rooms and volume scales supported only by the old trigger. |

## What stays

- Scripts performing bedtime, morning, movie, dinner, guest, heating, security, EV or scheduled briefing actions. Local response wording does not replace those actions or schedules.
- Visitor/guest-authority and quiet-hours helpers and their maintenance automations. Personality privacy never grants control privileges.
- A configured `phonetic_script`, and any pronunciation dictionary used by external announcements, until an equivalent pronunciation path and every caller have been migrated.
- Music scripts still used by dashboards or household routines, even if voice playback has moved to Music Assistant.

Current entity states alone cannot prove an automation has no remaining callers. Review current definitions, not only historical exports. Before disabling a candidate, compare its triggers and action payload, search all references (including dashboards), verify quiet-hours behavior after restart, and retain a rollback copy. This change does not disable or deploy anything.

