"""Read-only correction previews, persisted review history and bounded repair turns."""
import copy
import sys
from types import ModuleType
import pytest
import test_agent_dialogue as dialogue
from test_learning_storage import complete,storage
from custom_components.jarvis_local import learning


def test_preview_plans_without_services_or_learning_mutation():
    value=dialogue.fixtures.Hass();value.data={'jarvis_local':{
        'approved_aliases':{'lanp off':'turn off kitchen lamp'}}}
    value.services=dialogue.Services()
    before=copy.deepcopy(value.data)
    result=learning.test_correction(value,'lanp off')
    assert result['preview'] is True and 'kitchen' in result['summary'].lower()
    assert value.services.calls==[] and value.data==before
    with pytest.raises(ValueError):learning.test_correction(value,'unobserved phrase','turn off kitchen lamp')


def test_review_history_survives_restart_with_before_and_after(storage,monkeypatch):
    value=dialogue.fixtures.Hass();value.data={'jarvis_local':{'approved_aliases':{'lanp off':'turn off kitchen lights'}}}
    complete(learning.load_evidence(value))
    # The alias-decision store is separate from the evidence/history store.
    evidence_store=value.data['jarvis_local']['learning_evidence_store']
    module=ModuleType('homeassistant.helpers.storage')
    class Store:
        def __init__(self,*args):pass
        async def async_save(self,item):pass
    module.Store=Store
    with monkeypatch.context() as patch:
        patch.setitem(sys.modules,module.__name__,module)
        complete(learning.review(value,'lanp off','edit','turn off fairy lights'))
    complete(learning.flush_evidence(value))
    fresh=dialogue.fixtures.Hass();fresh.data={}
    complete(learning.load_evidence(fresh))
    event=fresh.data['jarvis_local']['learning_history'][-1]
    assert event['decision']=='edit' and event['before']=='turn off kitchen lights'
    assert event['after']=='turn off fairy lights' and event['time']
    assert len(learning._validated_history([event]*120))==100


def test_unknown_voice_request_requests_one_repair_turn_without_looping():
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        def request(text):
            user=dialogue.UserInput(text);user.satellite_id='assist_satellite.kitchen'
            return complete(case.agent.async_handle(user))
        assert request('unrecognised babble one').continue_conversation is True
        assert request('unrecognised babble two').continue_conversation is False
        assert request('unrecognised babble three').continue_conversation is False
        assert case.hass.services.calls==[]
    finally:case.doCleanups()


def test_chat_unknown_and_voice_preview_do_not_reopen_microphone():
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        result=complete(case.agent.async_handle(dialogue.UserInput('unrecognised babble')))
        assert result.continue_conversation is False
        user=dialogue.UserInput('preview unrecognised babble');user.satellite_id='assist_satellite.kitchen'
        assert complete(case.agent.async_handle(user)).continue_conversation is False
    finally:case.doCleanups()

