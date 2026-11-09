"""Declan Spotify discovery, favourites, exclusions and rotating playback."""
import asyncio
import json
import logging
from datetime import timedelta
from time import monotonic, perf_counter

import aiohttp
import voluptuous as vol
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store

from .music_assistant_voice import ROOMS
from .music_variety import choose_playlist, updated_history
from .spotify_discovery import QUERIES, SpotifyRateLimited, curate, credentials, search, uri

_LOGGER = logging.getLogger(__name__)
DOMAIN = "declan_local"


async def async_register(hass):
    catalogue_store = Store(hass, 1, "jarvis_local.spotify_categories")
    history_store = Store(hass, 1, "jarvis_local.music_history")
    preference_store = Store(hass, 1, "declan_local.music_preferences")
    lock = asyncio.Lock()
    refresh_lock = asyncio.Lock()
    # Keep requests within a category ordered, without blocking other categories.
    category_locks = {category: asyncio.Lock() for category in QUERIES}
    # Warmed lazily, then reused for voice playback. All writes are under lock.
    cached_catalogue = None
    cached_history = None
    cached_weights = None
    discovery_retry_at = 0.0

    async def load():
        nonlocal cached_catalogue
        if cached_catalogue is not None:
            return cached_catalogue
        saved = await catalogue_store.async_load()
        if isinstance(saved, dict):
            found = {key: (saved.get(key) or {}).get("discovered", []) for key in QUERIES}
            cached_catalogue = curate(saved, found)
            return cached_catalogue
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
        cached_catalogue = curate(pins, {})
        return cached_catalogue

    async def refresh(call=None):
        nonlocal cached_catalogue, discovery_retry_at
        # Spotify discovery can take seconds. Never hold the playback/cache
        # lock while waiting on remote API calls.
        async with refresh_lock:
            if monotonic() < discovery_retry_at:
                _LOGGER.info("Spotify discovery skipped during rate-limit cooldown")
                if call is not None:
                    raise HomeAssistantError("Spotify discovery is rate limited; try again later")
                return
            try:
                client_id, secret = await credentials(hass)
                discovered = await search(hass, client_id, secret)
                # Merge against the latest catalogue under lock so edits made
                # during discovery are not overwritten by stale favourites.
                async with lock:
                    updated = curate(await load(), discovered, capacity=25)
                    await catalogue_store.async_save(updated)
                    cached_catalogue = updated
                discovery_retry_at = 0.0
                _LOGGER.info("Declan refreshed %d Spotify music categories", len(updated))
            except SpotifyRateLimited as exc:
                discovery_retry_at = monotonic() + exc.retry_after
                _LOGGER.warning("Spotify discovery rate limited; retry no sooner than %d seconds", exc.retry_after)
                if call is not None:
                    raise HomeAssistantError("Spotify discovery rate limited; existing playlists retained") from exc
            except (OSError, KeyError, ValueError, aiohttp.ClientError, asyncio.TimeoutError) as exc:
                _LOGGER.warning("Spotify discovery failed (%s); previous catalogue retained", type(exc).__name__)
                if call is not None:
                    raise HomeAssistantError("Spotify discovery failed; check API credentials and access") from exc

    async def edit(call):
        nonlocal cached_catalogue
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
            cached_catalogue = catalogue

    async def prefer(call):
        nonlocal cached_weights
        playlist = uri(call.data["playlist"])
        if not playlist:
            raise HomeAssistantError("A valid Spotify playlist URI is required")
        operation = call.data["operation"]
        async with lock:
            if cached_weights is None:
                saved = await preference_store.async_load() or {}
                cached_weights = saved.get("playlists", {})
            weights = dict(cached_weights)
            if not isinstance(weights, dict):
                weights = {}
            current = max(1, min(5, int(weights.get(playlist, 1))))
            weights[playlist] = (min(5, current + 1) if operation == "like"
                                 else max(1, current - 1) if operation == "dislike"
                                 else 1)
            await preference_store.async_save({"playlists": weights})
            cached_weights = weights

    async def play(call):
        nonlocal cached_history, cached_weights
        category = call.data["category"].lower().strip().replace(" ", "_")
        room = call.data["room"]
        if category not in QUERIES or room not in ROOMS:
            raise HomeAssistantError("Unknown music category or room")
        entity = ROOMS[room]
        state = hass.states.get(entity)
        if state is None or state.state in ("unavailable", "unknown"):
            raise HomeAssistantError("Music player unavailable")
        started = perf_counter()
        # Serialize the same category through selection, dispatch and history
        # persistence. Other categories can dispatch while this one waits.
        async with category_locks[category]:
            async with lock:
                catalogue = await load()
                pool = {name: item["playlists"] for name, item in catalogue.items()}
                if cached_history is None:
                    cached_history = await history_store.async_load() or {}
                if cached_weights is None:
                    saved_preferences = await preference_store.async_load() or {}
                    cached_weights = saved_preferences.get("playlists", {})
                try:
                    selected = choose_playlist(category, pool, cached_history, weights=cached_weights)
                except ValueError as exc:
                    raise HomeAssistantError(str(exc)) from exc
            selection_ms = round((perf_counter() - started) * 1000)
            dispatch_started = perf_counter()
            # The shared lock is released during the bounded Music Assistant
            # call. A timeout is ambiguous, so do not retry automatically.
            try:
                await asyncio.wait_for(
                    hass.services.async_call(
                        "music_assistant", "play_media",
                        {"media_id": selected, "media_type": "playlist"},
                        target={"entity_id": entity}, blocking=True, context=call.context),
                    timeout=3,
                )
            except asyncio.TimeoutError as exc:
                _LOGGER.warning(
                    "Declan music dispatch timed out category=%s room=%s selection_ms=%d dispatch_ms=%d",
                    category, room, selection_ms, round((perf_counter() - dispatch_started) * 1000),
                )
                raise HomeAssistantError(
                    "Music Assistant did not confirm the playback request in time; "
                    "playback may still start. No automatic retry was made."
                ) from exc
            dispatch_ms = round((perf_counter() - dispatch_started) * 1000)
            # Record accepted requests under the shared lock using the latest
            # history, so concurrent categories cannot overwrite each other.
            async with lock:
                next_history = updated_history(category, selected, cached_history)
                await history_store.async_save(next_history)
                cached_history = next_history
            _LOGGER.info(
                "Declan music dispatch accepted category=%s room=%s selection_ms=%d dispatch_ms=%d",
                category, room, selection_ms, dispatch_ms,
            )

    hass.services.async_register(DOMAIN, "play_music_category", play,
        schema=vol.Schema({vol.Required("category"): str,
                           vol.Optional("room", default="everywhere"): vol.In(sorted(ROOMS))}))
    hass.services.async_register(DOMAIN, "refresh_music_categories", refresh)
    hass.services.async_register(DOMAIN, "rate_music_playlist", prefer,
        schema=vol.Schema({vol.Required("playlist"): str,
                           vol.Required("operation"): vol.In(("like", "dislike", "reset"))}))
    hass.services.async_register(DOMAIN, "manage_music_playlist", edit,
        schema=vol.Schema({vol.Required("category"): str,
                           vol.Required("playlist"): str,
                           vol.Required("operation"): vol.In(("favourite", "exclude", "remove"))}))
    async def scheduled_refresh(now):
        await refresh()

    cancel = async_track_time_interval(hass, scheduled_refresh, timedelta(days=7))
    hass.data.setdefault(DOMAIN, {})["music_refresh_unsub"] = cancel


def async_unregister(hass):
    cancel = hass.data.get(DOMAIN, {}).pop("music_refresh_unsub", None)
    if cancel:
        cancel()
    for service in ("play_music_category", "refresh_music_categories", "manage_music_playlist", "rate_music_playlist"):
        hass.services.async_remove(DOMAIN, service)
