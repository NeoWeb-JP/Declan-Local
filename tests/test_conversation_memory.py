"""Conversation memory stays bounded to known speaker or conversation."""
from types import SimpleNamespace
from custom_components.jarvis_local.conversation_memory import context_key


def request(user=None, satellite="kitchen"):
    return SimpleNamespace(context=SimpleNamespace(user_id=user), satellite_id=satellite)


def test_identified_speaker_survives_new_conversation():
    assert context_key(request(), "first", "Jaco") == context_key(request(), "second", "Jaco")


def test_different_speakers_are_isolated():
    assert context_key(request(), "first", "Jaco") != context_key(request(), "second", "Edd")


def test_anonymous_satellite_does_not_share_across_conversations():
    assert context_key(request(), "first") != context_key(request(), "second")


def test_authenticated_user_survives_conversation_change():
    assert context_key(request("user1"), "first") == context_key(request("user1"), "second")
    assert context_key(request("user1"), "first") != context_key(request("user2"), "second")


def test_context_does_not_leak_between_satellites():
    assert context_key(request(satellite="kitchen"), "first", "Jaco") != context_key(request(satellite="bedroom"), "first", "Jaco")
