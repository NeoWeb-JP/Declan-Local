"""Resolve explicit corrections before planning; preserve preview and negation."""
import re

_EXPLICIT = re.compile(
    r"\b(?:no[ ,]+i[ ,]+mean(?:t)?|sorry[ ,]+i[ ,]+meant|scratch[ ,]+that|"
    r"no[ ,]+actually|actually[ ,]+i[ ,]+meant)\b", re.I)
_START = r"(?:turn|switch|set|adjust|dim|brighten|make|play|find|search|start|end|stop|cancel|be quiet|shut up|good morning|good night|movie time|cinema time|dinner on|preview|dry run)\b"
_SHORT = re.compile(r"\b(?:actually|rather|sorry)(?!\s+than\b)(?=[ ,]+(?:" + _START + r"|(?:the |maybe |probably |just |only )))", re.I)
_NO_STOP = re.compile(r"\bno(?=[ ,]+(?:stop|cancel|be quiet|shut up)\b)", re.I)
_NO_RELATIVE = re.compile(r"\bno(?=[ ,]+(?:make|adjust|set) (?:it|them)\b)", re.I)
_PREVIEW = re.compile(r"^(preview\s+|dry run\s+|what would you do if i said\s+)", re.I)
_NEGATION = re.compile(r"\b(?:don't|do not|never|not|cannot|can't|shouldn't|wouldn't)\b", re.I)


def final_request(text):
    original = text
    match = _PREVIEW.match(text.strip())
    prefix = match[0] if match else ''
    body = text.strip()[match.end():] if match else text
    # Quoted titles/aliases are literal data, not correction instructions.
    masked = re.sub(r'\"[^\"]*\"|(?<!\w)\x27[^\x27]*\x27(?!\w)',
                    lambda m: ' ' * len(m[0]), body)
    markers = [(m, False) for m in _EXPLICIT.finditer(masked)]
    markers += [(m, True) for m in _SHORT.finditer(masked)]
    markers += [(m, True) for m in re.finditer(r"\bactually[ ,]+no\b", masked, re.I)]
    markers += [(m, False) for m in _NO_STOP.finditer(masked)]
    markers += [(m, True) for m in _NO_RELATIVE.finditer(masked)]
    if not markers:
        return original, False
    marker, short = max(markers, key=lambda value:(value[0].end(), -value[0].start()))
    if short and _NEGATION.search(masked[:marker.start()]):
        raise ValueError('The correction was unclear. Nothing was run. Please state the final request.')
    command = body[marker.end():].strip(' ,;.!?—–-')
    if not command:
        raise ValueError('What should I do instead? Nothing was run.')
    # A target-only correction inherits only a clearly stated on/off action.
    # This happens before planning, so the superseded action never runs.
    fragment = re.fullmatch(r'(?:just |only |the )?(.+)', command, re.I)
    if fragment and not re.match(r'^(?:turn|switch|set|adjust|dim|brighten|make|play|find|search|start|end|stop|cancel|be quiet|shut up|good morning|good night|movie time|cinema time|dinner on|preview|dry run)\b', command, re.I):
        earlier = body[:marker.start()].strip(' ,;.!?')
        action = re.fullmatch(r'(?:please )?(?:turn|switch) (on|off) (?:the )?(.+)', earlier, re.I)
        target = re.sub(r'^(?:just |only |the )+', '', command, flags=re.I).strip()
        if short and action and command.lower().startswith(('the ', 'just ', 'only ')) and re.fullmatch(r'[a-z][a-z0-9 -]{2,70}', target, re.I) and not re.search(r'\b(?:and|then|after|before|instead|because|maybe|probably|please|i|me|we)\b', target, re.I):
            previous_target = action[2].lower()
            if 'light' in previous_target and not re.search(r'\b(?:lights?|spotlights?)\b', target, re.I):
                target += ' lights'
            command = 'turn ' + action[1].lower() + ' ' + target
    # A fragment after a correction is not a complete actionable request.
    # Do not execute an earlier command or guess a target/action.
    if not re.match(r'^(?:turn|switch|set|adjust|dim|brighten|make|play|find|search|start|end|stop|cancel|be quiet|shut up|good morning|good night|movie time|cinema time|dinner on|preview|dry run)\b', command, re.I):
        raise ValueError('Please state the full corrected command. Nothing was run.')
    if prefix and not _PREVIEW.match(command):
        command = prefix + command
    return command, True
