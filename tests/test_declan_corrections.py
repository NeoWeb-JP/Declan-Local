"""Safety checks for in-utterance correction handling."""
import pytest
from custom_components.jarvis_local.corrections import final_request


def test_full_correction_supersedes_first_action():
    assert final_request("turn on kitchen lights, actually turn on kitchen spotlights") == ("turn on kitchen spotlights", True)


def test_target_only_correction_inherits_explicit_action():
    with pytest.raises(ValueError, match="full corrected command"):
        final_request("turn on kitchen lights, actually I meant the spotlights")


def test_preview_remains_preview_after_correction():
    assert final_request("preview turn on kitchen lights, actually turn off kitchen lights") == ("preview turn off kitchen lights", True)


def test_ambiguous_correction_does_not_execute():
    with pytest.raises(ValueError, match="full corrected command"):
        final_request("turn on kitchen lights, actually maybe the dining room")


def test_target_only_room_correction():
    assert final_request("turn off kitchen lights, actually the dining room") == ("turn off dining room lights", True)
