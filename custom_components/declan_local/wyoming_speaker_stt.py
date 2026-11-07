"""Integrated Wyoming speaker-aware speech recognition, adapted from Jarvis-Voice-Bridge.

Requires a Wyoming speech service emitting jarvis-speaker before Transcript.
"""
import asyncio
import logging
import math
from collections.abc import AsyncIterable
from homeassistant.components import stt
from wyoming.client import AsyncTcpClient
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioStart, AudioChunk, AudioStop
from wyoming.error import Error
from .speaker_models import SpeakerTranscript
_LOGGER=logging.getLogger(__name__)

async def upload(client,stream):
    async for data in stream:
        await client.write_event(AudioChunk(rate=16000,width=2,channels=1,audio=data).event())
    await client.write_event(AudioStop().event())

async def receive(client):
    identity = None
    speaker_event_seen = False
    speaker_event_valid = False
    speaker_unknown = False
    while event := await client.read_event():
        if event.type == 'jarvis-speaker':
            speaker_event_seen = True
            value = event.data if isinstance(event.data, dict) else {}
            name = value.get('speaker')
            confidence = value.get('confidence')
            identity_id = value.get('interaction_id')
            speaker_unknown = isinstance(name, str) and name.casefold() in ('unknown', 'unidentified', 'none')
            speaker_event_valid = (
                isinstance(name, str) and bool(name) and len(name) <= 80
                and isinstance(identity_id, str) and len(identity_id) <= 80
                and isinstance(confidence, (int, float)) and not isinstance(confidence, bool)
                and math.isfinite(confidence) and 0 <= confidence <= 1
            )
            if speaker_event_valid:
                identity = (identity_id, name, confidence)
            _LOGGER.info(
                "DECLAN_WYOMING_SPEAKER event=received valid=%s unknown=%s",
                speaker_event_valid, speaker_unknown,
            )
        elif Transcript.is_type(event.type):
            _LOGGER.info(
                "DECLAN_WYOMING_SPEAKER event=transcript speaker_event_seen=%s "
                "identity_attached=%s ordering=%s",
                speaker_event_seen, identity is not None,
                'speaker_before_transcript' if speaker_event_seen else 'transcript_before_speaker',
            )
            return stt.SpeechResult(
                SpeakerTranscript(Transcript.from_event(event).text, identity),
                stt.SpeechResultState.SUCCESS,
            )
        elif Error.is_type(event.type):
            _LOGGER.info(
                "DECLAN_WYOMING_SPEAKER event=error speaker_event_seen=%s",
                speaker_event_seen,
            )
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
    _LOGGER.info(
        "DECLAN_WYOMING_SPEAKER event=stream_closed speaker_event_seen=%s",
        speaker_event_seen,
    )
    return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

class DeclanWyomingVoiceBridge(stt.SpeechToTextEntity):
    _attr_name='Declan Wyoming Speaker Recognition'
    def __init__(self,entry):
        self.host=entry.options['wyoming_bridge_host'];self.port=entry.options['wyoming_bridge_port'];self._attr_unique_id='declan_wyoming_speaker_stt'
    @property
    def supported_languages(self):return ['en']
    @property
    def supported_formats(self):return [stt.AudioFormats.WAV]
    @property
    def supported_codecs(self):return [stt.AudioCodecs.PCM]
    @property
    def supported_bit_rates(self):return [stt.AudioBitRates.BITRATE_16]
    @property
    def supported_sample_rates(self):return [stt.AudioSampleRates.SAMPLERATE_16000]
    @property
    def supported_channels(self):return [stt.AudioChannels.CHANNEL_MONO]
    async def async_process_audio_stream(self,metadata,stream:AsyncIterable[bytes]):
        try:
            async with AsyncTcpClient(self.host,self.port) as client:
                await client.write_event(Transcribe(language=metadata.language).event())
                await client.write_event(AudioStart(rate=16000,width=2,channels=1).event())
                upload_task=asyncio.create_task(upload(client,stream))
                receive_task=asyncio.create_task(receive(client))
                try:
                    done,_=await asyncio.wait((upload_task,receive_task),return_when=asyncio.FIRST_COMPLETED)
                    if receive_task in done:return receive_task.result()
                    upload_task.result()
                    return await receive_task
                finally:
                    for task in (upload_task,receive_task):
                        if not task.done():task.cancel()
                    await asyncio.gather(upload_task,receive_task,return_exceptions=True)
        except (OSError,TimeoutError):
            _LOGGER.exception('Voice bridge could not reach speech service')
            return stt.SpeechResult(None,stt.SpeechResultState.ERROR)
