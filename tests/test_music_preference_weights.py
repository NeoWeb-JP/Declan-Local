"""Playlist preference selection and voice safety tests."""
import random
from types import SimpleNamespace
from music_fixtures import configure_music

import pytest
from custom_components.declan_local.music_variety import choose_playlist
from custom_components.declan_local.music_assistant_voice import plan_playlist_preference


def test_preferred_playlist_more_frequent():
    pool = {"rock": ["spotify:playlist:" + "A"*22, "spotify:playlist:" + "B"*22]}
    favourite = pool["rock"][0]
    rng = random.Random(42)
    selections = [choose_playlist("rock", pool, avoid_last=0, rng=rng,
                    weights={favourite: 5}) for _ in range(500)]
    assert selections.count(favourite) > 300


def test_recent_exclusion_still_applies():
    pool = {"rock": ["a", "b"]}
    assert choose_playlist("rock", pool, {"rock": ["a"]}, weights={"a": 5}) == "b"


def test_voice_requires_verified_playlist_uri():
    hass = configure_music(SimpleNamespace(states=SimpleNamespace(get=lambda entity:
        SimpleNamespace(state="playing", attributes={"media_title": "Song"}))))
    with pytest.raises(ValueError, match="cannot identify"):
        plan_playlist_preference(hass, "i love this playlist", SimpleNamespace(name="Kitchen"))


def test_voice_accepts_verified_playlist_uri():
    playlist = "spotify:playlist:" + "A"*22
    hass = configure_music(SimpleNamespace(states=SimpleNamespace(get=lambda entity:
        SimpleNamespace(state="playing", attributes={"playlist_uri": playlist}))))
    result = plan_playlist_preference(hass, "i like this playlist", SimpleNamespace(name="Kitchen"))
    assert result["playlist"] == playlist
    assert result["operation"] == "like"
