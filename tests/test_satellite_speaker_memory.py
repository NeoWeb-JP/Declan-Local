"""Regression tests for conversation-only speaker continuity."""
import unittest
import test_commands  # registers lightweight jarvis_test package
from jarvis_test.speaker_identity import SatelliteSpeakerMemory
from jarvis_test.speaker_models import SpeakerTranscript

PROFILES = {'jaco': {'name': 'Jaco', 'min_confidence': 0.5},
            'edd': {'name': 'Ed', 'min_confidence': 0.5}}

def utterance(text, speaker=None, confidence=0):
    identity = ('interaction', speaker, confidence) if speaker is not None else None
    return SpeakerTranscript(text, identity)

class SatelliteMemoryTests(unittest.TestCase):
    def setUp(self):
        self.memory = SatelliteSpeakerMemory()

    def test_anchor_and_unknown_short_followup(self):
        self.assertEqual(self.memory.resolve(utterance('good morning', 'jaco', .8), 'kitchen', PROFILES, 100), 'Jaco')
        self.assertEqual(self.memory.resolve(utterance('yes'), 'kitchen', PROFILES, 105), 'Jaco')

    def test_expiry_and_different_satellite(self):
        self.memory.resolve(utterance('hello', 'jaco', .8), 'kitchen', PROFILES, 100)
        self.assertIsNone(self.memory.resolve(utterance('yes'), 'bedroom', PROFILES, 101))
        self.assertIsNone(self.memory.resolve(utterance('yes'), 'kitchen', PROFILES, 130))

    def test_conflicting_weak_identity_clears_context(self):
        self.memory.resolve(utterance('hello', 'jaco', .8), 'kitchen', PROFILES, 100)
        self.assertIsNone(self.memory.resolve(utterance('yes', 'edd', .3), 'kitchen', PROFILES, 101))
        self.assertIsNone(self.memory.resolve(utterance('yes'), 'kitchen', PROFILES, 102))

    def test_strong_new_speaker_replaces_previous(self):
        self.memory.resolve(utterance('hello', 'jaco', .8), 'kitchen', PROFILES, 100)
        self.assertEqual(self.memory.resolve(utterance('hello', 'edd', .9), 'kitchen', PROFILES, 101), 'Ed')
        self.assertEqual(self.memory.resolve(utterance('yes'), 'kitchen', PROFILES, 102), 'Ed')

    def test_weak_match_does_not_anchor(self):
        self.assertEqual(self.memory.resolve(utterance('hello', 'jaco', .55), 'kitchen', PROFILES, 100), 'Jaco')
        self.assertIsNone(self.memory.resolve(utterance('yes'), 'kitchen', PROFILES, 101))

    def test_no_satellite_or_plain_text_never_inherits(self):
        self.memory.resolve(utterance('hello', 'jaco', .8), 'kitchen', PROFILES, 100)
        self.assertIsNone(self.memory.resolve(utterance('yes'), None, PROFILES, 101))
        self.assertIsNone(self.memory.resolve('yes', 'kitchen', PROFILES, 101))

    def test_long_utterance_does_not_inherit(self):
        self.memory.resolve(utterance('hello', 'jaco', .8), 'kitchen', PROFILES, 100)
        self.assertIsNone(self.memory.resolve(utterance('please give me a complete home status report'), 'kitchen', PROFILES, 101))


    def test_diagnostic_reports_direct_memory_and_unknown(self):
        records = []
        callback = lambda profile, source, confidence: records.append((profile, source, confidence))
        self.memory.resolve(utterance('hello', 'jaco', .8), 'kitchen', PROFILES, 100, diagnostic=callback)
        self.memory.resolve(utterance('yes'), 'kitchen', PROFILES, 101, diagnostic=callback)
        self.memory.resolve(utterance('yes'), 'bedroom', PROFILES, 102, diagnostic=callback)
        self.assertEqual(records, [('Jaco', 'direct', .8), ('Jaco', 'memory', None), (None, 'unknown', None)])

    def test_diagnostic_conflict_does_not_leak_previous_identity(self):
        records = []
        callback = lambda profile, source, confidence: records.append((profile, source, confidence))
        self.memory.resolve(utterance('hello', 'jaco', .8), 'kitchen', PROFILES, 100, diagnostic=callback)
        self.memory.resolve(utterance('yes', 'edd', .3), 'kitchen', PROFILES, 101, diagnostic=callback)
        self.assertEqual(records[-1], (None, 'unknown', .3))

if __name__ == '__main__':
    unittest.main()
