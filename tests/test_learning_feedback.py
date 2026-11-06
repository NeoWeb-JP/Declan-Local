"""Training feedback, editing/undo and private conversational recall."""
import sys
from types import SimpleNamespace, ModuleType
from test_learning_storage import storage, complete
from custom_components.declan_local import learning


def test_verified_success_failure_and_preview_feedback_survives_restart(storage):
    hass = SimpleNamespace(data={'declan_local': {'approved_aliases': {'lanp off':'turn off kitchen lamp'}}})
    complete(learning.load_evidence(hass))
    record = {'received_text':'lanp off','resolved_text':'turn off kitchen lamp',
              'outcome':'completed','time':'2026-11-03T13:00:00+00:00','steps':[{'kind':'light'}]}
    learning.observe(hass, record)
    learning.observe(hass, {**record,'preview':True})
    learning.observe(hass, {**record,'steps':[{'unverified':True}]})
    learning.observe(hass, {**record,'outcome':'failed'})
    usage = hass.data['declan_local']['learning_usage']['lanp off']
    assert usage['successes'] == usage['failures'] == 1
    assert usage['needs_review'] is True
    complete(learning.flush_evidence(hass))
    fresh = SimpleNamespace(data={})
    complete(learning.load_evidence(fresh))
    assert fresh.data['declan_local']['learning_usage']['lanp off'] == usage
    learning.observe(hass, record)
    assert usage['needs_review'] is False


def test_edit_and_undo_do_not_run_any_command(monkeypatch):
    module = ModuleType('homeassistant.helpers.storage')
    class Store:
        def __init__(self,*args): pass
        async def async_save(self,value): pass
    module.Store=Store
    monkeypatch.setitem(sys.modules,module.__name__,module)
    hass=SimpleNamespace(data={'declan_local':{'approved_aliases':{'lanp off':'turn off kitchen lights'}}})
    complete(learning.review(hass,'lanp off','edit','turn off fairy lights'))
    assert learning.resolve_alias(hass,'lanp off') == 'turn off fairy lights'
    complete(learning.review(hass,'lanp off','remove'))
    assert learning.resolve_alias(hass,'lanp off') == 'lanp off'


def test_what_did_you_hear_is_scoped_and_does_not_repeat_actions():
    import test_agent_dialogue as dialogue
    case=dialogue.Dialogue('test_other_conversation_cannot_answer');case.setUp()
    try:
        complete(case.agent.async_handle(dialogue.UserInput('turn off kitchen lamp','one')))
        count=len(case.hass.services.calls)
        result=complete(case.agent.async_handle(dialogue.UserInput('what did you hear?','one')))
        assert 'turn off kitchen lamp' in result.response.speech
        assert len(case.hass.services.calls) == count
        other=complete(case.agent.async_handle(dialogue.UserInput('what did you hear?','two')))
        assert 'do not have' in other.response.speech
        for item in case.agent._last_requests.values():item['at'] -= 121
        expired=complete(case.agent.async_handle(dialogue.UserInput('what did you hear?','one')))
        assert 'do not have' in expired.response.speech
    finally:case.doCleanups()

