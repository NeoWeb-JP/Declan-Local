"""Regression checks for the integrated Wyoming speaker bridge."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "declan_local"


def test_integrated_speaker_model_and_bridge_exist():
    model = ast.parse((ROOT / "speaker_models.py").read_text())
    assert any(isinstance(n, ast.ClassDef) and n.name == "SpeakerTranscript" for n in model.body)
    bridge = ast.parse((ROOT / "wyoming_speaker_stt.py").read_text())
    assert any(isinstance(n, ast.ClassDef) and n.name == "DeclanWyomingVoiceBridge" for n in bridge.body)


def test_identity_uses_integrated_model():
    source = (ROOT / "speaker_identity.py").read_text()
    assert "from .speaker_models import SpeakerTranscript" in source
    assert "custom_components.jarvis_voice_bridge" not in source


def test_bridge_is_opt_in_and_retains_original_event():
    source = (ROOT / "stt.py").read_text()
    assert 'entry.options.get("wyoming_bridge_enabled")' in source
    bridge = (ROOT / "wyoming_speaker_stt.py").read_text()
    assert "jarvis-speaker" in bridge
    assert "SpeakerTranscript" in bridge
