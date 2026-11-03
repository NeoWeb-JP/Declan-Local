"""Conservative Music Assistant voice playback planning."""
import re

ROOMS = {
    "kitchen": "media_player.kitchen_declan_voice_assistant",
    "bedroom": "media_player.bedroom_declan_voice_assistant",
    "living room": "media_player.living_room_declan",
    "lounge": "media_player.living_room_declan",
    "downstairs": "media_player.downstairs_2",
    "everywhere": "media_player.everywhere_2",
}

def plan_music(hass, text, area=None):
    """Plan explicit Music Assistant playback, resolving only known rooms."""
    request = text.strip().rstrip(".!?")
    request = re.sub(r"^(?:please\s+)?play\s+", "", request, flags=re.I)
    if request == text.strip().rstrip(".!?"):
        return None
    request = re.sub(r"^(?:some|me some)\s+", "", request, flags=re.I)
    room_names = sorted(ROOMS, key=len, reverse=True)
    room_pattern = "|".join(re.escape(name) for name in room_names)
    match = re.fullmatch(r"(.+?)\s+(?:(?:in|on|through)\s+(?:the\s+)?)?(" + room_pattern + r")", request, re.I)
    if match:
        query, room = match.groups()
        room = room.lower()
    else:
        query = request
        area_name = getattr(area, "name", "").lower().strip() if area is not None else ""
        room = {"master bedroom": "bedroom"}.get(area_name, area_name)
        if room not in ROOMS:
            raise ValueError("Which room should I play that in? Please name a room. Nothing was run.")
    query = query.strip()
    if not query or len(query) > 150:
        raise ValueError("Please name music to play. Nothing was run.")
    entity_id = ROOMS[room]
    player = hass.states.get(entity_id)
    if player is None or player.state in {"unavailable", "unknown"}:
        raise ValueError("The music player for " + room + " is unavailable. Nothing was run.")
    kind = "artist"
    artist = None
    if query.lower().endswith(" music") and query.lower()[:-6].strip() in {"country", "rock", "pop", "jazz", "classical", "blues", "dance", "folk", "reggae", "soul", "ambient", "electronic", "hip hop"}:
        kind = "playlist"
        query = query[:-6].strip()
    elif query.lower().startswith("the playlist "):
        kind = "playlist"
        query = query[13:].strip()
    elif query.lower().startswith("the song "):
        kind = "track"
        query = query[9:].strip()
    elif " by " in query.lower():
        parts = re.split(r"\s+by\s+", query, maxsplit=1, flags=re.I)
        query, artist = parts[0].strip(), parts[1].strip()
        kind = "track"
    if artist is None and " by " in query.lower():
        query, artist = [part.strip() for part in re.split(r"\s+by\s+", query, maxsplit=1, flags=re.I)]
        kind = "track"
    if not query or (artist is not None and not artist):
        raise ValueError("Please name music to play. Nothing was run.")
    data = {"media_id": query, "media_type": kind}
    if artist:
        data["artist"] = artist
    return {"kind": "music_assistant_play", "name": "play_media",
            "data": data, "entity_id": entity_id,
            "target_label": room.title(), "label": "play " + query + " in " + room}


def plan_stop_music(hass, text, area=None):
    """Stop a named Music Assistant player, or the current room's player."""
    match = re.fullmatch(
        r"(?:please )?(?:(?:stop|turn off)(?: the)? music|music off)"
        r"(?: (?:(?:in|on) (?:the )?)?(kitchen|bedroom|living room|lounge|downstairs|everywhere))?"
        r"(?: please)?[.!?]?", text.strip(), re.I
    )
    if not match:
        return None
    room = match.group(1)
    if not room:
        area_name = getattr(area, "name", "").lower().strip() if area is not None else ""
        aliases = {"master bedroom": "bedroom", "living room": "lounge"}
        room = aliases.get(area_name, area_name)
    if room not in ROOMS:
        raise ValueError("Which room should I stop the music in? Please name the room. Nothing was run.")
    entity_id = ROOMS[room]
    player = hass.states.get(entity_id)
    if player is None or player.state in {"unavailable", "unknown"}:
        raise ValueError("The music player for " + room + " is unavailable. Nothing was run.")
    return {
        "kind": "media_control", "name": "media_stop",
        "data": {"entity_id": entity_id}, "target_label": room.title(),
        "label": "stop music in " + room,
    }


def plan_music_transport(hass, text, area=None):
    """Plan standard media player transport controls, never claim playback verified."""
    match = re.fullmatch(
        r"(?:please )?(pause|resume|continue|skip|next|previous|restart)"
        r"(?: (?:the )?(?:music|song|track))?"
        r"(?: (?:(?:in|on) (?:the )?)?(kitchen|bedroom|living room|lounge|downstairs|everywhere))?"
        r"(?: please)?[.!?]?", text.strip(), re.I)
    if not match:
        return None
    action, room = match.groups()
    if not room:
        area_name = getattr(area, 'name', '').lower().strip() if area is not None else ''
        room = {'master bedroom': 'bedroom'}.get(area_name, area_name)
    room = room.lower()
    if room not in ROOMS:
        raise ValueError('Which room should I control the music in? Nothing was run.')
    entity_id = ROOMS[room]
    player = hass.states.get(entity_id)
    if player is None or player.state in {'unavailable', 'unknown'}:
        raise ValueError('The music player for '+room+' is unavailable. Nothing was run.')
    service = {'pause':'media_pause', 'resume':'media_play', 'continue':'media_play',
               'skip':'media_next_track', 'next':'media_next_track',
               'previous':'media_previous_track', 'restart':'media_previous_track'}[action.lower()]
    return {'kind':'media_control','name':service,'data':{'entity_id':entity_id},
            'target_label':room.title(),'label':action.lower()+' music in '+room}
