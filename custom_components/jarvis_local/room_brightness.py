"""Relative room brightness without turning on currently off lights."""
import math
import re
from .discovery import inventory, norm, display_name


def room_brightness(hass, text, area=None):
    match = re.fullmatch(
        r'(?:please )?make (?:the )?(.+?) (lighter|light|brighter|darker)(?: please)?',
        norm(text))
    if not match:
        return None
    target, direction = match.groups()
    rooms, _ = inventory(hass)
    if target in {'room', 'this room', 'it', 'here'}:
        if area is None or area.id not in rooms:
            raise ValueError('Which room? Name a room or use a satellite assigned to that room. Nothing was run.')
        room = rooms[area.id]
    else:
        target = re.sub(r' room$', '', target) if target.endswith(' room') and not any(
            target in room['aliases'] for room in rooms.values()) else target
        matches = [room for room in rooms.values() if target in room['aliases']]
        if len(matches) != 1:
            raise ValueError('I could not identify one room. Please name the room. Nothing was run.')
        room = matches[0]
    delta = -15 if direction == 'darker' else 15
    calls = []
    skipped = []
    for entity_id in room['lights']:
        state = hass.states.get(entity_id)
        if state is None or state.state != 'on':
            continue
        modes = set(state.attributes.get('supported_color_modes') or [])
        features = state.attributes.get('supported_features', 0)
        legacy_dimming = isinstance(features, int) and bool(features & 1)
        if not legacy_dimming and not modes.intersection({
                'brightness', 'color_temp', 'hs', 'xy', 'rgb', 'rgbw', 'rgbww', 'white'}):
            skipped.append(display_name(state))
            continue
        current = state.attributes.get('brightness')
        if isinstance(current, bool) or not isinstance(current, (int, float)) or not math.isfinite(current) or not 0 <= current <= 255:
            skipped.append(display_name(state))
            continue
        percent = max(0, min(100, round(current / 255 * 100) + delta))
        calls.append({'service': 'turn_on' if percent else 'turn_off',
                      'data': {'entity_id': [entity_id], **({'brightness_pct': percent} if percent else {})}})
    if not calls:
        return {'kind': 'text', 'response': 'No lights in '+room['name']+' are on with usable dimming support. Nothing was changed.',
                'label': 'check dimmable lights in '+room['name']}
    return {'kind': 'brightness', 'target_label': room['name'], 'calls': calls,
            'skipped_non_dimmable': skipped,
            'label': ('darken ' if delta < 0 else 'brighten ')+room['name']+
                     ' by 15 percentage points, leaving off lights off'+
                     ('; leave unchanged (no usable dimming): '+', '.join(skipped) if skipped else '')}

