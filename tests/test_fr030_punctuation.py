"""FR-030 punctuation equivalence and literal preservation."""
import pytest

from custom_components.declan_local.understanding import normalize_punctuation, normalize_request


@pytest.mark.parametrize(("spoken", "plain"), [
    ("Play, country music.", "Play country music"),
    ("Turn, off. the kitchen lights?", "Turn off the kitchen lights"),
    ("Start, movie time!", "Start movie time"),
    ("Please, don't turn off the kitchen lights.", "don't turn off the kitchen lights"),
    ('Play, "Hello, Goodbye".', 'Play "Hello, Goodbye"'),
    ("Set, light.kitchen to 12.5 percent.", "Set light.kitchen to 12.5 percent"),
])
def test_transcription_punctuation(spoken, plain):
    assert normalize_request(spoken)[0] == plain


@pytest.mark.parametrize("text", [
    'run scene with {"name": "Hello, Goodbye"}',
    "turn off kitchen; turn on lounge",
    "play https://example.com/media?q=one,two",
])
def test_structured_text_is_preserved(text):
    assert normalize_punctuation(text) == text
