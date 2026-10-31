"""Unit tests for provider usage metrics. No user speech is retained."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "custom_components" / "jarvis_local" / "voice_usage.py"
spec = importlib.util.spec_from_file_location("voice_usage", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_usage_breakdown():
    usage = module.VoiceUsage()
    assert usage.snapshot()["preferred_voice_pct"] is None
    assert usage.snapshot()["cache_hit_pct"] is None
    for source in ("elevenlabs_cached", "elevenlabs_generated",
                   "elevenlabs_category_cached", "xtts_generated"):
        usage.record(source)
    result = usage.snapshot()
    assert result["total"] == 4
    assert result["preferred_voice_pct"] == 75.0
    assert result["counts"]["xtts_generated"] == 1
    assert result["cache_hit_pct"] == 50.0
    usage.record_failure('primary')
    usage.record_failure('fallback')
    assert usage.snapshot()['provider_failures'] == {'primary': 1, 'fallback': 1}
    assert usage.snapshot()['total'] == 4


def test_reject_unrecognised_source():
    usage = module.VoiceUsage()
    try:
        usage.record("untrusted")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid source accepted")
