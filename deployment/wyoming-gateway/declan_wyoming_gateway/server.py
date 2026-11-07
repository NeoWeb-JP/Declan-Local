"""Test-only Wyoming proxy: faster-whisper at 10300, speaker gateway at 10301."""
from __future__ import annotations

import argparse
import asyncio
import logging
import math
import uuid

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.asr import Transcribe, Transcript
from wyoming.client import AsyncTcpClient
from wyoming.error import Error
from wyoming.event import Event
from wyoming.info import Describe
from wyoming.server import AsyncEventHandler, AsyncServer

from .speakers import SpeakerStore, WeSpeakerEmbedder

LOG = logging.getLogger(__name__)
MAX_PCM = 16000 * 2 * 60  # max 60 seconds of PCM16


async def forward_audio(host: str, port: int, audio: bytes,
                        *, language: str = "en", timeout: float = 90) -> str:
    async def request() -> str:
        async with AsyncTcpClient(host, port) as client:
            await client.write_event(Transcribe(language=language).event())
            await client.write_event(AudioStart(rate=16000, width=2, channels=1).event())
            for i in range(0, len(audio), 32000):
                await client.write_event(AudioChunk(
                    rate=16000, width=2, channels=1, audio=audio[i:i + 32000]
                ).event())
            await client.write_event(AudioStop().event())
            while event := await client.read_event():
                if Transcript.is_type(event.type):
                    return Transcript.from_event(event).text
                if Error.is_type(event.type):
                    raise RuntimeError("Upstream Whisper error")
            raise RuntimeError("Whisper closed without a transcript")
    return await asyncio.wait_for(request(), timeout)


async def process_utterance(pcm: bytes, store: SpeakerStore, host: str,
                            port: int, *, language: str = "en") -> list[Event]:
    """Speaker event MUST precede Transcript; no embedded speaker prefix."""
    transcript = await forward_audio(host, port, pcm, language=language)
    try:
        speaker, confidence = await asyncio.wait_for(
            asyncio.to_thread(store.identify, pcm), timeout=12
        )
        if (speaker not in {"Jaco", "Edd"}
            or isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not math.isfinite(confidence)
            or not 0 <= confidence <= 1):
            speaker, confidence = "Unknown", 0.0
    except Exception:
        LOG.exception("Speaker recognition failed; retaining transcript")
        speaker, confidence = "Unknown", 0.0
    return [
        Event(type="jarvis-speaker", data={
            "speaker": speaker,
            "confidence": float(confidence),
            "interaction_id": str(uuid.uuid4()),
        }),
        Transcript(text=transcript).event(),
    ]


class GatewayHandler(AsyncEventHandler):
    def __init__(self, reader, writer, *, store: SpeakerStore,
                 upstream_host: str, upstream_port: int, **kwargs):
        super().__init__(reader, writer, **kwargs)
        self.store = store
        self.host = upstream_host
        self.port = upstream_port
        self.audio = bytearray()
        self.language = "en"
        self.valid_audio = False

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            try:
                async with AsyncTcpClient(self.host, self.port) as client:
                    await client.write_event(event)
                    response = await asyncio.wait_for(client.read_event(), 10)
                    if response:
                        await self.write_event(response)
            except Exception:
                LOG.exception("Upstream Wyoming Describe unavailable")
            return True
        if Transcribe.is_type(event.type):
            self.language = Transcribe.from_event(event).language or "en"
            return True
        if AudioStart.is_type(event.type):
            start = AudioStart.from_event(event)
            self.valid_audio = (start.rate, start.width, start.channels) == (16000, 2, 1)
            self.audio.clear()
            return True
        if AudioChunk.is_type(event.type):
            if self.valid_audio:
                chunk = AudioChunk.from_event(event)
                self.valid_audio = (
                    chunk.rate, chunk.width, chunk.channels
                ) == (16000, 2, 1)
                if len(self.audio) + len(chunk.audio) > MAX_PCM:
                    self.valid_audio = False
                else:
                    self.audio.extend(chunk.audio)
            return True
        if AudioStop.is_type(event.type):
            if not self.valid_audio or not self.audio:
                await self.write_event(
                    Error(text="Expected nonempty 16-kHz mono PCM16 audio").event()
                )
                return False
            try:
                events = await process_utterance(
                    bytes(self.audio), self.store, self.host, self.port,
                    language=self.language
                )
                for response in events:
                    await self.write_event(response)
            except Exception:
                LOG.exception("Upstream transcription unavailable")
                await self.write_event(Error(text="Transcription unavailable").event())
            finally:
                self.audio.clear()
            return False
        return True


async def serve(args) -> None:
    embedder = None
    if args.model:
        try:
            embedder = WeSpeakerEmbedder(args.model)
        except Exception:
            LOG.exception("Speaker model unavailable: Unknown fallback enabled")
    store = SpeakerStore(args.profiles, embedder, threshold=args.threshold,
                         margin=args.margin)
    server = AsyncServer.from_uri(f"tcp://{args.listen_host}:{args.listen_port}")
    LOG.info("Declan test gateway %s:%d -> %s:%d",
             args.listen_host, args.listen_port,
             args.upstream_host, args.upstream_port)
    await server.run(lambda reader, writer: GatewayHandler(
        reader, writer, store=store,
        upstream_host=args.upstream_host, upstream_port=args.upstream_port
    ))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=10301)
    parser.add_argument("--upstream-host", default="127.0.0.1")
    parser.add_argument("--upstream-port", type=int, default=10300)
    parser.add_argument("--profiles", default="/opt/declan-stt/speakers.json")
    parser.add_argument("--model", default="", help="Local WeSpeaker ONNX model")
    parser.add_argument("--threshold", type=float, default=.75)
    parser.add_argument("--margin", type=float, default=.08)
    args = parser.parse_args()
    if args.listen_host == args.upstream_host and args.listen_port == args.upstream_port:
        parser.error("Gateway cannot forward to itself")
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve(args))


if __name__ == "__main__":
    main()
