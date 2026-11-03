"""Learning observations are opt-in and never change command behaviour."""
from types import SimpleNamespace
from custom_components.jarvis_local.learning import observe, summary


def test_disabled_debug_keeps_no_evidence():
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': False}})
    observe(hass, {'outcome': 'failed', 'received_text': 'lights on'})
    assert summary(hass)['total'] == 0


def test_bounded_evidence_and_no_successful_plain_commands():
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    observe(hass, {'outcome': 'completed', 'received_text': 'turn on lights'})
    assert summary(hass)['total'] == 0
    for i in range(50):
        observe(hass, {'outcome': 'rejected', 'received_text': f'command {i}', 'error': 'unrecognised'})
    assert summary(hass)['total'] == 40
    assert hass.data['jarvis_local']['learning_evidence'][0]['heard'] == 'command 10'


def test_correction_is_observed_without_adding_device_rules():
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    observe(hass, {'outcome': 'completed', 'received_text': 'lights, actually spotlights',
                   'resolved_text': 'turn on spotlights',
                   'transcript_corrections': ['superseded earlier command']})
    assert summary(hass)['correction_samples'] == 1
    assert 'learned_commands' not in hass.data['jarvis_local']
