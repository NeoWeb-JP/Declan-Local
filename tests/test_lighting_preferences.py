"""Saved lighting preferences survive restart and remain room-scoped."""
import json
import sys
from types import ModuleType
import pytest
import test_commands as fixtures
import test_agent_dialogue as dialogue
from jarvis_test.lighting_preferences import preference_request, prepare_preference, save_preference


def complete(coroutine):
    try:coroutine.send(None)
    except StopIteration as result:return result.value
    finally:coroutine.close()
    raise AssertionError('Unexpected suspension in fake storage')


@pytest.fixture
def stored(monkeypatch,tmp_path):
    path=tmp_path/'preferences.json'
    module=ModuleType('homeassistant.helpers.storage')
    class Store:
        def __init__(self,hass,version,key):assert key=='jarvis_local.lighting_preferences'
        async def async_load(self):return json.loads(path.read_text()) if path.exists() else None
        async def async_save(self,value):path.write_text(json.dumps(value))
    module.Store=Store;monkeypatch.setitem(sys.modules,module.__name__,module)
    return path


def request(hass,text,room='kitchen'):
    return preference_request(hass,text,hass.areas.entries[room])


def test_remember_restart_recall_and_room_isolation(stored):
    hass=fixtures.Hass();hass.data={}
    complete(save_preference(hass,request(hass,'remember these lights as cosy')))
    fresh=fixtures.Hass();fresh.data={}
    fresh.states.get('light.kitchen').state='off'
    step=complete(prepare_preference(fresh,request(fresh,'make it cosy')))
    assert step['calls']==[{'service':'turn_on','data':{'entity_id':['light.kitchen'],'brightness':128}}]
    with pytest.raises(ValueError,match='no cosy'):
        complete(prepare_preference(fresh,request(fresh,'make it cosy','bedroom')))
    with pytest.raises(ValueError,match='Which room'):
        preference_request(fresh,'make it cosy')


def test_remember_wont_overwrite_and_update_is_explicit(stored):
    hass=fixtures.Hass();hass.data={}
    complete(save_preference(hass,request(hass,'remember these lights as cosy')))
    hass.states.get('light.kitchen').state='off'
    with pytest.raises(ValueError,match='already exists'):
        complete(save_preference(hass,request(hass,'remember these lights as cosy')))
    complete(save_preference(hass,request(hass,'update cosy')))
    restored=complete(prepare_preference(hass,request(hass,'make it cosy')))
    assert restored['calls']==[{'service':'turn_off','data':{'entity_id':['light.kitchen']}}]


def test_hidden_or_moved_saved_light_is_rejected_before_restore(stored):
    hass=fixtures.Hass();hass.data={}
    complete(save_preference(hass,request(hass,'remember these lights as cosy')))
    hass.hidden.add('light.kitchen')
    with pytest.raises(ValueError,match='no longer exposed'):
        complete(prepare_preference(hass,request(hass,'make it cosy')))


def test_unavailable_or_unknown_brightness_cannot_be_saved(stored):
    hass=fixtures.Hass();hass.data={}
    hass.states.get('light.kitchen').attributes['brightness']=None
    with pytest.raises(ValueError,match='unknown brightness'):
        complete(save_preference(hass,request(hass,'remember these lights as cosy')))
    assert not stored.exists()


def test_agent_preview_save_update_and_restore(stored):
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        area=case.hass.areas.entries['kitchen']
        def command(text):return complete(case.agent.async_handle(dialogue.UserInput(text),area))
        command('preview remember these lights as cosy')
        assert not stored.exists()
        command('remember these lights as cosy')
        assert stored.exists() and case.hass.services.calls==[]
        command('preview make it cosy')
        assert case.hass.services.calls==[]
        command('make it cosy')
        assert case.hass.services.calls[0][0]==('light','turn_on',{'entity_id':['light.kitchen'],'brightness':128})
    finally:case.doCleanups()


def test_brightness_commands_are_not_stolen_by_preferences():
    hass=fixtures.Hass()
    assert request(hass,'make it lighter') is None
    assert request(hass,'make it darker') is None

