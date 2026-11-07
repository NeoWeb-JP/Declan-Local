"""Catch literal backslash-n syntax regressions in the Wyoming bridge."""
import ast
from pathlib import Path


def test_wyoming_bridge_parses_as_python():
    path = Path(__file__).resolve().parents[1] / "custom_components" / "declan_local" / "wyoming_speaker_stt.py"
    source = path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(path))
    assert source.startswith('"""Integrated Wyoming speaker-aware speech recognition, adapted from Jarvis-Voice-Bridge.\n')
