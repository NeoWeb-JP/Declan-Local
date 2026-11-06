"""Pure unit tests for local STT baseline metrics."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "stt_baseline", Path(__file__).resolve().parents[1] / "tools" / "stt_baseline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class STTBaselineTests(unittest.TestCase):
    def test_word_error_and_command_success_are_separate(self):
        results = module.evaluate([
            {"reference": "turn on fairy lights", "hypothesis": "turn on ferry lights",
             "room": "kitchen", "command_success": False},
            {"reference": "good night", "hypothesis": "good night",
             "room": "bedroom", "command_success": True},
        ])
        self.assertEqual(results["all"]["wer"], 0.1667)
        self.assertEqual(results["all"]["command_success_rate"], 0.5)
        self.assertEqual(results["room:kitchen"]["wer"], 0.25)
        self.assertEqual(results["room:bedroom"]["command_success_rate"], 1.0)

    def test_empty_reference_has_no_division_error(self):
        self.assertIsNone(module.evaluate([{"reference": "", "hypothesis": ""}])["all"]["wer"])

    def test_invalid_command_success_rejected(self):
        with self.assertRaises(ValueError):
            module.evaluate([{"reference": "hello", "hypothesis": "hello",
                              "command_success": "yes"}])


if __name__ == "__main__":
    unittest.main()
