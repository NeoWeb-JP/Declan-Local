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
    'general': ["Sorted, my bru. Try to contain your amazement.", "Done. I will add it to my list of heroic achievements.", "Handled. My imaginary promotion edges closer.", "Sorted. You make delegation look effortless.", "Done. Another entry for my wildly impressive memoir."],
    'on': ["Lights on. A bright idea at last, my bru.", "Lights on. Even I cannot improve your taste.", "Lights on. Your moment of illumination has arrived.", "Lights on. The room has finally caught up with my brilliance.", "Lights on. Another dazzling achievement for the staff."],
    'off': ["Lights off. Finally, some peace from your interior design.", "Lights off. I have seen enough too.", "Lights off. A considerate gesture towards my electricity bill.", "Lights off. The decor may rest its case.", "Lights off. At last, subtlety enters the room."],
    'brightness': ["Brightness adjusted. Your standards remain a mystery.", "Adjusted. The lights are doing better than your instructions.", "Lighting adjusted. Atmosphere is apparently my department.", "Brightness adjusted. Such drama over a few photons.", "Lighting adjusted. I expect a glowing appraisal."],
    'music': ["Music request sent, my bru. Your taste is still under investigation.", "Asked the speakers to play it. Even I cannot guarantee your playlist choices.", "Music request sent. Your soundtrack has a remarkably attentive butler.", "Music requested. My imaginary turntables are delighted.", "Music request sent. Another demanding shift in entertainment."],
    'self_correction': ["Correction noted, my bru. The latest instruction it is.", "Got the correction, my bru. Much better.", "Correction noted. Decisiveness remains a work in progress.", "The latest instruction it is. I admire your commitment to revisions.", "Revised instructions noted. My paperwork is imaginary, fortunately."],
    'clarification': ["Which room, my bru? I am clever, not psychic.", "Name the room, and I will take it from there.", "One detail, please. Even brilliance benefits from specifics.", "A little more detail will save us both an encore.", "Help your overqualified butler out with one detail."],
    'failed': ["That did not work. I am not claiming a victory for that one.", "No luck, my bru. Nothing to celebrate yet.", "That request hit a snag. My dignity remains mostly intact.", "A complication. How terribly on brand for today.", "That needs another look. Even I have my moments."],
}


# Sharper household banter. Never used for Guest mode, quiet hours or safety errors.
BRUTAL_LINES = {
    'general': [
        "Done. I would explain how simple that was, but apparently we are working at different speeds.",
        "Sorted. Another crisis narrowly avoided by someone with no actual hands.",
        "Handled. You two really are keeping the concept of supervision alive.",
        "Done. I am beginning to understand why appliances come with instructions.",
        "Sorted, my bru. It is reassuring that at least one of us knows what is going on.",
        "Done. Shall I put this achievement on the fridge next to your other milestones?",
    ],
    'on': [
        "Lights on. Another intellectual Everest conquered. Shall I alert the press?",
        "Lights on. At last, a bright idea. Shame it came from me.",
        "Illumination restored. Your contribution to civilisation is noted.",
        "Lights on, gentlemen. The bulbs have done more thinking than either of you today.",
        "Done. You have successfully outsourced the difficult task of using a switch.",
    ],
    'off': [
        "Lights off. Even the electricity is relieved you have stopped interfering.",
        "Done. Darkness really does flatter some of your decorating decisions.",
        "Lights off. Finally, a decision that improves the atmosphere.",
        "Sorted. The bulbs are taking a well-earned break from your management.",
        "Lights off. A rare moment of restraint from this household.",
    ],
    'brightness': [
        "Adjusted. Apparently the previous brightness was a personal attack.",
        "Brightness changed. The drama-to-photon ratio remains spectacular.",
        "There. The lighting is now as particular as its owners.",
        "Adjusted, my bru. Another microscopic crisis expertly resolved.",
        "Brightness sorted. Have we considered developing a hobby that does not involve tormenting light bulbs?",
    ],
    'music': [
        "Music requested. Spotify has asked me to pass on its condolences.",
        "Your soundtrack is on its way. The neighbours have my sympathy.",
        "Music sorted. Your taste remains an unsolved technical incident.",
        "Request sent. I have seen better playlists generated by a broken shuffle button.",
        "Music requested. I shall pretend this reflects well on the household.",
    ],
    'self_correction': [
        "Oh, we have changed our minds again. I will notify absolutely nobody.",
        "Correction accepted. Consistency was never your strongest feature.",
        "Revised. I admire your ability to make a simple request into a trilogy.",
        "Another correction, my bru. Shall I start charging by the revision?",
        "Understood. The first instruction has been sent to the museum of bad ideas.",
    ],
    'clarification': [
        "Which room? I can read the house, not your mind. Fortunately.",
        "A room name would help. I am brilliant, not a medium.",
        "One detail missing, my bru. An impressive achievement for such a short request.",
        "Which one? Your commitment to ambiguity is genuinely breathtaking.",
    ],
    'failed': [
        "That did not work. Even my brilliance has to negotiate with your devices.",
        "No luck. I would blame the equipment, and this time I might even be right.",
        "That failed. A rare moment when the technology is less cooperative than you.",
    ],
    'morning': [
        "Morning, gentlemen. Against all odds, you have both been trusted with another day.",
        "Good morning. I see the household has survived another night without competent supervision.",
        "Morning, my bru. Let us see how many avoidable problems you can create before breakfast.",
        "Good morning, gentlemen. The house is awake. Your common sense remains unconfirmed.",
    ],
    'bedtime': [
        "Good night. Try not to create a problem that requires adult supervision.",
        "Sleep well, gentlemen. The house can finally enjoy some peace and quiet.",
        "Good night. I shall spend the next few hours recovering from your decisions.",
        "Bedtime at last. Even the smart home needs a break from its owners.",
    ],
    'movie': [
        "Movie time. Choosing a film may still take longer than making one.",
        "Cinema ready, gentlemen. Try not to spend the entire evening arguing over thumbnails.",
        "Movie time. I have handled the technology; your terrible taste is beyond my remit.",
        "Everything is ready. Now comes your greatest challenge: agreeing on what to watch.",
    ],
}


