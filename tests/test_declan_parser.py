"""Household phrases must not resolve to source-coded routines."""
import pytest
from test_commands import Hass
from jarvis_test.planner import plan


@pytest.mark.parametrize("phrase", [
    "Declan good morning", "Hey Declan, good night", "movie time Declan",
    "Jarvis good morning", "dinner time", "start sexy time",
])
def test_household_phrases_are_not_local_actions(phrase):
    with pytest.raises(ValueError, match="did not understand"):
        plan(Hass(), phrase)
