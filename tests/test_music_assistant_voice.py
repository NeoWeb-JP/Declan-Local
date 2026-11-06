"""Focused tests for explicit-room Music Assistant requests."""
import pytest
from types import SimpleNamespace
from custom_components.declan_local.music_assistant_voice import plan_music

class States:
    def get(self, entity_id):
        return SimpleNamespace(state="idle")

def test_artist_and_room():
    step = plan_music(SimpleNamespace(states=States()), "play Norah Jones in the kitchen")
    assert step["data"] == {"media_id": "Norah Jones", "media_type": "artist"}
    assert step["entity_id"] == "media_player.kitchen_declan_voice_assistant"

def test_track_artist_filter():
    step = plan_music(SimpleNamespace(states=States()), "play Bohemian Rhapsody by Queen in the bedroom")
    assert step["data"] == {"media_id": "Bohemian Rhapsody", "media_type": "track", "artist": "Queen"}

def test_no_room_does_not_guess():
    with pytest.raises(ValueError, match="Which room"):
        plan_music(SimpleNamespace(states=States()), "play Norah Jones")

def test_missing_player_fails_without_action():
    hass = SimpleNamespace(states=SimpleNamespace(get=lambda _: None))
    with pytest.raises(ValueError, match="unavailable"):
        plan_music(hass, "play Queen everywhere")

def test_bedroom_and_groups():
    hass = SimpleNamespace(states=States())
    assert plan_music(hass, "play Queen in the bedroom")["entity_id"] == "media_player.bedroom_declan_voice_assistant"
    assert plan_music(hass, "play Queen downstairs")["entity_id"] == "media_player.downstairs_2"
    assert plan_music(hass, "play Queen everywhere")["entity_id"] == "media_player.everywhere_2"
