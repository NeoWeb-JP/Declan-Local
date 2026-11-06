"""Corrections and factual follow-ups with real agent code and simulated HA."""
import asyncio
from datetime import datetime, timezone
import types
import unittest
from unittest.mock import patch

import test_agent_dialogue as env
from jarvis_test import information_dialogue as info
from jarvis_test.corrections import final_request


class Grammar(unittest.TestCase):
    def test_latest_command_and_preview_survive_each_marker(self):
        for marker in ('no I mean', 'actually', 'rather', 'sorry I meant', 'scratch that'):
            with self.subTest(marker=marker):
                text, changed = final_request('preview turn office on, '+marker+' turn kitchen off')
                self.assertTrue(changed)
                self.assertEqual(text, 'preview turn kitchen off')
        self.assertEqual(final_request('turn office on, actually turn kitchen off, no I mean turn bedroom on'),
                         ('turn bedroom on', True))
        for prefix in ('dry run ', 'what would you do if i said '):
            self.assertEqual(final_request(prefix+'turn office on, no I mean turn bedroom off'),
                             (prefix+'turn bedroom off',True))

    def test_negation_titles_and_rather_than_are_not_discarded(self):
        for text in ('turn on "actually turn off"', "I would rather than turn kitchen off", "turn office on rather than turn kitchen off"):
            self.assertEqual(final_request(text), (text, False))
        with self.assertRaises(ValueError):
            final_request("don't actually turn office on")
        with self.assertRaises(ValueError):
            final_request('turn office on, scratch that')

    def test_final_stop_and_relative_adjustment(self):
        self.assertEqual(final_request('turn office on, no stop'), ('stop', True))
        self.assertEqual(final_request('actually make them a bit dimmer'), ('make them a bit dimmer', True))


