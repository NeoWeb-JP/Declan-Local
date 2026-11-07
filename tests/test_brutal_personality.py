"""Brutal Home personality must not leak into Guest responses."""
from collections import deque
from types import SimpleNamespace
from custom_components.declan_local.personality import BRUTAL_LINES, NUCLEAR_LINES, choose


def test_brutal_catalogue_covers_routine_actions():
    for action in ("general", "on", "off", "brightness", "music",
                   "self_correction", "clarification", "morning", "bedtime", "movie"):
        assert len(BRUTAL_LINES[action]) >= 4


def test_guest_never_receives_brutal_lines():
    hass = SimpleNamespace(data={})
    catalog = {"Home": {"on": ["Home reply"]}, "Guest": {"on": ["Guest reply"]}}
    for _ in range(12):
        assert choose(hass, "Guest", "on", catalog) == "Guest reply"


def test_home_includes_brutal_pool():
    hass = SimpleNamespace(data={})
    catalog = {"Home": {"on": []}, "Guest": {"on": []}}
    assert choose(hass, "Home", "on", catalog) in BRUTAL_LINES["on"]


def test_nuclear_lines_are_available_for_home():
    hass = SimpleNamespace(data={})
    catalog = {"Home": {"general": []}, "Guest": {"general": []}}
    seen = {choose(hass, "Home", "general", catalog) for _ in range(100)}
    assert seen.intersection(NUCLEAR_LINES["general"])


def test_nuclear_lines_are_never_selected_for_guest():
    hass = SimpleNamespace(data={})
    catalog = {"Home": {"general": []}, "Guest": {"general": ["Certainly."]}}
    assert {choose(hass, "Guest", "general", catalog) for _ in range(30)} == {"Certainly."}


def test_savage_default_morning_greeting():
    from custom_components.declan_local.morning import morning_reply
    assert any(word in morning_reply("Jaco", {}, {}) for word in ("Jaco",))


def test_custom_morning_profile_is_respected():
    from custom_components.declan_local.morning import morning_reply
    profiles = {"one": {"name": "Edd", "morning_responses": ["Good morning, {name}."]}}
    assert morning_reply("Edd", profiles, {}) == "Good morning, Edd."
