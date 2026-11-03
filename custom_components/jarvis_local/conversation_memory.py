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
    prefix=''
    text=text.strip()
    for candidate in ('preview ', 'dry run ', 'what would you do if i said '):
        if text.lower().startswith(candidate):
            prefix=candidate
            text=text[len(candidate):]
            break
    if not previous or previous.get('action') not in {'turn_on', 'turn_off', 'brightness'}:
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
    if previous['action'] == 'brightness':
        value=previous.get('brightness_pct')
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<=value<=100:
            return None
        return prefix+f'set {room} lights to {value:g} percent'
    action = 'on' if previous['action'] == 'turn_on' else 'off'
    return prefix+f'turn {action} the lights in {room}'


def verified_lighting_context(steps, now):
    """Remember only one common setting confirmed for all affected lights."""
    import math
    settings = {}
    for step in steps:
        if step.get('kind') not in {'light', 'switch_light', 'brightness'} or step.get('failed') or step.get('unverified'):
            return None
        succeeded = set(step.get('succeeded', []))
        calls = step.get('calls', []) if step['kind'] == 'brightness' else [
            {'service': step.get('name'), 'data': step.get('data', {})}]
        for call in calls:
            for entity in call.get('data', {}).get('entity_id', []):
                if entity not in succeeded:
                    return None
                data = call['data']
                if call.get('service') == 'turn_off':
                    setting = ('turn_off', None)
                elif 'brightness_pct' in data:
                    value = data['brightness_pct']
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0<=value<=100:
                        return None
                    setting = ('brightness', value)
                elif 'brightness' in data:
                    value = data['brightness']
                    if type(value) is not int or not 0<=value<=255:
                        return None
                    setting = ('brightness', round(value/255*100))
                elif call.get('service') == 'turn_on':
                    setting = ('turn_on', None)
                else:
                    return None
                settings[entity] = setting
    if not settings or len(set(settings.values())) != 1:
        return None
    action, value = next(iter(settings.values()))
    result = {'at': now, 'ids': list(settings), 'action': action}
    if action == 'brightness':
        result['brightness_pct'] = value
    return result
