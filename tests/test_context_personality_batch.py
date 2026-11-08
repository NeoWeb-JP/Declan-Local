"""Multi-turn brightness recipes and privacy-aware contextual replies."""
import pytest
import test_commands as fixtures
import test_agent_dialogue as dialogue
from jarvis_test.conversation_memory import context_followup, verified_lighting_context
from jarvis_test.personality import contextual_reply


def complete(coroutine):
    try:coroutine.send(None)
    except StopIteration as result:return result.value
    finally:coroutine.close()
    raise AssertionError('Unexpected suspension in mocked service call')


def test_brightness_recipe_requires_verified_uniform_results():
    step={'kind':'brightness','calls':[{'service':'turn_on','data':{'entity_id':['light.one'],'brightness_pct':30}}],
          'succeeded':['light.one'],'failed':[],'unverified':[]}
    memory=verified_lighting_context([step],1)
    assert context_followup('do the same in the kitchen',memory)=='set kitchen lights to 30 percent'
    assert verified_lighting_context([{**step,'unverified':['light.one']}],1) is None
    assert verified_lighting_context([{**step,'failed':['light.one']}],1) is None
    other={**step,'succeeded':['light.two'],'calls':[{'service':'turn_on','data':{'entity_id':['light.two'],'brightness_pct':60}}]}
    assert verified_lighting_context([step,other],1) is None
    assert context_followup('do the same in all rooms',memory) is None


def test_full_three_turn_sequence_and_preview():
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        def command(text,device='one'):
            return complete(case.agent.async_handle(dialogue.UserInput(text,device=device)))
        command('turn on bedroom lamp')
        command('make them 30 percent')
        count=len(case.hass.services.calls)
        command('preview do the same in the kitchen')
        assert len(case.hass.services.calls)==count
        command('do the same in the kitchen')
        assert case.hass.services.calls[-1][0] == ('light','turn_on',{'entity_id':['light.kitchen'],'brightness_pct':30})
        count=len(case.hass.services.calls)
        command('do the same in the office',device='other')
        assert len(case.hass.services.calls)==count
        for memory in case.agent._recent_lights.values():memory['at']-=121
        command('do the same in the office')
        assert len(case.hass.services.calls)==count
    finally:case.doCleanups()


def home():
    hass=fixtures.Hass();hass.data={'declan_local':{'settings':{
        'visitors_present':'input_boolean.visitors','guest_mode':'input_boolean.authority',
        'quiet_hours':'input_boolean.quiet'}}}
    for key in ('visitors','authority','quiet'):
        hass.states.values['input_boolean.'+key]=fixtures.State('input_boolean.'+key,key,'off')
    return hass


def test_contextual_personality_preserves_question_and_avoids_repetition():
    hass=home();question='Which light: Kitchen Lamp or Bedroom Lamp?'
    first=contextual_reply(hass,question,'clarification')
    second=contextual_reply(hass,question,'clarification')
    assert first.endswith(question) and second.endswith(question) and first!=second
    hass.states.get('input_boolean.authority').state='on'
    guest=contextual_reply(hass,question,'clarification')
    assert 'my bru' not in guest and guest.endswith(question)
    hass.states.get('input_boolean.quiet').state='on'
    assert contextual_reply(hass,question,'clarification').endswith(question)


@pytest.mark.parametrize('reason',['The device is unavailable.','Security alarm failed.','An emergency was reported.'])
def test_serious_errors_remain_direct(reason):
    assert contextual_reply(home(),reason,'failed')==reason


def test_real_agent_uses_clarification_context_without_losing_choices():
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        case.hass.data=home().data
        for key in ('visitors','authority','quiet'):
            case.hass.states.values['input_boolean.'+key]=fixtures.State('input_boolean.'+key,key,'off')
        reply=complete(case.agent.async_handle(dialogue.UserInput('lamp on')))
        assert reply.continue_conversation
        assert 'Kitchen Lamp' in reply.response.speech and 'Bedroom Lamp' in reply.response.speech
        assert case.hass.services.calls==[]
    finally:case.doCleanups()

