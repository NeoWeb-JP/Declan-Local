"""Artist and category music request parsing with a lightweight HA state stub."""
from types import SimpleNamespace
from custom_components.jarvis_local.music_assistant_voice import plan_music


class States:
    def get(self, entity):
        return SimpleNamespace(state="idle", attributes={})


def test_artist_playback():
    result = plan_music(SimpleNamespace(states=States()), "play Dolly Parton everywhere")
    assert result["kind"] == "music_assistant_play"
    assert result["data"] == {"media_id": "Dolly Parton", "media_type": "artist"}


def test_artist_mix():
    result = plan_music(SimpleNamespace(states=States()), "play a Norah Jones mix everywhere")
    assert result["data"] == {"media_id": "Norah Jones", "media_type": "playlist"}


def test_song_by_artist():
    result = plan_music(SimpleNamespace(states=States()), "play Jolene by Dolly Parton everywhere")
    assert result["data"] == {"media_id": "Jolene", "media_type": "track", "artist": "Dolly Parton"}


def test_all_new_categories_route_to_discovery():
    for phrase, category in [("80s music", "80s"), ("90s music", "90s"),
                             ("work focus music", "work_focus"),
                             ("ADHD focus music", "adhd_focus"),
                             ("massage music", "massage"),
                             ("Afrikaans music", "afrikaans")]:
        result = plan_music(SimpleNamespace(states=States()), "play " + phrase + " everywhere")
        assert result["kind"] == "music_category"
        assert result["category"] == category
