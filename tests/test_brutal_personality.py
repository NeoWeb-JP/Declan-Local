"""Brutal Home personality must not leak into Guest responses."""
from collections import deque
from types import SimpleNamespace
from custom_components.declan_local.personality import BRUTAL_LINES, choose


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