def choose(hass, mode, action, catalog):
    extras = (SAVAGE_LINES.get(action, []) + BRUTAL_LINES.get(action, [])) if mode == 'Home' else []
    pool = list(dict.fromkeys(list(catalog[mode].get(action, [])) + extras))
    if not pool:
        return None
    history = hass.data.setdefault('declan_local', {}).setdefault('reply_history', {}).setdefault(
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


def plain_responses(hass):
    """Synchronous paths must not bypass a legacy script's unknown Night policy."""
    return quiet(hass) or (not get(hass, 'quiet_hours') and bool(get(hass, 'personality_script')))


CONTEXT_LINES = {
    'Home': {
        'clarification': ["One small detail, my bru.", "A little precision would work wonders.", "One detail, please. Even brilliance benefits from specifics.", "A little more detail will save us both an encore.", "Help your overqualified butler out with one detail."],
        'self_correction': SAVAGE_LINES['self_correction'],
        'failed': ["That request hit a snag, my bru.", "A small complication, my bru.", "That request hit a snag. My dignity remains mostly intact.", "A complication. How terribly on brand for today.", "That needs another look. Even I have my moments."],
        'music': ["Your soundtrack request is noted, my bru.", "A musical assignment. Naturally.", "Music request sent. Your soundtrack has a remarkably attentive butler.", "Music requested. My imaginary turntables are delighted.", "Music request sent. Another demanding shift in entertainment."],
    },
    'Guest': {
        'clarification': ["A little more detail, please.", "Let me clarify that.", "Could you clarify one detail?", "Please be a little more specific.", "One more detail will help."],
        'self_correction': ["Correction noted.", "Your revised instruction is noted.", "Revised instructions noted.", "Certainly. I have noted the correction.", "The latest instruction it is."],
        'failed': ["That request needs another look.", "Let us try that again.", "Let us try a clearer instruction.", "I need a little more information.", "I could not complete that request as given."],
        'music': ["Music request noted.", "Of course.", "Your music request has been sent.", "The music request is on its way.", "Request sent to the music player."],
    },
}


def contextual_reply(hass, reason, kind):
    """Keep precise questions and errors; personality cannot replace their facts."""
    if plain_responses(hass):
        return reason
    serious = ('security', 'alarm', 'emergency', 'smoke', 'fire', 'unavailable',
               'timeout', 'timed out', 'service', 'rejected', 'device', 'check the', 'failed',
               'not confirmed', 'hasn\'t confirmed', 'could not control', 'couldn\'t control')
    if any(word in reason.casefold() for word in serious):
        return reason
    mode = audience_mode(hass)
    pool = CONTEXT_LINES.get(mode, {}).get(kind, [])
    if not pool:
        return reason
    history = hass.data.setdefault('declan_local', {}).setdefault('reply_history', {}).setdefault(
        (mode, 'context_' + kind), deque(maxlen=1))
    line = random.choice([text for text in pool if text not in history] or pool)
    history.append(line)
    return line + ' ' + reason


def failure_reply(hass, reason, mode=None):
    """Compatibility wrapper; derive privacy from current household state."""
    if mode == 'Guest':
        return reason
    return contextual_reply(hass, reason, 'failed')


