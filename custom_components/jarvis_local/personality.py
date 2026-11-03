"""Short local Home/Guest replies with independent quiet-hours policy."""
import json
import logging
import random
from collections import deque
from pathlib import Path
from time import perf_counter
from homeassistant.exceptions import HomeAssistantError
from .settings import get
from .audience import mode as audience_mode, quiet

_LOGGER = logging.getLogger(__name__)
CATALOG = None


async def _timed_script(hass, name, data, context, stage):
    started = perf_counter()
    try:
        return await hass.services.async_call('script', name, data, blocking=True,
                                              return_response=True, context=context)
    finally:
        _LOGGER.debug('Declan response timing: %s=%.1f ms', stage,
                      (perf_counter() - started) * 1000)


# Home responses blend the existing sassy catalogue with sharper lines.
# Guest and quiet-hours safety policies remain independent.
SAVAGE_LINES = {
    'general': ['Sorted, my bru. Try to contain your amazement.', 'Done. I will add it to my list of heroic achievements.'],
    'on': ['Lights on. A bright idea at last, my bru.', 'Lights on. Even I cannot improve your taste.'],
    'off': ['Lights off. Finally, some peace from your interior design.', 'Lights off. I have seen enough too.'],
    'brightness': ['Brightness adjusted. Your standards remain a mystery.', 'Adjusted. The lights are doing better than your instructions.'],
    'music': ['Music request sent, my bru. Your taste is still under investigation.', 'Asked the speakers to play it. Even I cannot guarantee your playlist choices.'],
    'self_correction': ['Right, corrected. I will pretend the first instruction never happened.', 'Got the correction, my bru. Much better.'],
}


def choose(hass, mode, action, catalog):
    extras = SAVAGE_LINES.get(action, []) if mode == 'Home' else []
    pool = list(dict.fromkeys(list(catalog[mode].get(action, [])) + extras))
    if not pool:
        return None
    history = hass.data.setdefault('jarvis_local', {}).setdefault('reply_history', {}).setdefault(
        (mode, action), deque(maxlen=3))
    available = [line for line in pool if line not in history] or pool
    line = random.choice(available)
    history.append(line)
    return line


async def confirmation(hass, context, fallback, action='general'):
    """Only call after successful actions; failures retain their direct wording."""
    global CATALOG
    if quiet(hass):
        return fallback
    # Preserve existing Night rules until an explicit quiet-hours helper replaces
    # the old policy script. Its Home/Guest choice and arbitrary text are ignored.
    if not get(hass, 'quiet_hours') and get(hass, 'personality_script'):
        script_id = get(hass, 'personality_script')
        state = hass.states.get(script_id) if isinstance(script_id, str) and script_id.startswith('script.') else None
        if state is None or state.state in {'unknown', 'unavailable'}:
            return fallback
        try:
            reply = await _timed_script(hass, script_id.split('.', 1)[1],
                {'response_context': 'general'}, context, 'legacy_quiet_policy')
            if not isinstance(reply, dict) or reply.get('personality') == 'Night':
                return fallback
        except (HomeAssistantError, ValueError, TypeError):
            return fallback
    try:
        if CATALOG is None:
            CATALOG = await hass.async_add_executor_job(
                lambda: json.loads(Path(__file__).with_name('responses.json').read_text(encoding='utf-8')))
        selected_mode = audience_mode(hass)
        line = choose(hass, selected_mode, action, CATALOG)
        if not line:
            return fallback
        phonetic_id = get(hass, 'phonetic_script')
        state = hass.states.get(phonetic_id) if isinstance(phonetic_id, str) and phonetic_id.startswith('script.') else None
        if state and state.state not in {'unknown', 'unavailable'}:
            converted = await _timed_script(hass, phonetic_id.split('.', 1)[1],
                {'input_text': line}, context, 'phonetic_script')
            if audience_mode(hass) != selected_mode or quiet(hass):
                return fallback
            value = converted.get('text') if isinstance(converted, dict) else None
            if isinstance(value, str) and value.strip():
                return value.strip()
        return line
    except (HomeAssistantError, ValueError, TypeError, KeyError, OSError):
        _LOGGER.warning('Declan reply unavailable; using plain confirmation')
        return fallback
