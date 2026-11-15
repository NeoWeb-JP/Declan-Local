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

def test_more_than_25_manual_pins_are_bounded():
    values = ["spotify://playlist/" + f"{i:022d}" for i in range(30)]
    result = curate({"braai": {"favourites": values}}, {"braai": []})
    assert result["braai"]["favourites"] == values[:25]
    assert result["braai"]["playlists"] == values[:25]


def test_manual_add_displaces_discovery_but_preserves_pins():
    values = ["spotify://playlist/" + f"{i:022d}" for i in range(25)]
    pinned = "spotify://playlist/" + "Z" * 22
    result = curate({"country": {"favourites": [pinned], "discovered": values}},
                    {"country": values})
    assert len(result["country"]["playlists"]) == 25
    assert result["country"]["playlists"][0] == pinned
    assert result["country"]["playlists"][-1] == values[23]


def test_deleted_playlist_is_excluded_on_refresh():
    result = curate({"rock": {"excluded": [A], "favourites": [B]}},
                    {"rock": [A, B, C]})
    assert result["rock"]["playlists"] == [B, C]
    assert result["rock"]["excluded"] == [A]
