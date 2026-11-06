"""Timer STT regression: exact duration-bearing mishearing only."""
from custom_components.declan_local.timers import parse

def test_time_off_timer_stt():
    assert parse('Set me a time off for 15 minutes.') == {
        'operation': 'set', 'seconds': 900, 'preview': False}
    assert parse('Preview set me a time off for 15 minutes')['preview'] is True

def test_time_off_does_not_capture_unrelated_speech():
    assert parse('I need some time off for 15 minutes') is None
    assert parse('set me a time off') is None
