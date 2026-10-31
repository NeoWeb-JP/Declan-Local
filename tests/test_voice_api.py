"""Import and register the full API module with only declared HA dependencies."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

ROOT=Path(__file__).resolve().parents[1]/'custom_components'/'jarvis_local'

class VoiceApi(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        modules={}
        package=types.ModuleType('voice_api_fixture');package.__path__=[str(ROOT)]
        modules[package.__name__]=package
        for name in ('homeassistant','homeassistant.components','homeassistant.helpers'):
            item=types.ModuleType(name);item.__path__=[];modules[name]=item
        vol=types.ModuleType('voluptuous')
        vol.Required=lambda key,**kwargs:key
        vol.Optional=lambda key,**kwargs:key
        vol.In=lambda values:lambda value:value
        modules['voluptuous']=vol
        api=types.ModuleType('homeassistant.components.websocket_api')
        def admin(fn):fn.requires_admin=True;return fn
        def command(schema):
            def decorate(fn):fn.command_type=schema['type'];return fn
            return decorate
        api.require_admin=admin;api.websocket_command=command;api.async_response=lambda fn:fn
        self.registered=[]
        api.async_register_command=lambda hass,fn:self.registered.append(fn)
        modules[api.__name__]=api;modules['homeassistant.components'].websocket_api=api
        conv=types.ModuleType('homeassistant.components.conversation')
        modules[conv.__name__]=conv;modules['homeassistant.components'].conversation=conv
        core=types.ModuleType('homeassistant.core');core.callback=lambda fn:fn
        modules[core.__name__]=core
        storage=types.ModuleType('homeassistant.helpers.storage');storage.Store=object
        modules[storage.__name__]=storage
        areas=types.ModuleType('homeassistant.helpers.area_registry')
        modules[areas.__name__]=areas
        errors=types.ModuleType('homeassistant.exceptions');errors.HomeAssistantError=type('HomeAssistantError',(Exception,),{})
        modules[errors.__name__]=errors
        for name,methods in {
            'voice_profiles':['public_profiles','validate_profiles','save_profiles_file'],
            'settings':['save'],'satellite_health':['check_mappings'],
            'media_search_config':['public_config','save'],'media_search':['parse_search'],
            'media_search_adapters':['search'],
        }.items():
            item=types.ModuleType('voice_api_fixture.'+name)
            for method in methods:setattr(item,method,AsyncMock())
            modules[item.__name__]=item
        self.patcher=patch.dict(sys.modules,modules);self.patcher.start();self.addCleanup(self.patcher.stop)
        spec=importlib.util.spec_from_file_location('voice_api_fixture.websocket',ROOT/'websocket.py')
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.manager=types.SimpleNamespace(catalogue=types.SimpleNamespace(
            plan=AsyncMock(return_value={'missing_count':1}),prepare=AsyncMock(return_value={'saved':True})))
        self.hass=types.SimpleNamespace(data={'jarvis_local':{'voice_manager':self.manager}})
        self.results=[];self.errors=[]
        self.connection=types.SimpleNamespace(send_result=lambda *args:self.results.append(args),
                                              send_error=lambda *args:self.errors.append(args))

    async def test_full_registration_keeps_catalogue_and_all_other_apis_admin_only(self):
        self.module.register(self.hass)
        self.assertGreater(len(self.registered),10)
        self.assertTrue(all(fn.requires_admin for fn in self.registered))
        self.assertIn('jarvis_local/review_voice_catalogue',{fn.command_type for fn in self.registered})
        self.assertIn('jarvis_local/prepare_voice_catalogue',{fn.command_type for fn in self.registered})

    async def test_review_never_synthesizes_and_preparation_requires_explicit_approval(self):
        await self.module.review_voice_catalogue(self.hass,self.connection,{'id':1,'modes':['Guest']})
        self.manager.catalogue.prepare.assert_not_awaited()
        request={'id':2,'token':'review','line_id':'line','approved':False}
        await self.module.prepare_voice_catalogue(self.hass,self.connection,request)
        self.manager.catalogue.prepare.assert_not_awaited()
        request['approved']=True
        await self.module.prepare_voice_catalogue(self.hass,self.connection,request)
        self.manager.catalogue.prepare.assert_awaited_once_with('review','line')

    async def test_busy_and_failure_do_not_expose_provider_details(self):
        lock=asyncio.Lock();await lock.acquire()
        self.hass.data['jarvis_local']['phrase_generation_lock']=lock
        request={'id':2,'token':'review','line_id':'line','approved':True}
        await self.module.prepare_voice_catalogue(self.hass,self.connection,request)
        self.manager.catalogue.prepare.assert_not_awaited()
        lock.release()
        self.manager.catalogue.prepare.side_effect=self.module.HomeAssistantError('PRIVATE_PROVIDER_SECRET')
        await self.module.prepare_voice_catalogue(self.hass,self.connection,request)
        self.assertNotIn('PRIVATE_PROVIDER_SECRET',str(self.errors))
