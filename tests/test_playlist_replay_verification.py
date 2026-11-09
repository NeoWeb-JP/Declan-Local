"""Playlist state verification, including repeated requests and uncertain metadata."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "declan_local"
spec = importlib.util.spec_from_file_location("declan_music_verify", ROOT / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class State:
    def __init__(self, status="playing", **attributes):
        self.state = status
        self.attributes = attributes


@pytest.mark.asyncio
async def test_repeated_playlist_request_reports_existing_playing_state():
    player = State(media_playlist_uri="spotify://playlist/" + "a" * 22)
    call = AsyncMock()
    hass = types.SimpleNamespace(
        states=types.SimpleNamespace(get=lambda entity: player),
        services=types.SimpleNamespace(async_call=call),
    )
    errors = sys.modules.setdefault("homeassistant.exceptions", types.ModuleType("homeassistant.exceptions"))
    errors.HomeAssistantError = getattr(errors, "HomeAssistantError", type("HomeAssistantError", (Exception,), {}))
    playlist = player.attributes["media_playlist_uri"]
    result = await verify.play_verified_playlist(
        hass, "media_player.kitchen", {"media_id": playlist, "media_type": "playlist"}, None
    )
    assert result == "playing"
    call.assert_awaited_once()


def test_playlist_state_requires_matching_identity():
    playlist = "spotify://playlist/" + "a" * 22
    assert verify._playing_playlist(State(media_playlist_uri=playlist), playlist)
    assert not verify._playing_playlist(State(media_title="A song"), playlist)
    assert not verify._playing_playlist(State(status="idle", media_playlist_uri=playlist), playlist)
    assert not verify._playing_playlist(State(media_playlist_uri="another"), playlist)