class Information(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.hass=env.fixtures.Hass()
        self.hass.data={'declan_local':{'settings':{'weather':'weather.home','thermostat':'climate.home'}}}
        self.hass.config=types.SimpleNamespace(time_zone='Europe/London',units=types.SimpleNamespace(temperature_unit='°C'))
        self.hass.states.values['weather.home']=env.fixtures.State('weather.home','Weather','sunny')
        self.hass.states.values['weather.home'].attributes={'temperature':12,'temperature_unit':'°C'}
        self.hass.states.values['climate.home']=env.fixtures.State('climate.home','Thermostat','heat')
        self.hass.states.values['climate.home'].attributes={'current_temperature':21,'temperature_unit':'°C'}
        self.calls=[]
        self.entries=[]
        async def service(*args,**kwargs):
            self.calls.append((args,kwargs))
            return {'weather.home':{'forecast':self.entries}}
        self.hass.services=types.SimpleNamespace(async_call=service)
        self.now=datetime(2026,10,31,12,tzinfo=timezone.utc)

    async def test_current_outdoor_and_indoor_readings_are_fresh_without_forecast_calls(self):
        request=info.parse("what's the temperature")
        self.assertIn('21', (await info.read(self.hass,request))[0])
        outside=info.parse('what about outside', 'temperature')
        self.hass.states.values['weather.home'].attributes['temperature']=8
        self.assertIn('8', (await info.read(self.hass,outside))[0])
        self.assertEqual(self.calls,[])

    async def test_future_temperature_is_explicitly_outdoors(self):
        self.entries=[{'datetime':'2026-11-01T00:00:00Z','temperature':8}]
        response,_=await info.read(self.hass,info.parse('and tomorrow','temperature'),now=self.now)
        self.assertIn('outdoors',response)
        self.assertNotIn('inside',response)

    async def test_tomorrow_matches_date_instead_of_using_first_forecast(self):
        self.entries=[{'datetime':'2026-10-31T00:00:00Z','condition':'sunny','temperature':99},
                      {'datetime':'2026-11-01T00:00:00Z','condition':'rainy','temperature':10,'templow':4}]
        text,available=await info.read(self.hass,info.parse('and tomorrow','weather'),now=self.now)
        self.assertTrue(available)
        self.assertEqual(text,'Tomorrow, the forecast is rain, 4 to 10 °C.')
        self.assertEqual(self.calls[0][0],('weather','get_forecasts',{'entity_id':'weather.home','type':'daily'}))
        self.assertTrue(self.calls[0][1]['return_response'])

    async def test_later_selects_nearest_future_hour_not_past_or_far_future(self):
        self.entries=[{'datetime':'2026-10-31T20:00:00Z','condition':'sunny'},
                      {'datetime':'2026-10-31T11:00:00Z','condition':'sunny'},
                      {'datetime':'2026-10-31T14:00:00Z','condition':'cloudy'},
                      {'datetime':'2026-10-31T13:00:00Z','condition':'rainy'}]
        text,available=await info.read(self.hass,info.parse('what about later','weather'),now=self.now)
        self.assertTrue(available)
        self.assertEqual(text,'At 1:00 PM, the forecast is rain.')

    async def test_missing_stale_naive_or_nonnumeric_data_never_invents_weather(self):
        for entries in ([], [{'datetime':'2026-10-30T00:00:00Z','temperature':18}],
                        [{'datetime':'2026-11-01T00:00:00','temperature':18}],
                        [{'datetime':'2026-11-01T00:00:00Z','temperature':float('nan')}]):
            self.entries=entries
            text,available=await info.read(self.hass,info.parse('weather tomorrow'),now=self.now)
            self.assertFalse(available)
            self.assertNotIn('sunny',text)
            self.assertNotIn('nan',text)

    async def test_service_failure_timeout_and_cancellation(self):
        async def failed(*args,**kwargs):raise info.HomeAssistantError('private failure')
        self.hass.services.async_call=failed
        text,available=await info.read(self.hass,info.parse('weather tomorrow'),now=self.now)
        self.assertFalse(available)
        self.assertNotIn('private',text)
        async def hung(*args,**kwargs):await asyncio.Event().wait()
        self.hass.services.async_call=hung
        with patch.object(info,'FORECAST_TIMEOUT',0.01):
            self.assertFalse((await info.read(self.hass,info.parse('weather tomorrow'),now=self.now))[1])
        async def cancelled(*args,**kwargs):raise asyncio.CancelledError()
        self.hass.services.async_call=cancelled
        with self.assertRaises(asyncio.CancelledError):
            await info.read(self.hass,info.parse('weather tomorrow'),now=self.now)

    def test_dst_repeat_uses_instant_order(self):
        from zoneinfo import ZoneInfo
        now=datetime(2026,10,25,1,45,tzinfo=ZoneInfo('Europe/London'),fold=0)
        entries=[{'datetime':'2026-10-25T01:15:00Z','condition':'rainy'}]
        self.assertIsNotNone(info.select_forecast(entries,'later',now))

    def test_unrelated_or_negative_text_does_not_become_forecast(self):
        self.assertIsNone(info.parse("don't tell me weather tomorrow"))
        self.assertIsNone(info.parse('turn tomorrow lamp off','weather'))
        self.assertTrue(info.parse('and tomorrow').get('clarify'))
        self.assertTrue(info.parse('and tomorrow','time').get('clarify'))


class AgentInformation(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        env.Dialogue.setUp(self)
        self.clock=100
        self.time_patch=patch.object(env.module,'monotonic',lambda:self.clock)
        self.time_patch.start();self.addCleanup(self.time_patch.stop)
        self.hass.data={'declan_local':{'settings':{'weather':'weather.home'}}}
        self.hass.config=types.SimpleNamespace(time_zone='Europe/London',units=types.SimpleNamespace(temperature_unit='°C'))
        weather=env.fixtures.State('weather.home','Weather','sunny')
        weather.attributes={'temperature':12,'temperature_unit':'°C'}
        self.hass.states.values['weather.home']=weather
        self.forecast=[{'datetime':'2026-11-01T00:00:00Z','condition':'rainy','temperature':11,'templow':6},
                       {'datetime':'2026-10-31T13:00:00Z','condition':'cloudy','temperature':10}]
        async def service(*args,**kwargs):
            self.hass.services.calls.append((args,kwargs))
            if args[:2]==('weather','get_forecasts'):
                return {'weather.home':{'forecast':self.forecast}}
            return {}
        self.hass.services.async_call=service
        async def reader(hass,request,context):
            return await info.read(hass,request,context,now=datetime(2026,10,31,12,tzinfo=timezone.utc))
        self.read_patch=patch.object(env.module,'read_information',reader)
        self.read_patch.start();self.addCleanup(self.read_patch.stop)

    async def test_weather_topic_followups_use_fresh_sources(self):
        first=await self.agent.async_handle(env.UserInput("what's the weather"))
        self.assertIn('sunny',first.response.speech)
        future=await self.agent.async_handle(env.UserInput('and tomorrow'))
        self.assertIn('6 to 11',future.response.speech)
        self.hass.states.values['weather.home'].attributes['temperature']=4
        outside=await self.agent.async_handle(env.UserInput('what about outside'))
        self.assertIn('4 °C',outside.response.speech)
        later=await self.agent.async_handle(env.UserInput('what about later'))
        self.assertIn('1:00 PM',later.response.speech)
        self.assertTrue(all(call[0][0]=='weather' for call in self.hass.services.calls))

    async def test_topic_expiry_other_conversation_and_preview_cannot_call_weather(self):
        await self.agent.async_handle(env.UserInput('weather'))
        other=await self.agent.async_handle(env.UserInput('and tomorrow','other'))
        self.assertIn('Were you asking',other.response.speech)
        preview=await self.agent.async_handle(env.UserInput('preview weather tomorrow'))
        self.assertIn('Preview only',preview.response.speech)
        self.clock=221
        expired=await self.agent.async_handle(env.UserInput('and tomorrow'))
        self.assertIn('Were you asking',expired.response.speech)
        self.assertEqual(self.hass.services.calls,[])

    async def test_recognized_speakers_and_satellites_do_not_share_topic_or_lights(self):
        speaker=['Jaco']
        with patch.object(env.module,'bridge_profile',lambda *args:speaker[0]):
            await self.agent.async_handle(env.UserInput('weather'))
            speaker[0]='Edd'
            result=await self.agent.async_handle(env.UserInput('and tomorrow'))
            self.assertIn('Were you asking',result.response.speech)
            speaker[0]='Jaco'
            other=env.UserInput('and tomorrow')
            other.satellite_id='assist_satellite.kitchen'
            result=await self.agent.async_handle(other)
            self.assertIn('Were you asking',result.response.speech)
            await self.agent.async_handle(env.UserInput('office on'))
            speaker[0]='Edd'
            result=await self.agent.async_handle(env.UserInput('turn them off'))
            self.assertIn('Which lights',result.response.speech)
        self.assertEqual(len(self.hass.services.calls),1)
        self.assertEqual(self.hass.services.calls[0][0][0],'light')

    async def test_preview_correction_and_negative_voice_command_execute_nothing(self):
        result=await self.agent.async_handle(env.UserInput('preview turn office on, actually turn bedroom off'))
        self.assertIn('Preview only',result.response.speech)
        result=await self.agent.async_handle(env.UserInput("don't actually turn office off",device='voice'))
        self.assertIn('Nothing was run',result.response.speech)
        self.assertEqual(self.hass.services.calls,[])

    async def test_unsupported_final_action_does_not_execute_discarded_lights(self):
        result=await self.agent.async_handle(env.UserInput('turn office on, no I mean unlock the front door'))
        self.assertIn('Nothing was run',result.response.speech)
        self.assertEqual(self.hass.services.calls,[])

    async def test_prior_committed_light_action_is_adjusted_as_a_new_command(self):
        await self.agent.async_handle(env.UserInput('office on'))
        result=await self.agent.async_handle(env.UserInput('actually make them a bit dimmer'))
        self.assertEqual(len(self.hass.services.calls),2)
        self.assertEqual(self.hass.services.calls[-1][0][:2],('light','turn_on'))
        self.assertIn('light.office',self.hass.services.calls[-1][0][2]['entity_id'])
        await self.agent.async_handle(env.UserInput('rather turn them off'))
        self.assertEqual(self.hass.services.calls[-1][0][:2],('light','turn_off'))

    async def test_corrected_stop_is_silent_and_never_executes_discarded_lights(self):
        self.hass.data['declan_local']['settings']['satellite_media_players']={
            'assist_satellite.bedroom':'media_player.bedroom'}
        user=env.UserInput('lamp on');user.satellite_id='assist_satellite.bedroom'
        await self.agent.async_handle(user)
        user=env.UserInput('turn office on, no stop');user.satellite_id='assist_satellite.bedroom'
        reply=await self.agent.async_handle(user)
        self.assertEqual(reply.response.speech,'')
        self.assertEqual(len(self.hass.services.calls),1)
        self.assertEqual(self.hass.services.calls[0][0][:2],('media_player','media_stop'))
        self.assertFalse(self.agent._pending_clarifications)

    async def test_unrelated_action_clears_weather_topic(self):
        await self.agent.async_handle(env.UserInput('weather'))
        await self.agent.async_handle(env.UserInput('office on'))
        result=await self.agent.async_handle(env.UserInput('and tomorrow'))
        self.assertIn('Were you asking',result.response.speech)
        self.assertEqual(len(self.hass.services.calls),1)

    async def test_preview_correction_preserves_pending_clarification(self):
        await self.agent.async_handle(env.UserInput('lamp on'))
        pending=dict(self.agent._pending_clarifications)
        await self.agent.async_handle(env.UserInput('preview turn office on, no I mean turn bedroom off'))
        self.assertEqual(self.agent._pending_clarifications,pending)
        self.assertEqual(self.hass.services.calls,[])

    async def test_stop_during_forecast_discards_late_reply_and_topic(self):
        started,release=asyncio.Event(),asyncio.Event()
        async def delayed(*args):
            started.set()
            await release.wait()
            return 'Forecast returned after stop.',True
        with patch.object(env.module,'read_information',delayed):
            task=asyncio.create_task(self.agent.async_handle(env.UserInput('weather tomorrow')))
            await started.wait()
            stopped=await self.agent.async_handle(env.UserInput('stop'))
            self.assertEqual(stopped.response.speech,'')
            release.set()
            late=await task
        self.assertEqual(late.response.speech,'')
        self.assertFalse(self.agent._information_topics)
        self.assertFalse(self.agent._information_runs)
