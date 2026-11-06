"""Bounded, safe follow-up parsing tests."""
from custom_components.declan_local.followup import followup, additional_room


def test_demonstrative_followups():
    assert followup("turn those off") == ("turn off __previous_lights__", False)
    assert followup("switch that on") == ("turn on __previous_lights__", False)
    assert followup("set these to 30 percent") == ("set __previous_lights__ to 30 percent", False)
    assert followup("dim the same lights") == ("dim __previous_lights__", False)


def test_no_unbounded_target_inference():
    assert followup("turn the lounge off") is None
    assert additional_room("and those", "turn_on") is None
    assert additional_room("and the dining room lights", "turn_on") == "turn on dining room lights"


def test_natural_brightness_followups():
    assert followup("make those lights 40 percent") == ("set __previous_lights__ to 40 percent", False)
    assert followup("put these at 25%") == ("set __previous_lights__ to 25 percent", False)
    assert followup("adjust that light to 60 percent") == ("set __previous_lights__ to 60 percent", False)
    assert followup("preview make them 35 percent") == ("set __previous_lights__ to 35 percent", True)
    assert followup("make the lounge 40 percent") is None
