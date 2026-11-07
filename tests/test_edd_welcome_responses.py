"""Welcome-home catalogue regression tests (no HA runtime required)."""
import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parents[1] / "custom_components" / "declan_local" / "responses.json"


def test_edd_welcome_has_variety():
    responses = json.loads(CATALOG.read_text(encoding="utf-8"))
    lines = responses["Home"]["welcome_edd"]
    assert len(lines) >= 5
    assert len(set(lines)) == len(lines)
    assert all("Edd" in line or "EDD" in line for line in lines)


def test_edd_welcome_has_guest_safe_fallback():
    responses = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert responses["Guest"]["welcome_edd"]
    assert all("Jaco" not in line for line in responses["Guest"]["welcome_edd"])
