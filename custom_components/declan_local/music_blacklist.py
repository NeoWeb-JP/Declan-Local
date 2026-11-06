"""Persistent household track exclusions with conservative playback enforcement."""
import asyncio
import re

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store

from .music_assistant_voice import ROOMS

KEY = "declan_local.music_blacklist"
URI = re.compile(r"(?:spotify:track:|open\.spotify\.com/track/)([A-Za-z0-9]{22})")


def track_details(state):
    if state is None or state.state not in {"playing", "paused"}:
        return None
    attrs = state.attributes
    title = attrs.get("media_title")
    artist = attrs.get("media_artist")
    if not isinstance(title, str) or not title.strip() or not isinstance(artist, str) or not artist.strip():
        return None
    identifier = attrs.get("media_content_id") or attrs.get("media_id") or ""
    match = URI.search(str(identifier))
    return {"title": title.strip(), "artist": artist.strip(),
            "spotify_id": match.group(1) if match else None}


def track_key(track):
    if track["spotify_id"]:
        return "spotify:" + track["spotify_id"]
    return "name:" + track["artist"].casefold() + "\0" + track["title"].casefold()


def excluded(track, entries):
    key = track_key(track)
    fallback = "name:" + track["artist"].casefold() + "\0" + track["title"].casefold()
    return key in entries or fallback in entries


class MusicBlacklist:
    def __init__(self, hass):
        self.hass = hass
        self.store = Store(hass, 1, KEY)
        self.entries = {}
        self.lock = asyncio.Lock()
        self.unsubscribe = None
        self.inflight = set()

    async def start(self):
        saved = await self.store.async_load()
        self.entries = saved.get("tracks", {}) if isinstance(saved, dict) and isinstance(saved.get("tracks"), dict) else {}
        self.unsubscribe = async_track_state_change_event(
            self.hass, list(set(ROOMS.values())), self._on_change)

    async def stop(self):
        if self.unsubscribe:
            self.unsubscribe()
            self.unsubscribe = None

    async def change(self, entity_id, operation, context=None):
        state = self.hass.states.get(entity_id)
        track = track_details(state)
        if track is None:
            raise ValueError("I cannot identify the current song and artist. Nothing was changed.")
        key = track_key(track)
        async with self.lock:
            if operation == "ban":
                self.entries[key] = track
            elif operation == "unban":
                self.entries.pop(key, None)
                self.entries.pop("name:" + track["artist"].casefold() + "\0" + track["title"].casefold(), None)
            else:
                raise ValueError("Unsupported blacklist operation.")
            await self.store.async_save({"tracks": self.entries})
        if operation == "ban" and state.state == "playing":
            await self._skip(entity_id, context)
        return track

    async def _skip(self, entity_id, context=None):
        if entity_id in self.inflight:
            return
        self.inflight.add(entity_id)
        try:
            await self.hass.services.async_call("media_player", "media_next_track",
                {"entity_id": entity_id}, blocking=True, context=context)
        finally:
            self.inflight.discard(entity_id)

    @callback
    def _on_change(self, event):
        entity_id = event.data.get("entity_id")
        state = event.data.get("new_state")
        track = track_details(state)
        if track and state.state == "playing" and excluded(track, self.entries) and entity_id not in self.inflight:
            self.hass.async_create_task(self._skip(entity_id))
