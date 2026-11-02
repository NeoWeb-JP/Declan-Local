"""Conservative Music Assistant voice playback planning."""
import re

ROOMS = {
    "kitchen": "media_player.kitchen_declan_voice_assistant_speaker",
    "bedroom": "media_player.master_bedroom_echo_show_4",
    "living room": "media_player.living_room_declan",
    "lounge": "media_player.living_room_declan",
    "everywhere": "media_player.everywhere_2",
}

def plan_music(hass, text):
    match = re.fullmatch(r"play (.+?) (?:in|on) (?:the )?(kitchen|bedroom|living room|lounge|everywhere)", text, re.I)
    if not match:
        return None
    query, room = match.groups()
    query = query.strip()
    if not query or len(query) > 150:
        raise ValueError("Please name music to play. Nothing was run.")
    entity_id = ROOMS[room.lower()]
    player = hass.states.get(entity_id)
    if player is None or player.state in {"unavailable", "unknown"}:
        raise ValueError("The music player for " + room + " is unavailable. Nothing was run.")
    kind = "artist"
    artist = None
    if query.lower().startswith("the playlist "):
        kind = "playlist"
        query = query[13:].strip()
    elif query.lower().startswith("the song "):
        kind = "track"
        query = query[9:].strip()
    elif " by " in query.lower():
        parts = re.split(r"\s+by\s+", query, maxsplit=1, flags=re.I)
        query, artist = parts[0].strip(), parts[1].strip()
        kind = "track"
    if not query or (artist is not None and not artist):
        raise ValueError("Please name music to play. Nothing was run.")
    data = {"media_id": query, "media_type": kind}
    if artist:
        data["artist"] = artist
    return {"kind": "music_assistant_play", "name": "play_media",
            "data": data, "entity_id": entity_id,
            "target_label": room.title(), "label": "play " + query + " in " + room}
