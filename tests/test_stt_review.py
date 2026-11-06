"""Consent and review gates for offline STT examples."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("stt_review", Path(__file__).resolve().parents[1] / "tools" / "stt_review.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReviewTests(unittest.TestCase):
    def test_only_consented_reviewed_records_export(self):
        records = [
            {"reference": "fairy lights", "hypothesis": "ferry lights", "reviewed": True, "consent": True, "room": "kitchen"},
            {"reference": "secret", "hypothesis": "secret", "reviewed": False, "consent": True},
            {"reference": "private", "hypothesis": "private", "reviewed": True, "consent": False},
        ]
        self.assertEqual(module.approved(records), [{"reference": "fairy lights", "hypothesis": "ferry lights", "room": "kitchen"}])

    def test_rejects_invalid_records(self):
        with self.assertRaises(ValueError):
            module.approved([{"reference": "hi", "hypothesis": "hi", "reviewed": True}])
        with self.assertRaises(ValueError):
            module.approved([{"reference": "hi", "hypothesis": "hi", "reviewed": True, "consent": True, "command_success": "yes"}])


if __name__ == "__main__":
    unittest.main()
