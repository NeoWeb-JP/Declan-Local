"""Learning observations are opt-in and never change command behaviour."""
from types import SimpleNamespace
from custom_components.jarvis_local.learning import observe, summary, suggestions, resolve_alias, normalize_alias


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


def test_repeated_failures_become_review_only_candidates():
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    for _ in range(2):
        observe(hass, {'outcome': 'rejected', 'received_text': 'switch the snuggly lights',
                       'error': 'unknown target'})
    assert suggestions(hass) == [{'type': 'repeated_failure',
                                   'heard': 'switch the snuggly lights',
                                   'count': 2, 'reason': 'unknown target'}]
    assert 'learned_commands' not in hass.data['jarvis_local']


def test_successful_corrections_need_repeated_evidence():
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    record = {'outcome': 'completed', 'received_text': 'turn on kitchen, actually turn on lounge',
              'resolved_text': 'turn on lounge',
              'transcript_corrections': ['superseded earlier command']}
    observe(hass, record)
    assert suggestions(hass) == []
    observe(hass, record)
    assert suggestions(hass)[0]['suggested'] == 'turn on lounge'


def test_preview_and_disabled_debug_never_generate_candidates():
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    for _ in range(3):
        observe(hass, {'outcome': 'failed', 'received_text': 'play jazz', 'preview': True})
    assert suggestions(hass) == []


def test_exact_approved_alias_only():
    hass = SimpleNamespace(data={'jarvis_local': {
        'approved_aliases': {'turn the cosy lights on': 'turn on lounge lights'}})
    assert resolve_alias(hass, '  TURN  the cosy lights ON ') == 'turn on lounge lights'
    assert resolve_alias(hass, 'turn the cosy lights off') == 'turn the cosy lights off'
    assert resolve_alias(hass, 'turn the cosy lights on and unlock door') == 'turn the cosy lights on and unlock door'


def test_alias_validation_rejects_non_plain_text():
    import pytest
    with pytest.raises(ValueError):
        normalize_alias('turn on <script>')
