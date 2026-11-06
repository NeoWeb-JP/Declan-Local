"""Learning examples survive restart without becoming executable aliases."""
import json
import sys
from types import SimpleNamespace, ModuleType
import pytest
from custom_components.declan_local.learning import (
    load_evidence, flush_evidence, observe, suggestions, resolve_alias)


def complete(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    finally:
        coroutine.close()
    raise AssertionError('Unexpected suspension in fake storage')


@pytest.fixture
def storage(monkeypatch, tmp_path):
    path = tmp_path / 'learning.json'
    class Store:
        def __init__(self, hass, version, key):
            assert key == 'jarvis_local.learning_evidence'
            self.pending = None
        async def async_load(self):
            return json.loads(path.read_text()) if path.exists() else None
        def async_delay_save(self, callback, delay):
            assert delay == 1
            self.pending = callback
        async def async_save(self, value):
            path.write_text(json.dumps(value))
            self.pending = None
    module = ModuleType('homeassistant.helpers.storage')
    module.Store = Store
    monkeypatch.setitem(sys.modules, module.__name__, module)
    return path


def test_restart_restores_waiting_and_review_decisions(storage):
    first = SimpleNamespace(data={'declan_local': {'debug_enabled': True}})
    complete(load_evidence(first))
    for heard in ('waiting command', 'approved command', 'rejected command'):
        observe(first, {'outcome': 'failed', 'received_text': heard})
    complete(flush_evidence(first))
    restarted = SimpleNamespace(data={'declan_local': {
        'debug_enabled': False,
        'approved_aliases': {'approved command': 'turn off fairy lights'},
        'rejected_aliases': ['rejected command']}})
    complete(load_evidence(restarted))
    assert [item['heard'] for item in suggestions(restarted)] == ['waiting command']
    assert resolve_alias(restarted, 'waiting command') == 'waiting command'
    assert resolve_alias(restarted, 'approved command') == 'turn off fairy lights'
    observe(restarted, {'outcome': 'failed', 'received_text': 'not collected'})
    assert len(restarted.data['declan_local']['learning_evidence']) == 3


def test_delayed_callback_uses_latest_bounded_evidence(storage):
    hass = SimpleNamespace(data={'declan_local': {'debug_enabled': True}})
    complete(load_evidence(hass))
    for i in range(50):
        observe(hass, {'outcome': 'rejected', 'received_text': f'command {i}'})
    store = hass.data['declan_local']['learning_evidence_store']
    complete(store.async_save(store.pending()))
    fresh = SimpleNamespace(data={})
    complete(load_evidence(fresh))
    assert len(suggestions(fresh)) == 40
    assert fresh.data['declan_local']['learning_evidence'][0]['heard'] == 'command 10'


@pytest.mark.parametrize('saved', [None, [], {'examples': 'bad'},
    {'examples': [None, {}, {'heard': 42, 'outcome': 'failed'}]}])
def test_malformed_saved_examples_are_ignored(storage, saved):
    storage.write_text(json.dumps(saved))
    hass = SimpleNamespace(data={})
    complete(load_evidence(hass))
    assert suggestions(hass) == []


def test_corrupt_json_does_not_prevent_startup(storage):
    storage.write_text('{broken')
    hass = SimpleNamespace(data={})
    complete(load_evidence(hass))
    assert suggestions(hass) == []


def test_previews_and_disabled_collection_do_not_schedule_writes(storage):
    hass = SimpleNamespace(data={'declan_local': {'debug_enabled': False}})
    complete(load_evidence(hass))
    observe(hass, {'outcome': 'failed', 'received_text': 'private command'})
    hass.data['declan_local']['debug_enabled'] = True
    observe(hass, {'outcome': 'failed', 'received_text': 'preview command', 'preview': True})
    assert hass.data['declan_local']['learning_evidence_store'].pending is None

