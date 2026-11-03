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
