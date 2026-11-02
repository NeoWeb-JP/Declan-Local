"""Bounded, safe follow-up parsing tests."""
from custom_components.jarvis_local.followup import followup, additional_room


def test_demonstrative_followups():
    assert followup("turn those off") == ("turn off __previous_lights__", False)
    assert followup("switch that on") == ("turn on __previous_lights__", False)
    assert followup("set these to 30 percent") == ("set __previous_lights__ to 30 percent", False)
    assert followup("dim the same lights") == ("dim __previous_lights__", False)


def test_no_unbounded_target_inference():
    assert followup("turn the lounge off") is None
    assert additional_room("and those", "turn_on") is None
    assert additional_room("and the dining room lights", "turn_on") == "turn on dining room lights"
