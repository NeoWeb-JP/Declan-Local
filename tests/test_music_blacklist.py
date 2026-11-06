"""Household blacklist parsing and track matching regression tests."""
from types import SimpleNamespace
import pytest
from custom_components.declan_local.music_blacklist import track_details, track_key, excluded
from custom_components.declan_local.music_assistant_voice import plan_music_blacklist


def state(title="Africa", artist="Toto", uri="spotify:track:1234567890123456789012"):
    return SimpleNamespace(state="playing", attributes={
        "media_title": title, "media_artist": artist, "media_content_id": uri})


def test_spotify_track_identity():
    track = track_details(state())
    assert track_key(track) == "spotify:1234567890123456789012"


def test_fallback_track_identity():
    track = track_details(state(uri=""))
    assert track_key(track) == "name:toto\\0africa".replace("\\0", "\0")


def test_missing_artist_does_not_ban_unknown_track():
    assert track_details(SimpleNamespace(state="playing", attributes={"media_title": "Africa"})) is None


def test_exclusion_matches_fallback_when_track_has_no_id():
    assert excluded(track_details(state(uri="")), {
        "name:toto\0africa": {"title": "Africa", "artist": "Toto"}})


def test_voice_command_requires_known_current_track():
    class States:
        def get(self, entity):
            return state()
    hass = SimpleNamespace(states=States())
    step = plan_music_blacklist(hass, "never play this song again", SimpleNamespace(name="Kitchen"))
    assert step["operation"] == "ban"
    assert step["entity_id"] == "media_player.kitchen_declan_voice_assistant"


def test_voice_command_does_not_match_skip():
    assert plan_music_blacklist(None, "skip this song") is None


def test_unknown_track_is_rejected():
    hass = SimpleNamespace(states=SimpleNamespace(get=lambda entity: None))
    with pytest.raises(ValueError):
        plan_music_blacklist(hass, "ban this song", SimpleNamespace(name="Kitchen"))
