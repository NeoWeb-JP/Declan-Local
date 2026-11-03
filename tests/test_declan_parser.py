"""Regression tests for Declan and legacy Jarvis invocation names."""
from custom_components.jarvis_local.parser import parse


def test_declan_wake_prefix():
    assert parse("Declan good morning") == ("jarvis_local_good_morning", {})
    assert parse("Hey Declan, good night") == ("jarvis_local_good_night", {})


def test_declan_suffix_and_legacy_name():
    assert parse("movie time Declan") == ("jarvis_local_movie", {"requested_action": "toggle"})
    assert parse("Jarvis good morning") == ("jarvis_local_good_morning", {})


def test_unknown_command_remains_rejected():
    assert parse("Declan do something unexpected") is None
