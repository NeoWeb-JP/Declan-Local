"""Shuffle uses the same room player and never executes a preview."""
import pytest
import test_agent_dialogue as dialogue
from types import SimpleNamespace
from test_music_improvements import TEST_DESTINATIONS, complete, hass
from jarvis_test.music_assistant_voice import plan_music_transport


@pytest.mark.parametrize('phrase,enabled',[
    ('shuffle on',True),('shuffle off',False),('turn shuffle on',True),
    ('switch shuffle off',False),('enable shuffle',True),('disable shuffle',False),
    ('shuffle music',True),('shuffle',True)])
def test_explicit_shuffle_commands_use_source_room(phrase,enabled):
    step=plan_music_transport(hass(),phrase,SimpleNamespace(name='Kitchen'))
    assert step['name']=='shuffle_set'
    assert step['data']=={'entity_id':TEST_DESTINATIONS['kitchen'],'shuffle':enabled}


def test_shuffle_named_group_and_missing_room():
    assert plan_music_transport(hass(),'shuffle on in everywhere')['data']['entity_id']==TEST_DESTINATIONS['everywhere']
    assert plan_music_transport(hass(),'shuffle OFF in the BEDROOM')['data']['shuffle'] is False
    with pytest.raises(ValueError):plan_music_transport(hass(),'shuffle on')
    with pytest.raises(ValueError):plan_music_transport(hass(),'shuffle on in garage',SimpleNamespace(name='Kitchen'))


def test_unsupported_player_is_refused():
    value=hass();value.states.get(TEST_DESTINATIONS['kitchen']).attributes['supported_features']=0
    with pytest.raises(ValueError,match='support'):
        plan_music_transport(value,'shuffle on in kitchen')


def test_real_agent_shuffle_preview_and_dispatch():
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        configured = hass()
        case.hass.states.values.update(configured.states.values)
        case.hass.data.setdefault('declan_local', {})['settings'] = configured.data['declan_local']['settings']
        area=case.hass.areas.entries['kitchen']
        complete(case.agent.async_handle(dialogue.UserInput('preview shuffle on'),area))
        assert case.hass.services.calls==[]
        complete(case.agent.async_handle(dialogue.UserInput('shuffle on'),area))
        assert case.hass.services.calls[-1][0]==('media_player','shuffle_set',{'entity_id':TEST_DESTINATIONS['kitchen'],'shuffle':True})
        complete(case.agent.async_handle(dialogue.UserInput('shuffle off'),area))
        assert case.hass.services.calls[-1][0][-1]['shuffle'] is False
    finally:case.doCleanups()

