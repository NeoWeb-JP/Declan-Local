"""Room brighter/darker commands only adjust already-on, dimmable lights."""
import types
import pytest
import test_commands as fixtures
import test_agent_dialogue  # Shared lightweight HA service and storage fixtures.
from jarvis_test.room_brightness import room_brightness
from jarvis_test.planner import plan


def complete(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    finally:
        coroutine.close()
    raise AssertionError('Unexpected suspension in mocked service call')


@pytest.mark.parametrize('phrase,expected', [
    ('make the kitchen lighter',65), ('make the kitchen light',65),
    ('make kitchen brighter',65), ('make the kitchen darker',35)])
def test_named_room_adjustment(phrase,expected):
    hass=fixtures.Hass();hass.data={}
    step=room_brightness(hass,phrase)
    assert step['calls'] == [{'service':'turn_on','data':{'entity_id':['light.kitchen'],'brightness_pct':expected}}]
    assert hass.states.get('light.kitchen').attributes['brightness'] == 128


def test_current_room_and_preview_route():
    hass=fixtures.Hass();hass.data={}
    area=hass.areas.entries['kitchen']
    steps,preview=plan(hass,'preview make the room darker',area)
    assert preview is True
    assert steps[0]['calls'][0]['data']['brightness_pct'] == 35
    assert room_brightness(hass,'make it lighter',area)['calls'][0]['data']['brightness_pct'] == 65
    with pytest.raises(ValueError,match='Which room'):
        room_brightness(hass,'make the room darker')


def add_light(hass,entity,state='on',modes=('brightness',),brightness=128):
    item=fixtures.State(entity,entity,state,modes)
    item.attributes['brightness']=brightness
    hass.states.values[entity]=item
    hass.entities.entries[entity]=types.SimpleNamespace(area_id='kitchen',device_id=None,disabled_by=None,hidden_by=None,aliases=set())


def test_mixed_room_leaves_off_non_dimmable_unavailable_and_hidden_unchanged():
    hass=fixtures.Hass();hass.data={}
    add_light(hass,'light.off',state='off')
    add_light(hass,'light.binary',modes=('onoff',))
    add_light(hass,'light.unavailable',state='unavailable')
    add_light(hass,'light.unknown_brightness',brightness=None)
    add_light(hass,'light.private');hass.hidden.add('light.private')
    add_light(hass,'light.second',brightness=204)
    calls=room_brightness(hass,'make kitchen darker')['calls']
    assert {call['data']['entity_id'][0] for call in calls} == {'light.kitchen','light.second'}
    assert {call['data']['brightness_pct'] for call in calls} == {35,65}


@pytest.mark.parametrize('brightness,direction,service,percent',[
    (250,'lighter','turn_on',100),(10,'darker','turn_off',None)])
def test_brightness_limits(brightness,direction,service,percent):
    hass=fixtures.Hass();hass.data={}
    hass.states.get('light.kitchen').attributes['brightness']=brightness
    call=room_brightness(hass,'make kitchen '+direction)['calls'][0]
    assert call['service'] == service
    assert call['data'].get('brightness_pct') == percent


def test_no_eligible_lights_is_no_action_and_unknown_room_never_broadens_scope():
    hass=fixtures.Hass();hass.data={}
    hass.states.get('light.kitchen').state='off'
    assert room_brightness(hass,'make kitchen lighter')['kind'] == 'text'
    for phrase in ('make missing room darker','make all rooms lighter'):
        with pytest.raises(ValueError):room_brightness(hass,phrase)


def test_unrelated_phrases_are_not_captured():
    hass=fixtures.Hass()
    assert room_brightness(hass,'turn on kitchen lamp') is None
    assert room_brightness(hass,'do not make kitchen darker') is None


def test_agent_uses_source_room_and_preview_calls_no_services():
    import test_agent_dialogue as dialogue
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        case.hass.devices.entries['voice-device']=types.SimpleNamespace(area_id='kitchen')
        preview=dialogue.UserInput('preview make the room darker',device='voice-device')
        complete(case.agent.async_handle(preview))
        assert case.hass.services.calls == []
        complete(case.agent.async_handle(dialogue.UserInput('make the room lighter',device='voice-device')))
        args,kwargs=case.hass.services.calls[0]
        assert args == ('light','turn_on',{'entity_id':['light.kitchen'],'brightness_pct':65})
    finally:case.doCleanups()


@pytest.mark.parametrize('phrase,expected', [('too bright',35),('too dark',65),('too bright in the kitchen',35)])
def test_natural_adjustments(phrase,expected):
    hass=fixtures.Hass();hass.data={}
    step=room_brightness(hass,phrase,hass.areas.entries['kitchen'])
    assert step['calls'][0]['data']['brightness_pct'] == expected


def test_undo_restores_each_light_and_rejects_intervening_changes():
    from jarvis_test.room_brightness import undo_room_brightness
    hass=fixtures.Hass();hass.data={}
    add_light(hass,'light.second',brightness=204)
    step=room_brightness(hass,'make kitchen darker')
    saved={'room':'Kitchen','before':step['undo_before'],'after':step['undo_after']}
    for entity,expected in step['undo_after'].items():
        hass.states.get(entity).state=expected['state']
        hass.states.get(entity).attributes['brightness']=expected['brightness']
    undo=undo_room_brightness(hass,saved)
    assert {call['data']['entity_id'][0]:call['data']['brightness'] for call in undo['calls']} == {'light.kitchen':128,'light.second':204}
    hass.states.get('light.second').attributes['brightness']=20
    with pytest.raises(ValueError,match='changed'):
        undo_room_brightness(hass,saved)


def test_agent_undo_is_scoped_previewable_single_use_and_expires():
    import test_agent_dialogue as dialogue
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        case.hass.devices.entries['voice-device']=types.SimpleNamespace(area_id='kitchen')
        original_call=case.hass.services.async_call
        async def update(domain,service,data,**kwargs):
            await original_call(domain,service,data,**kwargs)
            for entity in data['entity_id']:
                state=case.hass.states.get(entity)
                state.state='off' if service=='turn_off' else 'on'
                if 'brightness_pct' in data:state.attributes['brightness']=round(data['brightness_pct']/100*255)
                if 'brightness' in data:state.attributes['brightness']=data['brightness']
        case.hass.services.async_call=update
        def request(text,cid='one'):
            return complete(case.agent.async_handle(dialogue.UserInput(text,cid,device='voice-device')))
        request('too bright')
        count=len(case.hass.services.calls)
        request('undo that','other')
        request('preview undo that')
        assert len(case.hass.services.calls) == count
        request('undo that')
        assert case.hass.states.get('light.kitchen').attributes['brightness'] == 128
        count=len(case.hass.services.calls)
        request('undo that')
        assert len(case.hass.services.calls) == count
        request('too dark')
        for snapshot in case.agent._brightness_undo.values():snapshot['at'] -= 121
        count=len(case.hass.services.calls)
        request('undo that')
        assert len(case.hass.services.calls) == count
    finally:case.doCleanups()

