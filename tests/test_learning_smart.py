"""Suggested corrections stay editable, grounded and explicitly approved."""
import sys
from types import SimpleNamespace, ModuleType
import pytest
import test_commands as fixtures
from custom_components.jarvis_local import learning


def complete(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    finally:
        coroutine.close()
    raise AssertionError('Unexpected suspension')


def test_inventory_choices_never_execute_or_include_hidden_lights():
    hass = fixtures.Hass()
    hass.data = {'jarvis_local': {'debug_enabled': True}}
    learning.observe(hass, {'outcome': 'rejected', 'received_text': 'kitchen lanp off'})
    options = learning.suggestions(hass)[0]['options']
    assert options[0]['command'] == 'turn off kitchen lamp'
    assert all('hidden' not in choice['command'] for choice in options)
    assert learning.resolve_alias(hass, 'kitchen lanp off') == 'kitchen lanp off'
    assert learning.command_suggestions(hass, "don't turn kitchen lamp off", []) == []


def test_voice_pair_is_reviewable_after_one_success_and_keeps_original_phrase():
    hass = SimpleNamespace(data={'jarvis_local': {'debug_enabled': True}})
    learning.observe(hass, {'outcome': 'rejected', 'received_text': 'very lights off'})
    learning.observe(hass, {'outcome': 'completed', 'received_text': 'very lights off',
        'resolved_text': 'turn off fairy lights', 'transcript_corrections': ['voice correction']})
    pending = learning.suggestions(hass)
    assert len(pending) == 1
    assert pending[0]['source'] == 'voice'
    assert pending[0]['suggested'] == 'turn off fairy lights'
    assert learning.resolve_alias(hass, 'very lights off') == 'very lights off'


def test_natural_spoken_correction_requires_explicit_action():
    from custom_components.jarvis_local.cross_corrections import corrected_followup
    previous = {'outcome': 'rejected'}
    assert corrected_followup('no I meant fairy lights off', previous) == 'turn off fairy lights'
    with pytest.raises(ValueError):
        corrected_followup('no I meant fairy lights', previous)
    assert corrected_followup('no I meant fairy lights off', None) is None


def test_edited_known_light_can_be_taught_but_unsafe_targets_cannot(monkeypatch):
    hass = fixtures.Hass()
    hass.data = {'jarvis_local': {'debug_enabled': True}}
    learning.observe(hass, {'outcome': 'rejected', 'received_text': 'kitchen lanp off'})
    saved = []
    module = ModuleType('homeassistant.helpers.storage')
    class Store:
        def __init__(self, *args): pass
        async def async_save(self, value): saved.append(value)
    module.Store = Store
    monkeypatch.setitem(sys.modules, module.__name__, module)
    complete(learning.review(hass, 'kitchen lanp off', 'approve_manual', 'turn off kitchen lamp'))
    assert learning.resolve_alias(hass, 'kitchen lanp off') == 'turn off kitchen lamp'
    assert saved[-1]['approved']
    assert learning.suggestions(hass) == []
    for target in ('unlock door', 'turn off all lights', 'turn off missing lamp'):
        with pytest.raises(ValueError):
            learning.validate_taught_command(hass, target)


def test_agent_links_voice_correction_only_in_same_conversation():
    import test_agent_dialogue as dialogue
    case = dialogue.Dialogue('test_other_conversation_cannot_answer')
    case.setUp()
    try:
        case.hass.data = {'jarvis_local': {'debug_enabled': True}}
        complete(case.agent.async_handle(dialogue.UserInput('kitchen lanp off', 'voice')))
        complete(case.agent.async_handle(dialogue.UserInput('no I meant turn off kitchen lamp', 'voice')))
        from jarvis_test.learning import suggestions
        pending = suggestions(case.hass)
        assert any(item.get('source') == 'voice' and item['heard'] == 'kitchen lanp off' for item in pending)
        assert not case.hass.data['jarvis_local'].get('approved_aliases')
        complete(case.agent.async_handle(dialogue.UserInput('another garbled command', 'first')))
        complete(case.agent.async_handle(dialogue.UserInput('no I meant turn off kitchen lamp', 'second')))
        assert not any(item.get('source') == 'voice' and item['heard'] == 'another garbled command'
                       for item in suggestions(case.hass))
    finally:
        case.doCleanups()

