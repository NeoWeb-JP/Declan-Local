"""Bounded local agent with preflight validation and previews."""
import asyncio
import logging
import re
from time import perf_counter, monotonic
from uuid import uuid4
from .satellite_stop import is_spoken_stop, stop_player
from .understanding import normalize_request
from .media_search import parse_search
from .media_search_adapters import search as search_media
from .settings import get
from .speaker_identity import unwrap, bridge_profile
from .morning import morning_reply
from .social import social_reply
from .timers import parse as parse_timer
from .followup import followup, followup_steps, additional_room
from .conversation_memory import context_key, context_followup
from .learning import observe as observe_learning, resolve_alias
from .clarification import request as clarification_request, resolve as clarification_resolve
from .personality import confirmation
from .audience import mode as audience_mode
from .transcript import correct
from .corrections import final_request
from .cross_corrections import corrected_followup
from .verify import verify
from .device_control import apply_lighting, lighting_report
from .discovery import lighting, display_name
from homeassistant.components import conversation
from homeassistant.helpers import intent
from homeassistant.exceptions import HomeAssistantError
from .planner import plan
from .status import answer
from .information_dialogue import parse as parse_information, read as read_information
from .speech import recover_off
from .room_context import source_area, apply_room
from datetime import datetime, timezone

_LOGGER = logging.getLogger(__name__)

