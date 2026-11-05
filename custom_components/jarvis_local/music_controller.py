"""Shared Home Assistant service for curated, rotating Spotify playlists."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.helpers.storage import Store
from homeassistant.exceptions import HomeAssistantError
from .music_variety import choose_playlist, updated_history
from .music_assistant_voice import ROOMS

_LOGGER = logging.getLogger(__name__)
SERVICE = "play_music_category"
STORAGE_KEY = "jarvis_local.music_history"


async def async_register(hass):
    """Register a reusable service for voice, scripts, dashboards and Tessera."""
    store = Store(hass, 1, STORAGE_KEY)

    async def play(call):
        category = call.data["category"].lower().strip()
        room = call.data["room"].lower().strip()
        entity_id = ROOMS.get(room)
        if not entity_id:
            raise HomeAssistantError("Unknown music room")
        player = hass.states.get(entity_id)
        if player is None or player.state in ("unavailable", "unknown"):
            raise HomeAssistantError("Music player unavailable")
        path = Path(hass.config.path("declan_music_playlists.json"))

        def read_catalogue():
            with path.open(encoding="utf-8") as source:
                return json.load(source)

        try:
            catalogue = await hass.async_add_executor_job(read_catalogue)
        except (OSError, ValueError) as exc:
            raise HomeAssistantError("Music playlist catalogue missing or invalid") from exc
        if not isinstance(catalogue, dict):
            raise HomeAssistantError("Music playlist catalogue must be an object")
        pool = {}
        for key, entry in catalogue.items():
            if isinstance(entry, dict) and isinstance(entry.get("playlists"), list):
                pool[key.lower()] = entry["playlists"]
        history = await store.async_load() or {}
        if not isinstance(history, dict):
            history = {}
        try:
            selected = choose_playlist(category, pool, history, avoid_last=3)
        except ValueError as exc:
            raise HomeAssistantError(str(exc)) from exc
        # Only commit history after the service call completed without error.
        await hass.services.async_call(
            "music_assistant", "play_media",
            {"media_id": selected, "media_type": "playlist"},
            target={"entity_id": entity_id}, blocking=True, context=call.context
        )
        await store.async_save(updated_history(category, selected, history))
        _LOGGER.debug("Started configured music category %s in %s", category, room)

    hass.services.async_register(
        "jarvis_local", SERVICE, play,
        schema=vol.Schema({
            vol.Required("category"): vol.All(str, vol.Length(min=1, max=80)),
            vol.Optional("room", default="everywhere"): vol.In(sorted(ROOMS)),
        }),
    )


def async_unregister(hass):
    hass.services.async_remove("jarvis_local", SERVICE)
