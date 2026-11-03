"""Natural music requests share room routing and preserve preview safety."""
from types import SimpleNamespace
import pytest
import test_commands as fixtures
import test_agent_dialogue as dialogue
from jarvis_test.music_assistant_voice import (
    ROOMS, plan_music, plan_music_transport, plan_stop_music, plan_music_volume, plan_music_status)


def complete(coroutine):
    try:coroutine.send(None)
    except StopIteration as result:return result.value
    finally:coroutine.close()
    raise AssertionError('Unexpected suspension')


def hass():
    value=fixtures.Hass();value.data={}
    for entity in set(ROOMS.values()):
        state=fixtures.State(entity,entity,'playing')
        state.attributes.update(volume_level=0.5,media_title='Africa',media_artist='Toto')
        value.states.values[entity]=state
    return value


@pytest.mark.parametrize('phrase,kind,title,artist',[
    ('play the album Abbey Road by The Beatles in the kitchen','album','Abbey Road','The Beatles'),
    ('play my playlist Dinner downstairs','playlist','Dinner',None),
    ('play song Africa by Toto in bedroom','track','Africa','Toto'),
    ('play artist Queen everywhere','artist','Queen',None)])
def test_playback_types(phrase,kind,title,artist):
    step=plan_music(hass(),phrase)
    assert step['data']['media_type']==kind and step['data']['media_id']==title
    assert step['data'].get('artist')==artist


def test_unknown_explicit_destination_does_not_fall_back_to_source():
    with pytest.raises(ValueError,match='room'):
        plan_music(hass(),'play Queen in the garage',SimpleNamespace(name='Kitchen'))


def test_restart_seeks_to_start_and_transport_case_is_consistent():
    value=hass()
    assert plan_music_transport(value,'restart track in bedroom')['data']['seek_position']==0
    assert plan_music_transport(value,'restart track in bedroom')['name']=='media_seek'
    assert plan_music_transport(value,'skip this song in kitchen')['name']=='media_next_track'
    assert plan_stop_music(value,'stop music in BEDROOM')['data']['entity_id']==ROOMS['bedroom']


def test_volume_routes_to_same_room_and_is_bounded():
    value=hass();area=SimpleNamespace(name='Bedroom')
    assert plan_music_volume(value,'set music volume to 30 percent',area)['data']=={
        'entity_id':ROOMS['bedroom'],'volume_level':0.3}
    assert plan_music_volume(value,'turn it down in kitchen')['data']['volume_level']==0.4
    value.states.get(ROOMS['kitchen']).attributes['volume_level']=0.98
    assert plan_music_volume(value,'louder in kitchen')['data']['volume_level']==1
    with pytest.raises(ValueError):plan_music_volume(value,'set volume to 101 percent',area)
    with pytest.raises(ValueError):plan_music_volume(value,'set volume in garage to 20 percent',area)
    value.states.get(ROOMS['bedroom']).attributes['volume_level']=None
    with pytest.raises(ValueError,match='percentage'):plan_music_volume(value,'turn music down',area)


def test_status_uses_reported_metadata_and_honestly_handles_missing_title():
    value=hass();area=SimpleNamespace(name='Kitchen')
    assert 'Africa by Toto' in plan_music_status(value,"what's playing",area)['response']
    value.states.get(ROOMS['kitchen']).attributes.pop('media_title')
    assert 'not reported' in plan_music_status(value,"what's playing",area)['response']


@pytest.mark.parametrize('room,entity',list(ROOMS.items()))
def test_playback_transport_volume_and_status_share_room_mapping(room,entity):
    value=hass()
    assert plan_music(value,'play Queen in '+room)['entity_id']==entity
    assert plan_music_transport(value,'pause music in '+room)['data']['entity_id']==entity
    assert plan_music_volume(value,'set volume in '+room+' to 30 percent')['data']['entity_id']==entity
    assert room in plan_music_status(value,'what is playing in '+room)['response']


def test_unsupported_and_unavailable_players_fail_before_dispatch():
    value=hass()
    state=value.states.get(ROOMS['kitchen'])
    state.attributes['supported_features']=0
    with pytest.raises(ValueError,match='support'):
        plan_music_transport(value,'pause music in kitchen')
    with pytest.raises(ValueError,match='support'):
        plan_music_volume(value,'set volume in kitchen to 30 percent')
    state.state='unavailable'
    with pytest.raises(ValueError,match='unavailable'):
        plan_music(value,'play Queen in kitchen')


def test_agent_volume_preview_and_execution_use_music_player():
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        case.hass.states.values.update(hass().states.values)
        area=case.hass.areas.entries['kitchen']
        complete(case.agent.async_handle(dialogue.UserInput('preview set volume to 30 percent'),area))
        assert case.hass.services.calls==[]
        complete(case.agent.async_handle(dialogue.UserInput('set volume to 30 percent'),area))
        assert case.hass.services.calls[-1][0]==('media_player','volume_set',{'entity_id':ROOMS['kitchen'],'volume_level':0.3})
        count=len(case.hass.services.calls)
        result=complete(case.agent.async_handle(dialogue.UserInput("what's playing"),area))
        assert 'Africa' in result.response.speech and len(case.hass.services.calls)==count
    finally:case.doCleanups()

