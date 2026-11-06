"""Cross-turn correction and music transport regression checks."""
from types import SimpleNamespace
import pytest

from custom_components.declan_local.cross_corrections import corrected_followup
from custom_components.declan_local.music_assistant_voice import plan_music_transport, plan_stop_music


def test_correction_only_after_failure_and_explicit_full_request():
    previous = {'outcome': 'rejected'}
    assert corrected_followup('no I meant turn on the kitchen lights', previous) == 'turn on the kitchen lights'
    assert corrected_followup('no I meant turn on the kitchen lights', {'outcome': 'completed'}) is None
    assert corrected_followup('turn on the kitchen lights', previous) is None
    with pytest.raises(ValueError):
        corrected_followup('no I meant the kitchen', previous)


def test_music_transport_uses_configured_player_and_area():
    hass = SimpleNamespace(states={'media_player.kitchen_declan_voice_assistant':
                                   SimpleNamespace(state='idle')})
    area = SimpleNamespace(name='Kitchen')
    assert plan_music_transport(hass, 'pause music', area)['name'] == 'media_pause'
    assert plan_music_transport(hass, 'resume music', area)['name'] == 'media_play'
    assert plan_music_transport(hass, 'skip track', area)['name'] == 'media_next_track'
    assert plan_music_transport(hass, 'previous song', area)['name'] == 'media_previous_track'
    assert plan_stop_music(hass, 'pause music', area) is None


def test_music_transport_rejects_unknown_room_or_unavailable_player():
    hass = SimpleNamespace(states={})
    with pytest.raises(ValueError):
        plan_music_transport(hass, 'skip music')
    with pytest.raises(ValueError):
        plan_music_transport(hass, 'skip music in kitchen')
