"""All local response pools have enough unique choices without weakening policy."""
import json
from pathlib import Path
import test_agent_dialogue
from jarvis_test.personality import SAVAGE_LINES,CONTEXT_LINES,contextual_reply
from test_context_personality_batch import home


def test_each_catalogue_and_context_pool_has_five_unique_responses():
    path=Path(__file__).resolve().parents[1]/'custom_components/declan_local/responses.json'
    catalog=json.loads(path.read_text(encoding='utf-8'))
    for mode,pools in catalog.items():
        for context,lines in pools.items():assert len(set(lines))>=5,(mode,context)
    for context,lines in SAVAGE_LINES.items():assert len(set(lines))>=5,context
    for mode,pools in CONTEXT_LINES.items():
        for context,lines in pools.items():assert len(set(lines))>=5,(mode,context)


def test_new_choices_stay_guest_safe_and_quiet():
    hass=home();hass.states.get('input_boolean.visitors').state='on'
    for kind in CONTEXT_LINES['Guest']:
        assert 'my bru' not in contextual_reply(hass,'Exact facts remain.',kind)
    hass.states.get('input_boolean.quiet').state='on'
    for kind in CONTEXT_LINES['Home']:
        assert contextual_reply(hass,'Exact facts remain.',kind)=='Exact facts remain.'

