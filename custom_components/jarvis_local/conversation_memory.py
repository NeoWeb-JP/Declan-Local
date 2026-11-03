"""Scope short-lived conversational context to a known identity."""


def context_key(user_input, conversation_id, voice_profile=None, area_override=None):
    satellite = getattr(user_input, "satellite_id", None) or getattr(user_input, "device_id", None)
    user_id = getattr(getattr(user_input, "context", None), "user_id", None)
    area_id = getattr(area_override, "id", None)
    if isinstance(voice_profile, str) and voice_profile:
        return ("speaker", voice_profile, satellite, area_id)
    if user_id:
        return ("user", user_id, satellite, area_id)
    return ("anonymous", conversation_id, satellite, area_id)


def context_followup(text, previous):
    """Plan a safe repeat of a verified light action in another named room.

    The caller must still resolve the room and validate the resulting plan.
    """
    import re
    if not previous or previous.get('action') not in {'turn_on', 'turn_off'}:
        return None
    match = re.fullmatch(
        r'(?:please )?(?:do (?:the )?same|same (?:thing|lights)|do that)'
        r' (?:in|for) (?:the )?([a-z][a-z0-9 -]{1,48})(?: please)?[.!?]?',
        text.strip(), re.I)
    if not match:
        return None
    room = match.group(1).strip().lower()
    if any(word in room.split() for word in ('and', 'then', 'or', 'all', 'every')):
        return None
    action = 'on' if previous['action'] == 'turn_on' else 'off'
    return f'turn {action} the lights in {room}'
