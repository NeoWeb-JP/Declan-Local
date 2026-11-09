"""All acknowledgment paths preserve quiet/privacy policy and factual responses."""
import pytest
from music_fixtures import configure_music
import test_agent_dialogue as dialogue
import test_commands as fixtures
from test_context_personality_batch import home,complete
from jarvis_test.personality import contextual_reply


@pytest.mark.parametrize('kind',['clarification','failed','self_correction','music'])
def test_legacy_night_policy_is_not_bypassed_by_synchronous_responses(kind):
    hass=home();settings=hass.data['declan_local']['settings']
    settings.pop('quiet_hours');settings['personality_script']='script.jarvis_personality_engine'
    reason='The exact question or result remains here.'
    assert contextual_reply(hass,reason,kind).endswith(reason)


@pytest.mark.parametrize('kind',['clarification','failed','self_correction','music'])
def test_guest_and_quiet_responses_are_safe_and_keep_facts(kind):
    hass=home();hass.states.get('input_boolean.authority').state='on'
    reason='Requested Queen in Kitchen.'
    reply=contextual_reply(hass,reason,kind)
    assert reply.endswith(reason) and 'my bru' not in reply
    hass.states.get('input_boolean.quiet').state='on'
    assert contextual_reply(hass,reason,kind).endswith(reason)


def test_quiet_music_correction_keeps_request_fact_without_success_claim():
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        case.hass.data=home().data
        configure_music(case.hass)
        for key in ('visitors','authority','quiet'):
            case.hass.states.values['input_boolean.'+key]=fixtures.State('input_boolean.'+key,key,'on' if key=='quiet' else 'off')
        player='media_player.kitchen_declan_voice_assistant'
        case.hass.states.values[player]=fixtures.State(player,'Kitchen music','idle')
        complete(case.agent.async_handle(dialogue.UserInput('unrecognised babble')))
        result=complete(case.agent.async_handle(dialogue.UserInput('no I meant play Queen in the kitchen')))
        assert 'Requested' in result.response.speech and 'kitchen' in result.response.speech.lower()
        # Quiet hours no longer select a polite persona. Preserve the factual
        # request acknowledgement without claiming playback has started.
        assert 'Starting ' not in result.response.speech
        assert 'Now playing' not in result.response.speech
        assert case.hass.services.calls[-1][0][0]=='music_assistant'
    finally:case.doCleanups()
