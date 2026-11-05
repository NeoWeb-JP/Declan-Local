"""Declan Spotify discovery, favourites, exclusions and rotating playback."""
import asyncio
import json
import logging
from datetime import timedelta

import aiohttp
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store

from .music_assistant_voice import ROOMS
from .music_variety import choose_playlist, updated_history
from .spotify_discovery import QUERIES, curate, credentials, search, uri

_LOGGER = logging.getLogger(__name__)
DOMAIN = "jarvis_local"


async def async_register(hass):
    catalogue_store = Store(hass, 1, "jarvis_local.spotify_categories")
    history_store = Store(hass, 1, "jarvis_local.music_history")
    lock = asyncio.Lock()

    async def load():
        saved = await catalogue_store.async_load()
        if isinstance(saved, dict):
            found = {key: (saved.get(key) or {}).get("discovered", []) for key in QUERIES}
            return curate(saved, found)
        def read():
            with open(hass.config.path("declan_music_playlists.json"), encoding="utf-8") as stream:
                return json.load(stream)
        try:
            legacy = await hass.async_add_executor_job(read)
        except (OSError, ValueError):
            legacy = {}
        pins = {}
        for category in QUERIES:
            item = legacy.get(category, {}) if isinstance(legacy, dict) else {}
            if isinstance(item, dict):
                pins[category] = {"favourites": item.get("favourites", item.get("playlists", [])),
                                  "excluded": item.get("excluded", [])}
        return curate(pins, {})

    async def refresh(call=None):
        async with lock:
            try:
                client_id, secret = await credentials(hass)
                discovered = await search(hass, client_id, secret)
                updated = curate(await load(), discovered, capacity=25)
                await catalogue_store.async_save(updated)
                _LOGGER.info("Declan refreshed %d Spotify music categories", len(updated))
            except (OSError, KeyError, ValueError, aiohttp.ClientError, asyncio.TimeoutError) as exc:
                _LOGGER.warning("Spotify discovery failed (%s); previous catalogue retained", type(exc).__name__)
                if call is not None:
                    raise HomeAssistantError("Spotify discovery failed; check API credentials and access") from exc

    async def edit(call):
        category = call.data["category"].lower().strip().replace(" ", "_")
        selected = uri(call.data["playlist"])
        if category not in QUERIES or not selected:
            raise HomeAssistantError("Unknown category or invalid Spotify playlist")
        async with lock:
            catalogue = await load()
            item = catalogue[category]
            for field in ("favourites", "excluded", "discovered"):
                item[field] = [x for x in item[field] if x != selected]
            if call.data["operation"] == "favourite":
                item["favourites"].append(selected)
            elif call.data["operation"] == "exclude":
                item["excluded"].append(selected)
            item["playlists"] = [x for x in item["favourites"] + item["discovered"]
                                 if x not in item["excluded"]]
            await catalogue_store.async_save(catalogue)

    async def play(call):
        category = call.data["category"].lower().strip().replace(" ", "_")
        room = call.data["room"]
        if category not in QUERIES or room not in ROOMS:
            raise HomeAssistantError("Unknown music category or room")
        entity = ROOMS[room]
        state = hass.states.get(entity)
        if state is None or state.state in ("unavailable", "unknown"):
            raise HomeAssistantError("Music player unavailable")
        async with lock:
            catalogue = await load()
            pool = {name: item["playlists"] for name, item in catalogue.items()}
            history = await history_store.async_load() or {}
            try:
                selected = choose_playlist(category, pool, history)
            except ValueError as exc:
                raise HomeAssistantError(str(exc)) from exc
            await hass.services.async_call(
                "music_assistant", "play_media",
                {"media_id": selected, "media_type": "playlist"},
                target={"entity_id": entity}, blocking=True, context=call.context)
            await history_store.async_save(updated_history(category, selected, history))

    hass.services.async_register(DOMAIN, "play_music_category", play,
        schema=vol.Schema({vol.Required("category"): str,
                           vol.Optional("room", default="everywhere"): vol.In(sorted(ROOMS))}))
    hass.services.async_register(DOMAIN, "refresh_music_categories", refresh)
    hass.services.async_register(DOMAIN, "manage_music_playlist", edit,
        schema=vol.Schema({vol.Required("category"): str,
                           vol.Required("playlist"): str,
                           vol.Required("operation"): vol.In(("favourite", "exclude", "remove"))}))
    cancel = async_track_time_interval(hass, refresh, timedelta(days=7))
    hass.data.setdefault(DOMAIN, {})["music_refresh_unsub"] = cancel


def async_unregister(hass):
    cancel = hass.data.get(DOMAIN, {}).pop("music_refresh_unsub", None)
    if cancel:
        cancel()
    for service in ("play_music_category", "refresh_music_categories", "manage_music_playlist"):
        hass.services.async_remove(DOMAIN, service)