class JarvisAgent(conversation.ConversationEntity):
    _attr_supported_features = conversation.ConversationEntityFeature.CONTROL
    _attr_name = 'Declan'
    _attr_unique_id = 'jarvis_local_test'

    def __init__(self, hass):
        self.hass = hass
        self._lock = asyncio.Lock()
        self._recent_lights = {}
        self._pending_clarifications = {}
        self._voice_markers = {}
        self._information_topics = {}
        self._information_runs = {}
        self._previous_failed = {}

    @property
    def supported_languages(self):
        return ['en']

    async def async_process(self, user_input):
        return await self.async_handle(user_input)

    async def async_handle(self, user_input, area_override=None):
        start = perf_counter()
        result = intent.IntentResponse(language=user_input.language)
        steps=[]
        preview=False
        area=None
        resolved_text=""
        outcome='rejected'
        failure=None
        media_report=None
        conversation_id=user_input.conversation_id or uuid4().hex
        memory_key=context_key(user_input,conversation_id,area_override=area_override)
        now=monotonic()
        self._recent_lights={k:v for k,v in self._recent_lights.items() if now-v['at'] < 120}
        self._previous_failed={k:v for k,v in self._previous_failed.items() if now-v['at'] < 90}
        self._pending_clarifications={k:v for k,v in self._pending_clarifications.items() if now-v['at'] < 120}
        self._information_topics={k:v for k,v in getattr(self,'_information_topics',{}).items() if now-v['at'] < 120}
        self._information_runs=getattr(self,'_information_runs',{})
        continue_conversation=False
        followup_used=False
        corrections=[]
        self_corrected=False
        command_text=user_input.text
        cfg=self.hass.data.get('jarvis_local',{}).get('voice_id_config',{})
        voice_profile=bridge_profile(command_text,cfg.get('profiles',{}))
        if command_text.startswith('JVS1.'):
            cfg=self.hass.data.get('jarvis_local',{}).get('voice_id_config',{})
            command_text,voice_profile=unwrap(command_text,cfg.get('secret'),cfg.get('profiles',{}),self._voice_markers)
            if not command_text:command_text=''
        memory_key=context_key(user_input,conversation_id,voice_profile,area_override)
        original_text=str(command_text)
        previous_failure=self._previous_failed.pop(memory_key,None)
        cross_corrected=False
        try:
            replacement=corrected_followup(command_text,previous_failure)
            if replacement is not None:
                command_text=replacement
                cross_corrected=True
        except ValueError as err:
            # Preserve the explicit error for the normal preflight failure path.
            cross_error=err
        else:
            cross_error=None
        command_text=resolve_alias(self.hass,command_text)
        command_text,language_changes=normalize_request(command_text)
        corrections.extend(language_changes)
        correction_error=cross_error
        if cross_corrected:
            corrections.append('corrected previous failed command')
        request_preview=command_text.lower().startswith(('preview ', 'dry run ', 'what would you do if i said '))
        try:
            if correction_error is not None:
                raise correction_error
            command_text,self_corrected=final_request(command_text)
        except ValueError as err:
            correction_error=err
            if not request_preview:
                self._pending_clarifications.pop(memory_key,None)
                self._information_runs.pop(memory_key,None)
        if self_corrected:
            corrections.append('superseded earlier command')
            command_text,language_changes=normalize_request(command_text)
            corrections.extend(language_changes)
            request_preview=command_text.lower().startswith(('preview ', 'dry run ', 'what would you do if i said '))
            if not request_preview:
                self._pending_clarifications.pop(memory_key,None)
                self._information_runs.pop(memory_key,None)
        # Bypass the action lock so running routines cannot delay a stop.
        if is_spoken_stop(command_text):
            self._pending_clarifications.pop(memory_key, None)
            self._recent_lights.pop(memory_key, None)
            self._information_topics.pop(memory_key, None)
            self._information_runs.pop(memory_key, None)
            stop_report = await stop_player(self.hass, user_input)
            # Match the existing opt-in, bounded diagnostics history. Never speak
            # routing failures or claim that playback or barge-in was verified.
            if self.hass.data.get('jarvis_local', {}).get('debug_enabled', False):
                record = {
                    'time': datetime.now(timezone.utc).isoformat(),
                    'received_text': original_text, 'resolved_text': command_text,
                    'speaker_personalized': bool(voice_profile),
                    'transcript_corrections': corrections, 'device_id': getattr(user_input, 'device_id', None),
                    'satellite_id': getattr(user_input, 'satellite_id', None),
                    'area': None, 'preview': False, 'followup_used': False,
                    'steps': ([{'kind': 'media_stop', 'label': 'send silent stop request',
                                'data': {'entity_id': stop_report['media_player_id']},
                                'unverified': True}] if stop_report['service_called'] else []),
                    'outcome': stop_report['outcome'],
                    'error': ('Media stop request failed.' if stop_report['outcome'] == 'failed' else None),
                    'stop': stop_report, 'response': '',
                    'elapsed_ms': round((perf_counter() - start) * 1000),
                }
                history = self.hass.data['jarvis_local'].setdefault('diagnostics', [])
                history.append(record)
                del history[:-20]
            result.async_set_speech('', extra_data={'jarvis_local': {'trackable': False}})
            return conversation.ConversationResult(
                response=result, conversation_id=conversation_id,
                continue_conversation=False)
        try:
            if correction_error:
                raise correction_error
            area=area_override or source_area(self.hass,user_input)
            media_request=parse_search(command_text)
            previous_topic=self._information_topics.get(memory_key,{})
            information_request=parse_information(command_text,previous_topic.get('topic'))
            if media_request is None and (getattr(user_input,'device_id',None) or getattr(user_input,'satellite_id',None)):
                command_text,stt_corrections=correct(self.hass,command_text,area)
                corrections.extend(stt_corrections)
            stop_requested=bool(re.fullmatch(r'(?:jarvis[ ,]+)?(?:no[ ,]+)?(?:stop|stop that|cancel|cancel that|never mind|nevermind|leave it)[.!? ]*',command_text.strip(),re.I))
            timer_request=None if stop_requested else parse_timer(command_text)
            pending=self._pending_clarifications.get(memory_key) if not request_preview else None
            resolution,entity_id=clarification_resolve(pending,command_text) if pending else (None,None)
            social = social_reply(command_text, voice_profile if audience_mode(self.hass) == 'Home' else None, self.hass.data.setdefault('jarvis_local',{}).setdefault('social_history',{})) if not pending else None
            if information_request is not None:
                if not request_preview:
                    self._pending_clarifications.pop(memory_key,None)
                steps=[information_request]
                preview=information_request['preview']
                followup_used=information_request['followup']
                resolved_text=command_text
            elif media_request is not None:
                if not request_preview:
                    self._pending_clarifications.pop(memory_key,None)
                    self._recent_lights.pop(memory_key,None)
                steps=[media_request]
                preview=media_request['preview']
                resolved_text=command_text
            elif stop_requested:
                self._pending_clarifications.pop(memory_key,None)
                self._recent_lights.pop(memory_key,None)
                steps=[{'kind':'text','response':'Cancelled. Nothing was run.' if pending and resolution == 'cancel' else '','label':'stop pending conversation'}]
            elif social is not None:
                steps=[{'kind':'text','response':social,'label':'answer greeting'}]
            elif timer_request is not None:
                self._pending_clarifications.pop(memory_key,None)
                steps=[{'kind':'timer','data':timer_request,'label':'handle timer'}]
            elif pending and resolution == 'cancel':
                self._pending_clarifications.pop(memory_key,None)
                steps=[{'kind':'text','response':'Cancelled. Nothing was run.','label':'cancel clarification'}]
            elif pending and resolution == 'resolved':
                self._pending_clarifications.pop(memory_key,None)
                resolved_text='turn '+pending['action']+' '+entity_id
                preview=pending['preview']
                step=lighting(self.hass,resolved_text)
                if step is None:raise ValueError('That light is no longer available. Nothing was run.')
                steps=[step]
                followup_used=True
            elif pending and not re.search(r'\b(?:turn|switch|set|dim|brighten|play|preview|good|cancel)\b',command_text,re.I):
                steps=[{'kind':'text','response':'I am still not sure which light you mean. '+pending['question'],'label':'clarify light'}]
                continue_conversation=True
            else:
                if pending:self._pending_clarifications.pop(memory_key,None)
                ambiguous=clarification_request(self.hass,command_text,area)
                if ambiguous:
                    ambiguous['at']=now
                    previous=self._recent_lights.get(memory_key)
                    if previous and len(previous['ids']) == 1:
                        ambiguous['previous_id']=previous['ids'][0]
                    self._pending_clarifications[memory_key]=ambiguous
                    while len(self._pending_clarifications)>64:del self._pending_clarifications[next(iter(self._pending_clarifications))]
                    steps=[{'kind':'text','response':ambiguous['question'],'label':'clarify light'}]
                    continue_conversation=True
                else:
                    continuation=followup(command_text)
                    if continuation is not None:
                        previous=self._recent_lights.get(memory_key)
                        if previous is None:
                            raise ValueError('Which lights do you mean? Please name the room or lights.')
                        resolved_text,preview=continuation
                        steps=followup_steps(self.hass,resolved_text,previous['ids'])
                        followup_used=True
                    else:
                        previous=self._recent_lights.get(memory_key)
                        extra=context_followup(command_text, previous) or additional_room(command_text, previous.get('action') if previous else None)
                        resolved_text=apply_room(extra or command_text,area,self.hass)
                        steps, preview = plan(self.hass, resolved_text,area)
                        if extra:
                            followup_used=True
        except ValueError as err:
            recovered = recover_off(self.hass, command_text) if correction_error is None and (getattr(user_input, 'device_id', None) or getattr(user_input, 'satellite_id', None)) else None
            if recovered is not None:
                # Retry with the same context; never infer voice recovery from chat.
                from dataclasses import replace
                return await self.async_handle(replace(user_input, text=recovered),area_override)
            speech = str(err)
            if speech.startswith('I did not understand "') and speech.endswith('Try "help" for supported requests.'):
                import random
                speech = random.choice((
                    "What? Put your teeth back in and try that again.",
                    "I speak several languages. Whatever that was isn't one of them.",
                    "Was that a command, or did you just sneeze?",
                    "I'm going to pretend I didn't hear that. Try again, my bru.",
                    "That sounded important. Shame none of it made sense.",
                    "I'm a voice assistant, not a psychic. Give me something to work with.",
                    "Even Alexa would've struggled with that one. And that's saying something.",
                    "Could you repeat that, preferably using actual words?",
                    "Alexa says she understood you. She's lying, obviously.",
                    "That sounded like something you'd ask Alexa. Let's try proper words instead.",
                    "If you wanted a random answer, Alexa's still available. Try again.",
                    "Alexa would have confidently done the wrong thing. I prefer to ask you to repeat it.",
                ))
            failure=str(err)
        else:
            if preview:
                outcome='preview'
                speech = 'Preview only. I would ' + '; then '.join(s['label'] for s in steps) + '. No actions were run.'
            elif self._lock.locked():
                outcome='busy'
                speech = 'I am processing another request. Please try again shortly.'
            else:
                outcome='completed'
                replies = []
                grouped_lighting=(len(steps)>1 and all(s.get('kind') in {'light','switch_light'} for s in steps) and len({s.get('name') for s in steps})==1)
                lighting_succeeded=False
                async with self._lock:
                    try:
                        for step in steps:
                            if step['kind'] == 'information':
                                self._recent_lights.pop(memory_key,None)
                                token=object()
                                self._information_runs[memory_key]=token
                                try:
                                    reply,available=await read_information(self.hass,step,user_input.context)
                                    superseded=self._information_runs.get(memory_key) is not token
                                finally:
                                    if self._information_runs.get(memory_key) is token:
                                        self._information_runs.pop(memory_key,None)
                                if superseded:
                                    outcome='cancelled'
                                    replies.clear()
                                    break
                                step['available']=available
                                replies.append(reply)
                                if available:
                                    self._information_topics[memory_key]={'at':monotonic(),'topic':step['topic']}
                                    while len(self._information_topics)>64:
                                        del self._information_topics[next(iter(self._information_topics))]
                                else:
                                    self._information_topics.pop(memory_key,None)
                                continue
                            if step['kind'] == 'media_search':
                                media_report=await search_media(self.hass,step)
                                replies.append(media_report['response'])
                                continue
                            if step['kind'] == 'timer':
                                replies.append(await self.hass.data['jarvis_local']['timers'].handle(getattr(user_input,'satellite_id',None),step['data']))
                                continue
                            if step['kind'] == 'text':
                                if step.get('label') == 'answer greeting':
                                    replies.append(social_reply(command_text, voice_profile if audience_mode(self.hass) == 'Home' else None, self.hass.data['jarvis_local']['social_history']))
                                else:
                                    replies.append(step['response'])
                                continue
                            if step['kind'] in {'brightness', 'switch_light', 'light'}:
                                calls = step['calls'] if step['kind'] == 'brightness' else [
                                    {'service': step['name'], 'data': step['data']}
                                ]
                                domain = 'switch' if step['kind'] == 'switch_light' else 'light'
                                successes, failures, unknown = [], [], []
                                for call in calls:
                                    ok, failed_ids, unchecked = await apply_lighting(
                                        self.hass, domain, call['service'],
                                        call['data'], user_input.context
                                    )
                                    successes.extend(ok)
                                    failures.extend(failed_ids)
                                    unknown.extend(unchecked)
                                step['succeeded'] = successes
                                step['failed'] = failures
                                step['unverified'] = unknown
                                if failures or unknown:
                                    outcome = 'partial' if successes else 'failed'
                                    if failures:
                                        failure = 'Device command rejected: ' + ', '.join(failures)
                                    message = lighting_report(self.hass, failures, unknown)
                                    if successes:
                                        message = 'Changed ' + ', '.join(display_name(self.hass.states.get(i)) if self.hass.states.get(i) else i.split('.', 1)[-1].replace('_', ' ').title() for i in successes) + '. ' + message
                                    replies.append(message)
                                elif step['kind'] == 'brightness' and not calls:
                                    replies.append('Those lights are off, so I left them off.')
                                elif grouped_lighting:
                                    lighting_succeeded = True
                                else:
                                    action = ('brightness' if step['kind'] == 'brightness'
                                              else 'off' if step['name'] == 'turn_off' else 'on')
                                    fallback = ('Adjusted ' if action == 'brightness'
                                                else 'Turned ' + action + ' ') + step.get('target_label', 'the lights') + '.'
                                    replies.append(await confirmation(
                                        self.hass, user_input.context, fallback, action=action))
                                continue
                            if step['kind'] == 'guest':
                                controller=self.hass.data['jarvis_local'].get('guest_authority')
                                if controller is None:
                                    raise ValueError('Guest handover controller is unavailable')
                                replies.append(await controller.command(step['data'],user_input.context))
                                continue
                            if step['kind'] == 'media_control':
                                await self.hass.services.async_call('media_player',step['name'],step['data'],blocking=True,context=user_input.context)
                                import random
                                replies.append(random.choice((
                                    'Request sent to ' + step['target_label'] + '.',
                                    'Sorted. Alexa would still be thinking about it.',
                                    'Done. Another task Alexa can cross off her imaginary to-do list.',
                                )))
                                continue
                            if step['kind'] == 'music_assistant_play':
                                await self.hass.services.async_call('music_assistant', 'play_media', step['data'], target={'entity_id': step['entity_id']}, blocking=True, context=user_input.context)
                                import random
                                replies.append(random.choice((
                                    'Requested ' + step['data']['media_id'] + ' in ' + step['target_label'] + '.',
                                    'Music requested for ' + step['target_label'] + '. Alexa can sit this one out.',
                                    'On it. No need to ask Alexa three times.',
                                    'Music requested. Alexa, take notes.',
                                )))
                                continue
                            if step['kind'] == 'music':
                                await self.hass.services.async_call('script',step['name'],step['data'],blocking=True,context=user_input.context)
                                replies.append('I requested '+step['data']['music']+' in '+step['data']['location']+'.')
                                continue
                            if step['kind'] == 'status':
                                replies.append(answer(self.hass, step['text']))
                                continue
                            reply = await self.hass.services.async_call(
                                'script', step['name'], step['data'], blocking=True,
                                return_response=True, context=user_input.context)
                            if (reply or {}).get('response'):
                                routine_reply=reply['response']
                                if step['name']=='jarvis_local_good_morning':
                                    if audience_mode(self.hass) == 'Guest':
                                        routine_reply=await confirmation(self.hass,user_input.context,'Good morning. The morning routine is underway.',action='morning')
                                    else:
                                        routine_reply=morning_reply(voice_profile, cfg.get('profiles', {}), self.hass.data.setdefault('jarvis_local', {}).setdefault('morning_history', {}))
                                replies.append(routine_reply)
                    except (HomeAssistantError, ValueError) as err:
                        outcome='failed'
                        failure=str(err)
                        if isinstance(err, HomeAssistantError) and 'tuya' in str(err).lower() and 'reject' in str(err).lower():
                            _LOGGER.warning(
                                'Declan routine %s stopped after Tuya rejected a command: %s. '
                                'Earlier script actions may have run; not retrying automatically.',
                                step.get('name', 'unknown'), err,
                            )
                            replies.append(
                                "Tuya's having a moment and rejected a command. "
                                "I stopped the routine, but some earlier actions may have worked. "
                                "Check the devices before trying again."
                            )
                        else:
                            _LOGGER.exception('Declan routine %s failed', step.get('name', 'unknown'))
                            replies.append('I stopped because an action failed. Earlier actions may already have run. Please check the Home Assistant log before retrying.')
                if grouped_lighting and lighting_succeeded and outcome=='completed':
                    action='off' if steps[0]['name']=='turn_off' else 'on'
                    replies.insert(0,await confirmation(self.hass,user_input.context,'Turning '+action+' the lights.',action=action))
                speech = ' '.join(r for r in replies if r)
                if outcome == 'completed' and self_corrected and not preview and media_report is None and all(s.get('kind') in {'light','switch_light','brightness','action','guest'} for s in steps):
                    speech = await confirmation(self.hass,user_input.context,'Changed your mind? No problem.',action='self_correction') + ' ' + speech
                if outcome in {'completed', 'partial'}:
                    light_ids=[]
                    invalidated=False
                    for step in steps:
                        if step['kind'] in {'light','switch_light'}:
                            light_ids.extend(step.get('succeeded', []))
                        elif step['kind']=='brightness':
                            light_ids.extend(step.get('succeeded', []))
                        elif step['kind'] in {'action','guest'} or step.get('unverified') or step.get('failed'):
                            invalidated=True
                    if invalidated and not light_ids:
                        self._recent_lights.pop(memory_key,None)
                    elif light_ids:
                        self._recent_lights[memory_key]={'at':monotonic(),'ids':list(dict.fromkeys(light_ids)),
                            'action':next((st['name'] for st in reversed(steps)
                                           if st.get('kind') in {'light','switch_light'} and st.get('succeeded')
                                           and st.get('name') in {'turn_on','turn_off'}),None)}
                    while len(self._recent_lights)>64:
                        del self._recent_lights[next(iter(self._recent_lights))]
        if outcome in {'failed','rejected'}:
            self._recent_lights.pop(memory_key,None)
            self._information_topics.pop(memory_key,None)
        elif outcome in {'completed','partial'} and not any(s.get('kind')=='information' for s in steps):
            self._information_topics.pop(memory_key,None)
        if getattr(user_input,'device_id',None) or getattr(user_input,'satellite_id',None):
            speech=speech.replace(' Try "help" for supported requests.', '')
        if not preview and outcome in {'failed','rejected'} and not cross_corrected:
            self._previous_failed[memory_key]={'at':monotonic(),'outcome':outcome}
            while len(self._previous_failed)>64:
                del self._previous_failed[next(iter(self._previous_failed))]
        record = {
            'time':datetime.now(timezone.utc).isoformat(),
            'received_text':original_text,'resolved_text':resolved_text,'speaker_personalized':bool(voice_profile),'transcript_corrections':corrections,
            'device_id':getattr(user_input,'device_id',None),
            'satellite_id':getattr(user_input,'satellite_id',None),
            'area':area.name if area else None,'preview':preview,
            'steps':steps,'outcome':outcome,'error':failure,'followup_used':followup_used,
            'response':speech,'elapsed_ms':round((perf_counter()-start)*1000),
        }
        if self.hass.data.setdefault('jarvis_local',{}).get('debug_enabled',False):
            history=self.hass.data['jarvis_local'].setdefault('diagnostics',[])
            history.append(record)
            del history[:-20]
        observe_learning(self.hass, record)
        trackable = (outcome == 'completed' and not preview and not continue_conversation
                     and bool(steps) and all(step.get('kind') in {'light', 'switch_light', 'brightness', 'media_control', 'music', 'music_assistant_play', 'action', 'status', 'information'}
                                             and not step.get('unverified') and (step.get('kind')!='information' or step.get('available')) for step in steps))
        metadata={'trackable':trackable}
        if media_report is not None:
            metadata['media_search']=media_report
        result.async_set_speech(speech, extra_data={'jarvis_local': metadata})
        _LOGGER.debug('Declan local processing: %.0f ms', (perf_counter()-start)*1000)
        return conversation.ConversationResult(response=result, conversation_id=conversation_id, continue_conversation=continue_conversation)
