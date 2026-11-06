"""Focused review-only learning, room context and recognition regression tests."""
from types import SimpleNamespace

from custom_components.declan_local.learning import (
    speech_variants, failure_category, suggestions, observe)
from custom_components.declan_local.conversation_memory import context_followup, context_key
from custom_components.declan_local.transcript import recognition_diagnostic


def test_similar_approved_speech_only_suggested():
    hass = SimpleNamespace(data={'declan_local': {
        'debug_enabled': True,
        'approved_aliases': {'very light off': 'turn off fairy lights'}}})
    for _ in range(2):
        observe(hass, {'outcome': 'rejected', 'received_text': 'very lights off',
                       'error': 'I did not understand'})
    result = suggestions(hass)
    assert result[0]['similar_approved'][0]['suggested'] == 'turn off fairy lights'
    assert 'very lights off' not in hass.data['declan_local']['approved_aliases']
    assert speech_variants('completely unrelated', hass.data['declan_local']['approved_aliases']) == []


def test_device_fault_is_not_misclassified_as_stt():
    assert failure_category('Media player unavailable') == 'device_or_service'
    assert failure_category('Which room?') == 'clarification'
    assert failure_category('I did not understand') == 'unrecognised_command'


def test_same_action_other_room_requires_verified_context():
    previous = {'action': 'turn_off', 'ids': ['light.lounge']}
    assert context_followup('do the same in the kitchen', previous) == 'turn off the lights in kitchen'
    assert context_followup('do the same in all rooms', previous) is None
    assert context_followup('do the same in the kitchen', {'action': None}) is None
    assert context_followup('do the same in the kitchen', None) is None


def test_identity_scope_isolated():
    user = SimpleNamespace(context=SimpleNamespace(user_id=None),
                           satellite_id='satellite.kitchen', device_id=None)
    a = context_key(user, 'conversation', 'jaco')
    b = context_key(user, 'conversation', 'edd')
    assert a != b


def test_voice_diagnostics_never_infer_microphone_gain():
    result = recognition_diagnostic('very light off', 'very light off', [],
                                    'rejected', 'I did not understand', 'kitchen')
    assert result['stage'] == 'command_understanding'
    assert result['satellite'] is True
    assert 'gain' not in result
    assert recognition_diagnostic('play', 'play', [], 'failed',
                                  'player unavailable')['stage'] == 'device_or_service'
