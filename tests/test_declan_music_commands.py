"""Music Assistant command routing regressions (no playback side effects)."""
from types import SimpleNamespace
import pytest
from custom_components.jarvis_local.music_assistant_voice import plan_music


class States:
    def get(self, entity_id):
        return SimpleNamespace(state="idle")


HASS = SimpleNamespace(states=States())


def test_named_room_and_natural_prefix():
    step = plan_music(HASS, "play some Queen in the kitchen")
    assert step["entity_id"] == "media_player.kitchen_declan_voice_assistant"
    assert step["data"] == {"media_id": "Queen", "media_type": "artist"}


def test_roomless_uses_satellite_area():
    step = plan_music(HASS, "play Queen", SimpleNamespace(name="Lounge"))
    assert step["entity_id"] == "media_player.living_room_declan"


def test_explicit_room_overrides_satellite():
    step = plan_music(HASS, "play the song Africa by Toto in the bedroom", SimpleNamespace(name="Kitchen"))
    assert step["data"] == {"media_id": "Africa", "media_type": "track", "artist": "Toto"}
    assert step["entity_id"] == "media_player.bedroom_declan_voice_assistant"


def test_no_room_context_requires_clarification():
    with pytest.raises(ValueError, match="Which room"):
        plan_music(HASS, "play Queen")
