"""Speech privacy policy. This module never grants household authority."""


def helper_state(hass, key):
    settings = hass.data.get('jarvis_local', {}).get('settings', {})
    entity_id = settings.get(key)
    if not isinstance(entity_id, str) or not entity_id.startswith('input_boolean.'):
        return None
    state = hass.states.get(entity_id)
    return state.state if state is not None and state.state in {'on', 'off'} else None


def mode(hass):
    """Private Home speech requires affirmative, healthy privacy signals.

    An absent/unavailable visitor or authority helper is not evidence that the
    room is private. Speaker identity cannot override this decision.
    """
    settings = hass.data.get('jarvis_local', {}).get('settings', {})
    if settings.get('guests_staying') and helper_state(hass, 'guests_staying') != 'off':
        return 'Guest'
    if helper_state(hass, 'visitors_present') == 'off' and helper_state(hass, 'guest_mode') == 'off':
        return 'Home'
    return 'Guest'


def quiet(hass):
    settings = hass.data.get('jarvis_local', {}).get('settings', {})
    # An explicitly configured but unhealthy quiet-hours helper stays quiet.
    return bool(settings.get('quiet_hours')) and helper_state(hass, 'quiet_hours') != 'off'
