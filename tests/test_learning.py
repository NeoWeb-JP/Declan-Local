"""Learning observations are opt-in and never change command behaviour."""
from types import SimpleNamespace
import pytest
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
        'approved_aliases': {'turn the cosy lights on': 'turn on lounge lights'}}})
    assert resolve_alias(hass, '  TURN  the cosy lights ON ') == 'turn on lounge lights'
    assert resolve_alias(hass, 'turn the cosy lights off') == 'turn the cosy lights off'
    assert resolve_alias(hass, 'turn the cosy lights on and unlock door') == 'turn the cosy lights on and unlock door'


def test_alias_validation_rejects_non_plain_text():
    import pytest
    with pytest.raises(ValueError):
        normalize_alias('turn on <script>')


@pytest.mark.asyncio
async def test_review_approval_persistence_and_removal(monkeypatch):
    import sys
    from custom_components.jarvis_local.learning import review
    saved = []
    class FakeStore:
        def __init__(self, *args): pass
        async def async_save(self, value): saved.append(value)
    from homeassistant.helpers import storage
    monkeypatch.setattr(storage, 'Store', FakeStore)
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    sample = {'outcome': 'completed',
              'received_text': 'turn on kitchen, actually turn on lounge',
              'resolved_text': 'turn on lounge',
              'transcript_corrections': ['superseded earlier command']}
    observe(hass, sample)
    observe(hass, sample)
    await review(hass, sample['received_text'], 'approve', 'turn on lounge')
    assert resolve_alias(hass, sample['received_text']) == 'turn on lounge'
    assert suggestions(hass) == []
    assert saved[-1]['approved']
    await review(hass, sample['received_text'], 'remove')
    assert resolve_alias(hass, sample['received_text']) == sample['received_text']
    assert saved[-1]['approved'] == {}


@pytest.mark.asyncio
async def test_rejected_candidate_cannot_be_approved_without_evidence(monkeypatch):
    from custom_components.jarvis_local.learning import review
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    with pytest.raises(ValueError):
        await review(hass, 'unlock door', 'approve', 'turn on lounge lights')


@pytest.mark.asyncio
async def test_manual_teaching_of_repeated_fairy_light_mishearing(monkeypatch):
    from homeassistant.helpers import storage
    from custom_components.jarvis_local.learning import review
    saved = []
    class FakeStore:
        def __init__(self, *args): pass
        async def async_save(self, value): saved.append(value)
    monkeypatch.setattr(storage, 'Store', FakeStore)
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    for _ in range(2):
        observe(hass, {'outcome': 'rejected', 'received_text': 'very light off.',
                       'error': 'Not understood'})
    assert suggestions(hass)[0]['type'] == 'repeated_failure'
    await review(hass, 'very light off.', 'approve_manual', 'turn off fairy lights')
    assert resolve_alias(hass, 'VERY LIGHT OFF.') == 'turn off fairy lights'
    assert saved[-1]['approved']['very light off.'] == 'turn off fairy lights'
    assert suggestions(hass) == []


@pytest.mark.asyncio
async def test_manual_teaching_rejects_unobserved_or_unsafe_actions():
    from custom_components.jarvis_local.learning import review
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    with pytest.raises(ValueError):
        await review(hass, 'unlock the door', 'approve_manual', 'turn off fairy lights')
    for _ in range(2):
        observe(hass, {'outcome': 'rejected', 'received_text': 'very light off'})
    with pytest.raises(ValueError):
        await review(hass, 'very light off', 'approve_manual', 'unlock front door')
    with pytest.raises(ValueError):
        await review(hass, 'very light off', 'approve_manual', 'turn off all lights')
