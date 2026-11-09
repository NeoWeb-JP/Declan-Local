"""Choose one satellite for a near-simultaneous matching utterance."""
import asyncio
from array import array
from collections import defaultdict
from math import sqrt
from sys import byteorder
from time import monotonic

from .speaker_models import SpeakerTranscript


class CaptureLevel:
    """Measure RMS of the PCM samples already sent to Wyoming."""

    def __init__(self):
        self.energy = 0
        self.count = 0
        self.remainder = b""
        self.finished_at = None

    def add(self, chunk):
        pcm = self.remainder + chunk
        end = len(pcm) & ~1
        self.remainder = pcm[end:]
        samples = array("h", pcm[:end])
        if byteorder != "little":
            samples.byteswap()
        self.energy += sum(sample * sample for sample in samples)
        self.count += len(samples)

    @property
    def rms(self):
        return sqrt(self.energy / self.count) if self.count else 0


class SatellitePriority:
    """Arbitrate before conversation side effects, with a bounded wait."""

    wait_seconds = 0.35
    capture_tolerance = 0.4
    late_retention = 3.0

    def __init__(self):
        self.pending = defaultdict(list)
        self.recent = []

    async def allow(self, satellite, transcript):
        if not satellite or not isinstance(transcript, SpeakerTranscript):
            return True
        capture = transcript.capture_level
        if capture is None:
            return True
        captured_at, rms = capture
        key = " ".join(transcript.casefold().split()).rstrip(".!?").rstrip()
        if not key:
            return True

        now = monotonic()
        self.recent = [item for item in self.recent if now - item[0] < self.late_retention]
        for _, previous_key, previous_satellite, previous_capture in self.recent:
            if (key == previous_key and satellite != previous_satellite
                    and abs(captured_at - previous_capture) <= self.capture_tolerance):
                return False

        loop = asyncio.get_running_loop()
        decision = loop.create_future()
        for batch in self.pending[key]:
            if (abs(captured_at - batch[0][0]) <= self.capture_tolerance
                    and all(candidate[1] != satellite for candidate in batch)):
                break
        else:
            batch = []
            self.pending[key].append(batch)
            loop.call_later(self.wait_seconds, self._decide, key, batch)
        batch.append((captured_at, satellite, rms, decision))
        return await decision

    def _decide(self, key, batch):
        self.pending[key].remove(batch)
        if not self.pending[key]:
            del self.pending[key]
        active = [candidate for candidate in batch if not candidate[3].cancelled()]
        if not active:
            return
        captured_at, satellite, _, winner = max(active, key=lambda candidate: candidate[2])
        self.recent.append((monotonic(), key, satellite, captured_at))
        for _, _, _, decision in active:
            decision.set_result(decision is winner)
