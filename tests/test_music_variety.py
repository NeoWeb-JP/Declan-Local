"""Tests for Declan playlist selection."""
import random
import pytest

from custom_components.declan_local.music_variety import choose_playlist, updated_history


def test_avoids_recent_playlists():
    pool = {"country": ["one", "two", "three", "four"]}
    assert choose_playlist("country", pool, {"country": ["one", "two", "three"]}) == "four"


def test_relaxes_exclusion_when_pool_is_small():
    pool = {"romantic": ["one", "two"]}
    assert choose_playlist("romantic", pool, {"romantic": ["one", "two"]}, rng=random.Random(1)) in pool["romantic"]


def test_deduplicates_and_ignores_blank_entries():
    assert choose_playlist("country", {"country": ["a", "a", "", " "]}) == "a"


def test_missing_category_fails_clearly():
    with pytest.raises(ValueError, match="No playlists"):
        choose_playlist("unknown", {})


def test_history_is_immutable_and_bounded():
    original = {"country": ["a", "b"]}
    updated = updated_history("country", "c", original, max_entries=2)
    assert original["country"] == ["a", "b"]
    assert updated["country"] == ["b", "c"]


def test_invalid_limits_rejected():
    with pytest.raises(ValueError):
        choose_playlist("country", {"country": ["a"]}, avoid_last=-1)
    with pytest.raises(ValueError):
        updated_history("country", "a", max_entries=0)
