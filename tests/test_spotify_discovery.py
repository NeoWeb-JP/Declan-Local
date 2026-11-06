"""Spotify discovery catalogue tests."""
from custom_components.declan_local.spotify_discovery import QUERIES, curate, uri

A = "spotify://playlist/" + "A" * 22
B = "spotify://playlist/" + "B" * 22
C = "spotify://playlist/" + "C" * 22


def test_categories_include_household_preferences():
    assert {"country", "braai", "romantic", "sexy_time", "rock", "afrikaans",
            "80s", "90s", "work_focus", "adhd_focus", "massage"} <= set(QUERIES)


def test_favourites_survive_and_exclusions_win():
    old = {"country": {"favourites": [A, B], "excluded": [B]}}
    result = curate(old, {"country": [B, C]})
    assert result["country"]["favourites"] == [A]
    assert result["country"]["excluded"] == [B]
    assert result["country"]["playlists"] == [A, C]


def test_maximum_25_and_favourites_preserved():
    values = ["spotify://playlist/" + f"{i:022d}" for i in range(30)]
    result = curate({"rock": {"favourites": values[:3]}}, {"rock": values})
    assert len(result["rock"]["playlists"]) == 25
    assert result["rock"]["playlists"][:3] == values[:3]


def test_uri_rejects_untrusted_urls():
    assert uri("https://evil.example/playlist/" + "A" * 22) is None
    assert uri("spotify:playlist:" + "A" * 22) == A
