"""Authority lifecycle regressions with independent HA state/service fixtures."""
import copy
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]/'custom_components'/'jarvis_local'
core=types.ModuleType('homeassistant.core')
core.callback=lambda fn:fn
errors=types.ModuleType('homeassistant.exceptions')
errors.HomeAssistantError=type('HomeAssistantError',(Exception,),{})
spec=importlib.util.spec_from_file_location('guest_authority_fixture',ROOT/'guest_authority.py')
module=importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {'homeassistant.core':core,'homeassistant.exceptions':errors}):
    spec.loader.exec_module(module)


class Store:
    def __init__(self):self.saved=None;self.fail=False
    async def async_load(self):return copy.deepcopy(self.saved)
    async def async_save(self,value):
        if self.fail:raise OSError('storage unavailable')
        self.saved=copy.deepcopy(value)


class AuthorityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.now=0
        self.store=Store()
        config={key:('person.' if key.startswith('guest_owner') else 'input_text.' if key in {'guest_names','guest_staying_names'} else 'input_boolean.')+key
                for key in (*module.AUTO_KEYS,'guest_names','guest_staying_names')}
        initial=dict(guest_mode='off',visitors_present='on',guests_staying='on',
                     guest_auto_enable='on',guest_owner_one='not_home',guest_owner_two='not_home',
                     guest_away_suspend='off',guest_names='',guest_staying_names='Mike and Kathy')
        self.config=config
        self.values={config[k]:types.SimpleNamespace(state=v,attributes={'max':255}) for k,v in initial.items()}
        self.calls=[]
        self.fail_entity=None
        self.hook=None
        self.hass=types.SimpleNamespace(data={'jarvis_local':{'settings':config}},
            states=types.SimpleNamespace(get=lambda entity:self.values.get(entity)),
            async_create_task=lambda coro:coro.close())
        self.controller=module.GuestAuthority(self.hass,self.store,types.SimpleNamespace(id='own'),clock=lambda:self.now)
        async def service(domain,action,data,**kwargs):
            self.calls.append((domain,action,dict(data)))
            if data['entity_id']==self.fail_entity:raise module.HomeAssistantError('unavailable')
            if self.hook:
                hook,self.hook=self.hook,None
                hook()
            value=data['value'] if domain=='input_text' else 'on' if action=='turn_on' else 'off'
            self.change_id(data['entity_id'],value,kwargs.get('context'))
        self.hass.services=types.SimpleNamespace(async_call=service)

    def change_id(self,entity,value,context=None):
        old=self.values.get(entity)
        self.values[entity]=types.SimpleNamespace(state=value,attributes={'max':255})
        self.controller.changed(types.SimpleNamespace(data={'entity_id':entity,'old_state':old,'new_state':self.values[entity]},
                                                     context=context or types.SimpleNamespace(id='external')))
    def change(self,key,value):self.change_id(self.config[key],value)
    async def grant(self):
        await self.controller.tick()
        self.now+=120
        await self.controller.tick()
    def value(self,key):return self.values[self.config[key]].state

    async def test_requires_full_continuous_delay_then_suspends_before_grant(self):
        await self.controller.tick()
        self.now=119.99
        await self.controller.tick()
        self.assertEqual(self.calls,[])
        self.now=120
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')
        self.assertEqual(self.value('guest_away_suspend'),'on')
        self.assertEqual(self.value('guest_names'),'Mike and Kathy')
        self.assertEqual([c[2]['entity_id'] for c in self.calls],
                         [self.config['guest_away_suspend'],self.config['guest_names'],self.config['guest_mode']])
        self.assertEqual(self.store.saved['authority'],'automatic')

    async def test_unknown_unavailable_and_zone_states_never_qualify(self):
        for invalid in ('unknown','unavailable','home','work'):
            with self.subTest(state=invalid):
                self.change('guest_owner_two',invalid)
                await self.controller.tick()
                self.now+=200
                await self.controller.tick()
                self.assertEqual(self.value('guest_mode'),'off')
        self.assertEqual(self.calls,[])

    async def test_unknown_after_grant_revokes_automatic_authority(self):
        await self.grant()
        self.change('guest_owner_two','unavailable')
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')

    async def test_external_manual_on_is_not_revoked_by_owner_return(self):
        self.change('guest_mode','on')
        await self.controller.tick()
        self.change('guest_owner_one','home')
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')
        self.assertEqual(self.store.saved['authority'],'manual')

    async def test_manual_restart_keeps_authority(self):
        await self.controller.command({'operation':'set','names':'Kathy'})
        self.controller=module.GuestAuthority(self.hass,self.store,types.SimpleNamespace(id='own'),clock=lambda:self.now)
        self.controller.record=await self.store.async_load()
        self.change('guest_owner_one','home')
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')

    async def test_cancellation_during_grant_remains_recoverable(self):
        import asyncio
        await self.controller.tick()
        self.now=120
        async def interrupted(*args, **kwargs):raise asyncio.CancelledError()
        self.hass.services.async_call=interrupted
        with self.assertRaises(asyncio.CancelledError):
            await self.controller.tick()
        self.assertEqual(self.store.saved['authority'],'automatic')
        self.assertFalse(self.store.saved['active'])
        self.assertEqual(self.value('guest_mode'),'off')

    async def test_transient_unknown_resets_delay_even_before_poll(self):
        await self.controller.tick()
        self.now=119
        self.change('guest_owner_one','unknown')
        self.change('guest_owner_one','not_home')
        await self.controller.tick()
        self.now=120
        await self.controller.tick()
        self.assertEqual(self.calls,[])
        self.now=239
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')

    async def test_owner_return_removes_only_automatic_authority_and_keeps_visitors(self):
        await self.grant()
        self.change('guest_owner_one','home')
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')
        self.assertEqual(self.value('guest_away_suspend'),'off')
        self.assertEqual(self.value('visitors_present'),'on')
        self.assertTrue(all(c[0] in {'input_boolean','input_text'} for c in self.calls))

    async def test_manual_handover_survives_owner_return_and_guests_left(self):
        await self.controller.command({'operation':'set','names':'Manual Guest'})
        await self.controller.command({'operation':'staying','names':'Other Visitors'})
        self.assertEqual(self.value('guest_names'),'Manual Guest')
        self.change('guest_owner_one','home')
        await self.controller.tick()
        reply=await self.controller.command({'operation':'clear'})
        self.assertEqual(self.value('guest_mode'),'on')
        self.assertEqual(self.value('guest_names'),'Manual Guest')
        self.assertIn('manual',reply)
        self.assertEqual(self.value('guests_staying'),'off')
        self.assertEqual(self.value('visitors_present'),'off')

    async def test_manual_adoption_of_automatic_handover_is_persisted(self):
        await self.grant()
        await self.controller.command({'operation':'set','names':'Kathy'})
        self.change('guest_owner_two','home')
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')
        self.assertEqual(self.store.saved['authority'],'manual')

    async def test_cancel_blocks_automatic_regrant_until_new_declaration(self):
        await self.grant()
        await self.controller.command({'operation':'cancel'})
        await self.controller.tick()
        self.now+=200
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')
        await self.controller.command({'operation':'staying','names':'Kathy'})
        await self.controller.tick()
        self.now+=120
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')

    async def test_opt_in_and_complete_configuration_required(self):
        self.change('guest_auto_enable','off')
        await self.grant()
        self.assertEqual(self.calls,[])
        self.change('guest_auto_enable','on')
        self.config.pop('guest_owner_two')
        await self.grant()
        self.assertEqual(self.calls,[])

    async def test_storage_failure_cannot_grant(self):
        await self.controller.tick()
        self.store.fail=True
        self.now=120
        await self.controller.tick()
        self.assertEqual(self.calls,[])
        self.assertEqual(self.value('guest_mode'),'off')

    async def test_owner_returns_during_awaited_suspension_never_grants(self):
        await self.controller.tick()
        self.hook=lambda:self.change('guest_owner_one','home')
        self.now=120
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')
        self.assertEqual(self.value('guest_away_suspend'),'off')
        self.assertFalse(any(c[:2]==('input_boolean','turn_on') and c[2]['entity_id']==self.config['guest_mode'] for c in self.calls))

    async def test_partial_provider_failure_rolls_back_on_next_reconcile(self):
        await self.controller.tick()
        self.fail_entity=self.config['guest_mode']
        self.now=120
        await self.controller.tick()
        self.assertEqual(self.value('guest_away_suspend'),'on')
        self.fail_entity=None
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')
        self.assertEqual(self.value('guest_away_suspend'),'off')

    async def test_preexisting_suspension_is_not_cleared(self):
        self.change('guest_away_suspend','on')
        await self.grant()
        self.change('guest_owner_one','home')
        await self.controller.tick()
        self.assertEqual(self.value('guest_away_suspend'),'on')

    async def test_manual_on_during_grant_before_event_dispatch_is_preserved(self):
        await self.controller.tick()
        self.hook=lambda:setattr(self.values[self.config['guest_mode']],'state','on')
        self.now=120
        await self.controller.tick()
        self.assertEqual(self.store.saved['authority'],'manual')
        self.change('guest_owner_one','home')
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')

    async def test_unload_releases_automatic_but_not_manual(self):
        await self.grant()
        await self.controller.stop()
        self.assertEqual(self.value('guest_mode'),'off')
        self.assertEqual(self.value('guest_away_suspend'),'off')
        self.controller.stopped=False
        await self.controller.command({'operation':'set','names':'Kathy'})
        await self.controller.stop()
        self.assertEqual(self.value('guest_mode'),'on')

    async def test_status_does_not_restart_observation(self):
        await self.controller.tick()
        self.now=119
        await self.controller.command({'operation':'status'})
        self.now=120
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'on')

    async def test_external_off_is_manual_cancel_and_does_not_regrant(self):
        await self.grant()
        self.change('guest_mode','off')
        await self.controller.tick()
        self.now+=400
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')
        self.assertEqual(self.value('guest_away_suspend'),'off')

    async def test_reconfiguration_revokes_old_auto_not_new_manual_helper(self):
        await self.grant()
        new=dict(self.config,guest_mode='input_boolean.other')
        self.values[new['guest_mode']]=types.SimpleNamespace(state='on')
        await self.controller.prepare_settings(new)
        self.assertEqual(self.value('guest_mode'),'off')
        self.assertEqual(self.values[new['guest_mode']].state,'on')

    async def test_restart_revokes_recorded_auto_then_restarts_delay_and_unsubscribes(self):
        await self.grant()
        handles=[]
        event=types.ModuleType('homeassistant.helpers.event')
        def track(hass, fn, interval):
            handles.append(fn)
            return lambda:handles.append('timer stopped')
        event.async_track_time_interval=track
        self.hass.bus=types.SimpleNamespace(async_listen=lambda *args:lambda:handles.append('listener stopped'))
        self.controller=module.GuestAuthority(self.hass,self.store,types.SimpleNamespace(id='own'),clock=lambda:self.now)
        with patch.dict(sys.modules,{'homeassistant.helpers.event':event}):
            await self.controller.start()
        self.assertEqual(self.value('guest_mode'),'off')
        self.now+=119
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')
        await self.controller.stop()
        self.assertIn('listener stopped',handles)
        self.assertIn('timer stopped',handles)
        self.now+=100
        await self.controller.tick()
        self.assertEqual(self.value('guest_mode'),'off')
