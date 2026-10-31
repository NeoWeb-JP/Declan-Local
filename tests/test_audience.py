"""Privacy isolation and local persona behavior without a running HA instance."""
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1] / 'custom_components' / 'jarvis_local'
spec = importlib.util.spec_from_file_location('audience_policy_fixture', ROOT / 'audience.py')
audience = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audience)


def house(visitors='off', authority='off', quiet=None):
    settings = {'visitors_present': 'input_boolean.visitors', 'guest_mode': 'input_boolean.authority'}
    values = {'input_boolean.visitors': visitors, 'input_boolean.authority': authority}
    if quiet is not None:
        settings['quiet_hours'] = 'input_boolean.quiet'
        values['input_boolean.quiet'] = quiet
    return types.SimpleNamespace(
        data={'jarvis_local': {'settings': settings}},
        states=types.SimpleNamespace(get=lambda entity: types.SimpleNamespace(state=values[entity]) if entity in values and values[entity] is not None else None),
        services=types.SimpleNamespace(async_call=AsyncMock()),
    )


class AudienceTests(unittest.TestCase):
    def test_home_requires_both_explicit_off_signals(self):
        for visitor in ('on', 'off', 'unknown', 'unavailable', None):
            for authority in ('on', 'off', 'unknown', 'unavailable', None):
                with self.subTest(visitor=visitor, authority=authority):
                    hass = house(visitor, authority)
                    self.assertEqual(audience.mode(hass), 'Home' if visitor == authority == 'off' else 'Guest')
                    hass.services.async_call.assert_not_called()

    def test_no_configuration_is_private_by_default(self):
        hass = house()
        hass.data = {}
        self.assertEqual(audience.mode(hass), 'Guest')

    def test_quiet_helper_is_independent_and_fails_quiet(self):
        for state in ('on', 'unknown', 'unavailable'):
            hass = house(quiet=state)
            self.assertTrue(audience.quiet(hass))
            self.assertEqual(audience.mode(hass), 'Home')
        self.assertFalse(audience.quiet(house(quiet='off')))
        self.assertFalse(audience.quiet(house()))


class PersonaTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        package = types.ModuleType('persona_fixture')
        package.__path__ = [str(ROOT)]
        settings = types.ModuleType('persona_fixture.settings')
        settings.get = lambda hass, key: hass.data['jarvis_local']['settings'].get(key)
        errors = types.ModuleType('homeassistant.exceptions')
        errors.HomeAssistantError = type('HomeAssistantError', (Exception,), {})
        self.patcher = patch.dict(sys.modules, {'persona_fixture': package, 'persona_fixture.settings': settings,
                                                'homeassistant.exceptions': errors})
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.module = importlib.import_module('persona_fixture.personality')
        self.module.CATALOG = json.loads((ROOT / 'responses.json').read_text(encoding='utf-8'))
        self.hass = house()
        async def executor(fn): return fn()
        self.hass.async_add_executor_job = executor

    async def test_only_home_and_guest_local_catalogue_without_script_calls(self):
        self.assertEqual(set(self.module.CATALOG), {'Home', 'Guest'})
        for visitors, expected in (('off', 'Home'), ('on', 'Guest'), ('unavailable', 'Guest')):
            self.hass = house(visitors)
            line = await self.module.confirmation(self.hass, None, 'Lights on.', 'on')
            self.assertIn(line, self.module.CATALOG[expected]['on'])
            self.hass.services.async_call.assert_not_called()

    async def test_live_visitor_change_cannot_reuse_home_history(self):
        home = await self.module.confirmation(self.hass, None, 'Done.', 'off')
        self.assertIn(home, self.module.CATALOG['Home']['off'])
        self.hass.states = house('on').states
        guest = await self.module.confirmation(self.hass, None, 'Done.', 'off')
        self.assertIn(guest, self.module.CATALOG['Guest']['off'])

    async def test_quiet_and_legacy_night_keep_plain_confirmation(self):
        self.hass = house(quiet='on')
        self.assertEqual(await self.module.confirmation(self.hass, None, 'Lights off.', 'off'), 'Lights off.')
        self.hass = house()
        self.hass.data['jarvis_local']['settings']['personality_script'] = 'script.legacy'
        self.hass.states = types.SimpleNamespace(get=lambda entity: types.SimpleNamespace(state='on'))
        self.hass.services.async_call.return_value = {'personality': 'Night', 'response': 'PRIVATE'}
        self.assertEqual(await self.module.confirmation(self.hass, None, 'Lights off.', 'off'), 'Lights off.')

    async def test_legacy_home_choice_cannot_override_visitors(self):
        self.hass = house('on')
        original = self.hass.states.get
        self.hass.data['jarvis_local']['settings']['personality_script'] = 'script.legacy'
        self.hass.states.get = lambda entity: types.SimpleNamespace(state='on') if entity == 'script.legacy' else original(entity)
        self.hass.services.async_call.return_value = {'personality': 'Savage', 'response': 'PRIVATE'}
        line = await self.module.confirmation(self.hass, None, 'Done.', 'on')
        self.assertIn(line, self.module.CATALOG['Guest']['on'])

    async def test_unknown_context_and_quiet_failure_do_not_joke(self):
        self.assertEqual(await self.module.confirmation(self.hass, None, 'Alarm failed.', 'security_error'), 'Alarm failed.')
        self.hass = house(quiet='unavailable')
        self.assertEqual(await self.module.confirmation(self.hass, None, 'Done.', 'on'), 'Done.')

    async def test_action_specific_anti_repeat(self):
        lines = [await self.module.confirmation(self.hass, None, 'Done.', 'on') for _ in range(4)]
        self.assertEqual(len(set(lines)), 4)

    async def test_visitors_arriving_during_phonetic_script_get_plain_reply(self):
        self.hass.data['jarvis_local']['settings']['phonetic_script'] = 'script.phonetic'
        original = self.hass.states.get
        self.hass.states.get = lambda entity: types.SimpleNamespace(state='on') if entity == 'script.phonetic' else original(entity)
        async def convert(*args, **kwargs):
            self.hass.states = house('on').states
            return {'text': 'PRIVATE_HOME_TRANSLITERATION'}
        self.hass.services.async_call.side_effect = convert
        self.assertEqual(await self.module.confirmation(self.hass, None, 'Lights on.', 'on'), 'Lights on.')
