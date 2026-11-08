"""Speech privacy policy. This module never grants household authority."""


def helper_state(hass, key):
    settings = hass.data.get('declan_local', {}).get('settings', {})
    entity_id = settings.get(key)
    if not isinstance(entity_id, str) or not entity_id.startswith('input_boolean.'):
        return None
    state = hass.states.get(entity_id)
    return state.state if state is not None and state.state in {'on', 'off'} else None


def mode(hass):
    """Only Guest Mode controls the reply personality.

    Unknown/unavailable Guest Mode stays Guest, avoiding private Home banter.
    Presence, visitors and speaker identity never change the persona.
    """
    return 'Home' if helper_state(hass, 'guest_mode') == 'off' else 'Guest'


def quiet(hass):
    settings = hass.data.get('declan_local', {}).get('settings', {})
    # An explicitly configured but unhealthy quiet-hours helper stays quiet.
    return bool(settings.get('quiet_hours')) and helper_state(hass, 'quiet_hours') != 'off'
