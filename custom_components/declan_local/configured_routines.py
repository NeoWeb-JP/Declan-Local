"""Plan routines selected by the administrator from Home Assistant entities."""
import re

from .settings import get


def _normalise(text):
    text = str(text or "").strip().casefold()
    text = re.sub(r"^(?:hey\s+)?(?:declan|jarvis)[,\s:]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .!?,")


def plan(hass, text):
    """Return a routine step only for an exact configured phrase match."""
    utterance = _normalise(text)
    if not utterance:
        return None

    routines = get(hass, "routines", [])
    if not isinstance(routines, list):
        return None

    for routine in routines:
        if not isinstance(routine, dict):
            continue
        phrases = routine.get("phrases", [])
        if not isinstance(phrases, list):
            continue
        if not any(_normalise(phrase) == utterance for phrase in phrases):
            continue

        entity_id = routine.get("entity_id", "")
        state = hass.states.get(entity_id) if isinstance(entity_id, str) else None
        if state is None or state.state in {"unknown", "unavailable"}:
            raise ValueError(
                "The configured Home Assistant routine is unavailable. Nothing was run."
            )

        domain = entity_id.split(".", 1)[0]
        data = routine.get("data", {})
        if domain == "automation" and data:
            raise ValueError(
                "Home Assistant automations do not accept routine variables. "
                "Select a script or configure the automation to run without variables. Nothing was run."
            )

        return {
            "kind": "configured_routine",
            "entity_id": entity_id,
            "name": routine.get("name") or entity_id,
            "data": data if isinstance(data, dict) else {},
            "label": "run " + (routine.get("name") or "the configured routine"),
        }
    return None
