"""Bridge labels may change; registration identities and connection keys may not."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch
import test_bridge

ROOT=Path(__file__).resolve().parents[1]/'custom_components'/'jarvis_voice_bridge'

class Labels(unittest.IsolatedAsyncioTestCase):
    async def test_stt_display_and_legacy_identity(self):
        from bridge.stt import VoiceBridge
        entry=types.SimpleNamespace(entry_id='existing',data={'host':'example.local','port':10300})
        entity=VoiceBridge(entry)
        self.assertEqual(entity._attr_name,'Home Voice Assistant Speech')
        self.assertEqual(entity._attr_unique_id,'existing-stt')
        self.assertEqual((entity.host,entity.port),('example.local',10300))

    async def test_setup_import_and_existing_host_port_unique_identity(self):
        schema=types.ModuleType('voluptuous')
        config=types.ModuleType('homeassistant.config_entries')
        class Flow:
            def __init_subclass__(cls,**kwargs):cls.domain=kwargs['domain']
            async_set_unique_id=AsyncMock()
            def _abort_if_unique_id_configured(self):pass
            def async_create_entry(self,**kwargs):return kwargs
        config.ConfigFlow=Flow
        result=types.ModuleType('homeassistant.data_entry_flow');result.FlowResult=dict
        modules={'voluptuous':schema,'homeassistant.config_entries':config,'homeassistant.data_entry_flow':result}
        with patch.dict(sys.modules,modules),patch.object(sys.modules['homeassistant'],'config_entries',config,create=True),patch.object(sys.modules['bridge'],'DOMAIN','jarvis_voice_bridge',create=True):
            spec=importlib.util.spec_from_file_location('bridge.brand_flow_fixture',ROOT/'config_flow.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            flow=module.ConfigFlow()
            value=await flow.async_step_user({'host':'example.local','port':10300})
        self.assertEqual(value['title'],'Home Voice Assistant Bridge')
        self.assertEqual(value['data'],{'host':'example.local','port':10300})
        self.assertEqual(flow.domain,'jarvis_voice_bridge')
        flow.async_set_unique_id.assert_awaited_with('example.local:10300')

    async def test_diagnostic_display_keeps_its_existing_registry_identity(self):
        conversation=types.ModuleType('homeassistant.components.conversation')
        conversation.ConversationEntity=type('ConversationEntity',(),{})
        helpers=types.ModuleType('homeassistant.helpers');helpers.__path__=[]
        intent=types.ModuleType('homeassistant.helpers.intent');helpers.intent=intent
        modules={'homeassistant.components.conversation':conversation,
                 'homeassistant.helpers':helpers,'homeassistant.helpers.intent':intent}
        with patch.dict(sys.modules,modules),patch.object(sys.modules['homeassistant.components'],'conversation',conversation,create=True):
            spec=importlib.util.spec_from_file_location('bridge.brand_conversation_fixture',ROOT/'conversation.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            entity=module.BridgeTestAgent(types.SimpleNamespace(entry_id='existing'))
        self.assertEqual(entity._attr_name,'Home Voice Assistant Bridge Check')
        self.assertEqual(entity._attr_unique_id,'existing-test-conversation')
