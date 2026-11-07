"""Gateway protocol and enrolment tests, using the real Wyoming event classes."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from wyoming.asr import Transcript

from declan_wyoming_gateway.server import process_utterance
from declan_wyoming_gateway.speakers import SpeakerStore


class FakeEmbedder:
    def embed(self, pcm):
        return {b"a": [1., 0.], b"b": [0., 1.], b"c": [-1., 0.]}.get(pcm, [.71, .71])


class SpeakerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = SpeakerStore(str(Path(self.tmp.name) / "profiles.json"),
                                  FakeEmbedder(), threshold=.75, margin=.08)

    def test_unknown_until_enrolled(self):
        self.assertEqual(self.store.identify(b"a"), ("Unknown", 0.))

    def test_enrol_identify_and_reload(self):
        self.store.enrol("Jaco", [b"a"] * 3)
        self.store.enrol("Edd", [b"b"] * 3)
        self.assertEqual(self.store.identify(b"a")[0], "Jaco")
        self.assertEqual(self.store.identify(b"b")[0], "Edd")
        self.assertEqual(self.store.identify(b"c"), ("Unknown", 0.))
        reloaded = SpeakerStore(str(Path(self.tmp.name) / "profiles.json"), FakeEmbedder())
        self.assertEqual(reloaded.identify(b"b")[0], "Edd")

    def test_reject_unsupported_names_or_insufficient_samples(self):
        with self.assertRaises(ValueError):
            self.store.enrol("Guest", [b"a"] * 3)
        with self.assertRaises(ValueError):
            self.store.enrol("Jaco", [b"a"])


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_metadata_before_transcript(self):
        store = SpeakerTests()
        store.setUp()
        self.addCleanup(store.doCleanups)
        store.store.enrol("Jaco", [b"a"] * 3)
        with patch("declan_wyoming_gateway.server.forward_audio",
                   new=AsyncMock(return_value="Good morning")):
            events = await process_utterance(b"a", store.store, "localhost", 10300)
        self.assertEqual([event.type for event in events], ["jarvis-speaker", "transcript"])
        self.assertEqual(events[0].data["speaker"], "Jaco")
        self.assertTrue(events[0].data["interaction_id"])
        self.assertEqual(Transcript.from_event(events[1]).text, "Good morning")

    async def test_unknown_preserves_transcript(self):
        class Unavailable:
            def identify(self, pcm):
                raise RuntimeError("model offline")
        with patch("declan_wyoming_gateway.server.forward_audio",
                   new=AsyncMock(return_value="Lights on")):
            events = await process_utterance(b"a", Unavailable(), "localhost", 10300)
        self.assertEqual(events[0].data["speaker"], "Unknown")
        self.assertEqual(events[0].data["confidence"], 0.)
        self.assertEqual(Transcript.from_event(events[1]).text, "Lights on")

    async def test_concurrent_utterances_keep_separate_ids(self):
        store = SpeakerTests()
        store.setUp()
        self.addCleanup(store.doCleanups)
        store.store.enrol("Jaco", [b"a"] * 3)
        store.store.enrol("Edd", [b"b"] * 3)
        with patch("declan_wyoming_gateway.server.forward_audio",
                   new=AsyncMock(return_value="Hello")):
            a, b = await asyncio.gather(*(
                process_utterance(pcm, store.store, "localhost", 10300)
                for pcm in (b"a", b"b")
            ))
        self.assertEqual([a[0].data["speaker"], b[0].data["speaker"]], ["Jaco", "Edd"])
        self.assertNotEqual(a[0].data["interaction_id"], b[0].data["interaction_id"])


if __name__ == "__main__":
    unittest.main()
