"""Check Home Assistant reported state after a lighting command."""
import asyncio

def pending(hass, domain, action, data):
    missing=[]
    for entity in data['entity_id']:
        state=hass.states.get(entity)
        wanted='off' if action=='turn_off' else 'on'
        if state is None or state.state!=wanted:
            missing.append(entity);continue
        if 'brightness' in data:
            value=state.attributes.get('brightness')
            if not isinstance(value,(int,float)) or abs(value-data['brightness'])>2:
                missing.append(entity);continue
        if 'brightness_pct' in data:
            value=state.attributes.get('brightness')
            if not isinstance(value,(int,float)) or abs(value/255*100-data['brightness_pct'])>4:
                missing.append(entity)
    return missing

async def verify(hass, domain, action, data):
    # Reported state may be optimistic; this is not physical verification.
    for delay in (0.05, 0.05, 0.1, 0.2, 0.2, 0.2, 0.2):
        remaining=pending(hass,domain,action,data)
        if not remaining:return []
        await asyncio.sleep(delay)
    return pending(hass,domain,action,data)


def _playing_playlist(state, requested):
    if state is None or state.state != "playing":
        return False
    attributes = state.attributes
    identities = [
        attributes.get("media_playlist"),
        attributes.get("media_playlist_uri"),
        attributes.get("playlist_uri"),
    ]
    if attributes.get("media_content_type") == "playlist":
        identities.append(attributes.get("media_content_id"))
    return any(
        isinstance(identity, str) and identity.strip().casefold() == requested
        for identity in identities
    )


async def play_verified_playlist(hass, entity_id, data, context):
    """Dispatch once and verify the requested playlist on the mapped player."""
    from homeassistant.exceptions import HomeAssistantError

    requested = data["media_id"].strip().casefold()
    already_playing = _playing_playlist(hass.states.get(entity_id), requested)
    try:
        await asyncio.wait_for(
            hass.services.async_call(
                "music_assistant", "play_media", data,
                target={"entity_id": entity_id}, blocking=True, context=context,
            ),
            timeout=3,
        )
    except TimeoutError:
        return "dispatch_unknown"
    except HomeAssistantError:
        return "failed"

    for attempt in range(9):
        matches = _playing_playlist(hass.states.get(entity_id), requested)
        # A repeated request for the same reported playlist is still a valid
        # playing state. Do not require an artificial stop/start transition.
        if matches:
            return "playing"
        if attempt < 8:
            await asyncio.sleep(0.25)
    return "unverified"


def movie_result(reply):
    """Interpret Movie Time results without speaking untrusted script text."""
    if not isinstance(reply, dict):
        reply = {}
    action = {"movie_start": "movie", "movie_end": "movie_end"}.get(
        str(reply.get("response_context")),
    )
    status = reply.get("status", "success" if action else "unknown")
    if status == "success" and action:
        speech = "Movie Time started." if action == "movie" else "Movie Time ended."
        return "success", action, speech
    if status == "partial":
        return "partial", None, "Movie Time only partly completed. Check the affected devices."
    if status == "failed":
        return "failed", None, "Movie Time failed. Check the devices before retrying."
    if status == "busy":
        return "busy", None, "Movie Time is already running."
    return "unknown", None, "I couldn't confirm the Movie Time result. Check the projector."
