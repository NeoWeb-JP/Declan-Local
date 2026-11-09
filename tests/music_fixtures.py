"""Explicit music destinations for fake Home Assistant instances."""
DESTINATIONS = {
    "kitchen": "media_player.kitchen_declan_voice_assistant",
    "bedroom": "media_player.bedroom_declan_voice_assistant",
    "lounge": "media_player.living_room_declan",
    "living room": "media_player.living_room_declan",
    "downstairs": "media_player.downstairs_2",
    "everywhere": "media_player.everywhere_2",
}


def configure_music(hass):
    if not hasattr(hass, "data"):
        hass.data = {}
    settings = hass.data.setdefault("declan_local", {}).setdefault("settings", {})
    settings["music_players"] = DESTINATIONS.copy()
    return hass
