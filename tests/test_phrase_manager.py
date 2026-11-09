"""Exercise the real TTS wrapper with controlled Home Assistant providers."""
import asyncio
import importlib
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from test_phrase_library import audio, VoiceCache
import base64

ROOT=Path(__file__).resolve().parents[1]/'custom_components'/'declan_local'

class ManagerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        package=types.ModuleType('phrase_manager_fixture');package.__path__=[str(ROOT)]
        fake_tts=types.ModuleType('homeassistant.components.tts');fake_tts.TextToSpeechEntity=type('TextToSpeechEntity',(),{})
        fake_ffmpeg=types.ModuleType('homeassistant.components.ffmpeg')
        fake_ffmpeg.get_ffmpeg_manager=lambda hass:types.SimpleNamespace(binary='ffmpeg')
        exceptions=types.ModuleType('homeassistant.exceptions')
        exceptions.HomeAssistantError=type('HomeAssistantError',(Exception,),{})
        self.modules={'phrase_manager_fixture':package,'homeassistant.components.tts':fake_tts,
                      'homeassistant.components.ffmpeg':fake_ffmpeg,'homeassistant.exceptions':exceptions}
        for name in ['homeassistant','homeassistant.components']:
            stub=types.ModuleType(name);stub.__path__=[];self.modules[name]=stub
        self.modules['homeassistant.components'].tts=fake_tts
        # Keep all stubs scoped to this test; other repository fixtures coexist.
        self.patcher=patch.dict(sys.modules,self.modules);self.patcher.start();self.addCleanup(self.patcher.stop)
        self.module=importlib.import_module('phrase_manager_fixture.tts')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.cache=VoiceCache(self.temp.name,min_free_bytes=0)
        self.entry=types.SimpleNamespace(entry_id='test',options={'primary_tts':'tts.elevenlabs','fallback_tts':'tts.xtts','elevenlabs_voice':'declan','cache_revision':'v1','category_fallback':False})
        self.usage=self.module.VoiceUsage()
        self.manager=self.module.JarvisVoiceManager(self.entry,self.cache,self.usage)
        self.manager.entity_id='tts.jarvis_voice_manager'
        self.manager.hass=types.SimpleNamespace()
        self.calls=[]
        async def generate(hass,**kwargs):
            self.calls.append((kwargs['provider_entity_id'],kwargs['text']))
            return 'wav',audio()
        self.generate=generate
        self.provider_patch=patch.object(self.module,'generate_from_existing_tts',generate)
        self.provider_patch.start();self.addCleanup(self.provider_patch.stop)

    async def test_real_music_reply_uses_segments_then_only_new_genre(self):
        first=await self.manager.async_get_tts_audio('I requested country in kitchen.','en',{})
        self.assertEqual(first[0],'wav');self.assertEqual(len(self.calls),4)
        self.calls.clear()
        await self.manager.async_get_tts_audio('I requested jazz in kitchen.','en',{})
        self.assertEqual(self.calls,[('tts.elevenlabs','jazz')])
        self.assertEqual(self.usage.snapshot()['last_source'],'elevenlabs_phrase_generated')
        self.assertEqual(self.usage.snapshot()['generated_clips'],5)
        self.calls.clear()
        await self.manager.async_get_tts_audio('I requested jazz in kitchen.','en',{})
        self.assertEqual(self.calls,[])
        self.assertEqual(self.usage.snapshot()['last_source'],'elevenlabs_phrase_cached')

    async def test_explicit_whole_sentence_is_preferred_and_preview_does_not_run_music(self):
        text='I requested country in kitchen.'
        await self.manager.prepare_phrase(text,'sentence')
        self.assertEqual(self.calls,[('tts.elevenlabs',text)])
        self.calls.clear()
        await self.manager.async_get_tts_audio(text,'en',{})
        self.assertEqual(self.calls,[])
        self.assertEqual(self.usage.snapshot()['last_source'],'elevenlabs_cached')

    async def test_primary_phrase_failure_does_not_try_secondary_provider(self):
        text='I requested country in kitchen.'
        async def fail(hass,**kwargs):
            self.calls.append((kwargs['provider_entity_id'],kwargs['text']))
            if kwargs['provider_entity_id']=='tts.elevenlabs':raise self.module.HomeAssistantError('offline')
            return 'wav',audio(2000)
        with patch.object(self.module,'generate_from_existing_tts',fail):
            with self.assertRaises(self.module.HomeAssistantError):
                await self.manager.async_get_tts_audio(text,'en',{})
        self.assertEqual(self.calls,[('tts.elevenlabs','i requested')])

    async def test_conversion_failure_uses_original_full_sentence(self):
        async def broken(*args):raise ValueError('bad audio')
        self.manager._phrases.normalise=broken
        text='I requested country in kitchen.'
        await self.manager.async_get_tts_audio(text,'en',{})
        self.assertEqual(self.calls[-1],('tts.elevenlabs',text))

    async def test_disabled_library_and_unknown_text_use_whole_sentences(self):
        self.entry.options['phrase_library_enabled']=False
        text='I requested country in kitchen.'
        await self.manager.async_get_tts_audio(text,'en',{})
        self.assertEqual(self.calls,[('tts.elevenlabs',text)])
        self.calls.clear();self.entry.options['phrase_library_enabled']=True
        await self.manager.async_get_tts_audio('Kitchen light did not respond.','en',{})
        self.assertEqual(self.calls,[('tts.elevenlabs','Kitchen light did not respond.')])

    async def test_admin_generation_checks_storage_and_validation_first(self):
        for text,kind in [('', 'clip'),('x'*201,'clip'),('hello','unknown')]:
            with self.assertRaises(ValueError):await self.manager.prepare_phrase(text,kind)
        self.cache.min_free_bytes=10**30
        with self.assertRaises(ValueError):await self.manager.prepare_phrase('country','clip')
        self.assertEqual(self.calls,[])

    async def test_import_matches_active_identity_without_calling_provider(self):
        item={'text':'kitchen.','extension':'wav','audio':base64.b64encode(audio()).decode('ascii')}
        token=self.manager.import_token()
        result=await self.manager.import_clips([item],token)
        self.assertEqual(result['imported'],['kitchen.']);self.assertEqual(self.calls,[])
        await self.manager.async_get_tts_audio('I requested country in kitchen.','en',{})
        self.assertNotIn(('tts.elevenlabs','kitchen.'),self.calls)

    async def test_import_rejects_voice_changes_and_disabled_cache(self):
        token=self.manager.import_token()
        self.entry.options['elevenlabs_voice']='another'
        with self.assertRaises(ValueError):await self.manager.import_clips([],token)
        self.entry.options['cache_enabled']=False
        with self.assertRaises(ValueError):await self.manager.import_clips([],self.manager.import_token())
        self.assertEqual(self.calls,[])

    async def test_sentence_preview_uses_saved_audio_without_provider_calls(self):
        items=[{'text':text,'extension':'wav','audio':base64.b64encode(audio()).decode('ascii')}
               for text in ['playing','country','music from Spotify in the','kitchen.']]
        token=self.manager.import_token()
        await self.manager.import_clips(items,token)
        before=await self.cache.snapshot()
        result=await self.manager.preview_sentence([item['text'] for item in items],token,50)
        self.assertEqual(result['extension'],'wav');self.assertEqual(result['missing'],[])
        self.assertEqual(self.calls,[])
        self.assertEqual(self.usage.snapshot()['total'],0)
        self.assertEqual((await self.cache.snapshot())['bytes'],before['bytes'])
        self.entry.options['elevenlabs_voice']='other'
        with self.assertRaises(ValueError):await self.manager.preview_sentence(['country'],token)

    async def test_saved_sentence_is_reused_by_normal_tts(self):
        token=self.manager.import_token()
        result=await self.manager.save_sentence(['I requested','country','in','kitchen.'],token,60)
        self.assertTrue(result['saved']);self.assertEqual(result['generated_clips'],4)
        self.calls.clear()
        extension,recording=await self.manager.async_get_tts_audio('I requested country in kitchen.','en',{})
        self.assertEqual(extension,'wav');self.assertEqual(self.calls,[])
        self.assertEqual(len(recording),result['bytes'])
        await self.manager.save_sentence(['I requested','jazz','in','kitchen.'],token)
        self.assertEqual(self.calls,[('tts.elevenlabs','jazz')])

    async def test_save_rejects_changed_voice_and_disabled_cache_before_provider(self):
        token=self.manager.import_token()
        self.entry.options['elevenlabs_voice']='other'
        with self.assertRaises(ValueError):await self.manager.save_sentence(['country'],token)
        self.entry.options['cache_enabled']=False
        with self.assertRaises(ValueError):await self.manager.save_sentence(['country'],self.manager.import_token())
        self.assertEqual(self.calls,[])

    def real_provider(self):
        """Remove the provider mock so these tests reach HA's media-source boundary."""
        self.provider_patch.stop()
        provider = importlib.import_module('phrase_manager_fixture.voice_provider')
        self.manager.hass.data = {'declan_local': {'voice_manager': self.manager}}
        provider.tts.generate_media_source_id = lambda hass, text, **kwargs: (kwargs['engine'], text)
        self.entry.options.update(fallback_tts='tts.jarvis_xtts', phrase_library_enabled=False)
        return provider

    async def test_real_primary_failure_ignores_stored_xtts_fallback(self):
        self.entry.options['fallback_tts'] = 'tts.jarvis_xtts'
        provider = self.real_provider()

        async def fetch(hass, source):
            self.calls.append(source)
            raise self.module.HomeAssistantError('offline')

        provider.tts.async_get_media_source_audio = fetch
        with self.assertRaisesRegex(self.module.HomeAssistantError, 'no cached alternative'):
            await self.manager.async_get_tts_audio('Test outage.', 'en', {})
        self.assertEqual(self.calls, [('tts.elevenlabs', 'Test outage.')])
        self.assertEqual(self.usage.snapshot()['provider_failures'], {'primary': 1})


    async def test_real_provider_rejects_renamed_manager_and_preserves_cancellation(self):
        provider = self.real_provider()
        self.manager.entity_id = 'tts.declan'
        for recursive in ('tts.declan', 'tts.jarvis_voice_manager', 'tts.jarvis_voice_manager_2'):
            with self.assertRaises(ValueError):
                await provider.generate_from_existing_tts(self.manager.hass, provider_entity_id=recursive, text='Hello')
        async def cancelled(hass, source):
            raise asyncio.CancelledError()
        provider.tts.async_get_media_source_audio = cancelled
        with self.assertRaises(asyncio.CancelledError):
            await self.manager.async_get_tts_audio('Cancelled request.', 'en', {})
        self.assertEqual(self.usage.snapshot()['provider_failures'], {})

    async def test_real_hung_primary_reports_failure_with_deadline(self):
        provider = self.real_provider()
        async def fetch(hass, source):
            self.calls.append(source)
            await asyncio.Event().wait()
        provider.tts.async_get_media_source_audio = fetch
        with patch.object(provider, 'PROVIDER_TIMEOUT_SECONDS', 0.02):
            with self.assertRaises(self.module.HomeAssistantError):
                await self.manager.async_get_tts_audio('Primary stalled.', 'en', {})
        self.assertEqual([source[0] for source in self.calls], ['tts.elevenlabs'])
        self.assertEqual(self.usage.snapshot()['total'], 0)
        self.assertEqual(self.usage.snapshot()['provider_failures'], {'primary': 1})

    async def test_provider_exception_details_are_not_logged(self):
        async def fail(hass, **kwargs):
            raise self.module.HomeAssistantError('PRIVATE_SPEECH_OR_KEY')
        with patch.object(self.module, 'generate_from_existing_tts', fail):
            with self.assertLogs(self.module._LOGGER, level='WARNING') as logs:
                with self.assertRaises(self.module.HomeAssistantError):
                    await self.manager.async_get_tts_audio('Private message.', 'en', {})
        self.assertNotIn('PRIVATE_SPEECH_OR_KEY', '\n'.join(logs.output))
        self.assertEqual(self.usage.snapshot()['provider_failures'], {'primary': 1})

    async def test_cached_alternative_honors_guest_mode_privacy(self):
        catalogue={'Home':{'on':['PRIVATE_HOME_A','PRIVATE_HOME_B']},
                   'Guest':{'on':['Guest A','Guest B']}}
        self.manager.hass.data={'declan_local':{'settings':{'guest_mode':'input_boolean.permission', 'visitors_present':'input_boolean.company'}}}
        self.manager.hass.states=types.SimpleNamespace(get=lambda entity:types.SimpleNamespace(state='on' if entity=='input_boolean.permission' else 'off'))
        async def executor(fn, *args): return catalogue
        self.manager.hass.async_add_executor_job=executor
        async def find(**kwargs):
            return ('wav', audio()) if kwargs['text'] in {'PRIVATE_HOME_B','Guest B'} else None
        with patch.object(self.cache,'find_cached_audio',find):
            private=await self.manager._cached_primary_alternative('PRIVATE_HOME_A','tts.elevenlabs','v1','en',{})
            guest=await self.manager._cached_primary_alternative('Guest A','tts.elevenlabs','v1','en',{})
        self.assertIsNone(private)
        self.assertEqual(guest,('wav',audio()))

    async def test_primary_budget_applies_to_admin_and_runtime_without_blocking_saved_audio(self):
        self.entry.options.update(primary_daily_character_limit=5,phrase_library_enabled=False)
        await self.manager.prepare_phrase('hello','sentence')
        self.assertEqual(len(self.calls),1)
        await self.manager.async_get_tts_audio('hello','en',{})
        self.assertEqual(len(self.calls),1)
        with self.assertRaises(ValueError):await self.manager.prepare_phrase('another','sentence')
        with self.assertRaises(self.module.HomeAssistantError):
            await self.manager.async_get_tts_audio('another','en',{})
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.manager.budget_snapshot()['primary_attempts'],1)

    async def test_catalogue_review_is_read_only_and_missing_preparation_is_exact_reusable_audio(self):
        async def execute(fn,*args):return {'Guest':{'on':['A static reply.','Another static reply.']}}
        self.manager.hass.async_add_executor_job=execute
        plan=await self.manager.catalogue.plan(['Guest'])
        self.assertEqual(self.calls,[])
        self.assertEqual(plan['missing_count'],2)
        line=plan['lines'][0]
        first=await self.manager.catalogue.prepare(plan['token'],line['id'])
        self.assertTrue(first['saved'])
        self.assertEqual(self.calls,[('tts.elevenlabs',line['text'])])
        await self.manager.catalogue.prepare(plan['token'],line['id'])
        await self.manager.async_get_tts_audio(line['text'],'en',{})
        self.assertEqual(len(self.calls),1)
        next_plan=await self.manager.catalogue.plan(['Guest'])
        self.assertEqual(next_plan['missing_count'],1)

    async def test_catalogue_requires_current_review_identity_and_rejects_dynamic_facts(self):
        async def execute(fn,*args):return {'Home':{'on':['Static reply.']}}
        self.manager.hass.async_add_executor_job=execute
        plan=await self.manager.catalogue.plan(['Home'])
        self.entry.options['cache_revision']='new'
        with self.assertRaises(ValueError):await self.manager.catalogue.prepare(plan['token'],plan['lines'][0]['id'])
        self.assertEqual(self.calls,[])
        async def dynamic(fn,*args):return {'Home':{'on':['The temperature is {temperature}.']}}
        self.manager.hass.async_add_executor_job=dynamic
        with self.assertRaises(ValueError):await self.manager.catalogue.plan(['Home'])
        self.assertEqual(self.calls,[])

    async def test_catalogue_failed_attempt_is_not_silently_billed_again(self):
        async def execute(fn,*args):return {'Guest':{'on':['Static reply.']}}
        self.manager.hass.async_add_executor_job=execute
        plan=await self.manager.catalogue.plan(['Guest'])
        async def fail(hass,**kwargs):
            self.calls.append(kwargs['text'])
            raise self.module.HomeAssistantError('provider unavailable')
        with patch.object(self.module,'generate_from_existing_tts',fail):
            with self.assertRaises(self.module.HomeAssistantError):await self.manager.catalogue.prepare(plan['token'],plan['lines'][0]['id'])
            with self.assertRaises(ValueError):await self.manager.catalogue.prepare(plan['token'],plan['lines'][0]['id'])
        self.assertEqual(self.calls,['Static reply.'])
        self.assertEqual(self.manager.budget_snapshot()['primary_attempts'],1)

    async def test_catalogue_actual_home_and_guest_file_is_reviewable_without_generation(self):
        async def executor(fn,*args):return fn(*args)
        self.manager.hass.async_add_executor_job=executor
        plan=await self.manager.catalogue.plan(['Home','Guest'])
        self.assertEqual({line['mode'] for line in plan['lines']},{'Home','Guest'})
        self.assertGreater(plan['missing_count'],20)
        self.assertEqual(plan['voice']['provider'],'tts.elevenlabs')
        self.assertEqual(self.calls,[])

    async def test_catalogue_expiry_cost_change_and_disabled_storage_require_new_review(self):
        async def execute(fn,*args):return {'Guest':{'on':['Static reply.']}}
        self.manager.hass.async_add_executor_job=execute
        self.manager.catalogue.clock=lambda:0
        plan=await self.manager.catalogue.plan(['Guest'])
        self.manager.catalogue.clock=lambda:901
        with self.assertRaises(ValueError):await self.manager.catalogue.prepare(plan['token'],plan['lines'][0]['id'])
        self.manager.catalogue.clock=lambda:902
        plan=await self.manager.catalogue.plan(['Guest'])
        self.entry.options['primary_daily_character_limit']=100
        with self.assertRaises(ValueError):await self.manager.catalogue.prepare(plan['token'],plan['lines'][0]['id'])
        plan=await self.manager.catalogue.plan(['Guest'])
        self.cache.min_free_bytes=10**30
        with self.assertRaises(ValueError):await self.manager.catalogue.prepare(plan['token'],plan['lines'][0]['id'])
        self.assertEqual(self.calls,[])

    async def test_catalogue_and_runtime_coalesce_one_billable_attempt(self):
        async def execute(fn,*args):return {'Guest':{'on':['Static reply.']}}
        self.manager.hass.async_add_executor_job=execute
        plan=await self.manager.catalogue.plan(['Guest'])
        started,release=asyncio.Event(),asyncio.Event()
        async def generate(hass,**kwargs):
            self.calls.append(kwargs['text']);started.set();await release.wait()
            return 'wav',audio()
        with patch.object(self.module,'generate_from_existing_tts',generate):
            preparing=asyncio.create_task(self.manager.catalogue.prepare(plan['token'],plan['lines'][0]['id']))
            await started.wait()
            speaking=asyncio.create_task(self.manager.async_get_tts_audio('Static reply.','en',{}))
            await asyncio.sleep(0)
            release.set()
            await asyncio.gather(preparing,speaking)
        self.assertEqual(self.calls,['Static reply.'])
        self.assertEqual(self.manager.budget_snapshot()['primary_attempts'],1)

    async def test_setup_loads_persistent_budget_before_registering_and_does_not_reset_on_reload(self):
        storage=types.ModuleType('homeassistant.helpers.storage')
        loads=[]
        day=self.manager._budget.today()
        class Store:
            def __init__(self,*args):pass
            async def async_load(self):
                loads.append(True)
                return {'day':day,'primary_characters':7,'primary_attempts':1,'fallback_characters':0,'fallback_attempts':0}
            async def async_save(self,data):pass
        storage.Store=Store
        hass=types.SimpleNamespace(data={},config=types.SimpleNamespace(path=lambda name:str(Path(self.temp.name)/name)))
        entities=[]
        with patch.dict(sys.modules,{'homeassistant.helpers.storage':storage}):
            await self.module.async_setup_entry(hass,self.entry,entities.extend)
            await self.module.async_setup_entry(hass,self.entry,entities.extend)
        self.assertEqual(len(loads),1)
        self.assertEqual(entities[-1].budget_snapshot()['primary_characters'],7)
        self.assertIs(entities[-1]._budget,entities[0]._budget)

    async def test_catalogue_cannot_bill_for_previously_saved_line_removed_after_review(self):
        async def execute(fn,*args):return {'Guest':{'on':['Saved line.','Missing line.']}}
        self.manager.hass.async_add_executor_job=execute
        await self.manager.prepare_phrase('Saved line.','sentence')
        plan=await self.manager.catalogue.plan(['Guest'])
        line=next(line for line in plan['lines'] if line['cached'])
        key=self.cache.key(text='Saved line.',extension='wav',**self.manager.import_identity())
        self.cache.path_for(key,'wav').unlink()
        with self.assertRaises(ValueError):await self.manager.catalogue.prepare(plan['token'],line['id'])
        self.assertEqual(len(self.calls),1)

    async def test_declan_display_keeps_registration_and_pronunciation_keeps_written_cache_identity(self):
        self.assertEqual(self.manager._attr_name,'Declan Voice Manager')
        self.assertEqual(self.manager._attr_unique_id,'test_voice_manager')
        written='Good morning, Edd.'
        await self.manager.prepare_phrase(written,'sentence')
        self.assertEqual(self.calls,[('tts.elevenlabs','Good morning, Ed.')])
        await self.manager.async_get_tts_audio(written,'en',{})
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.manager.budget_snapshot()['primary_characters'],len('Good morning, Ed.'))

if __name__=='__main__':unittest.main()
