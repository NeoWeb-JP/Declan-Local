"""Conservative cross-utterance corrections, scoped to a conversation identity."""
import re

_CORRECTION = re.compile(r"^(?:no[ ,]+i[ ,]+meant|sorry[ ,]+i[ ,]+meant|actually[ ,]+i[ ,]+meant|no[ ,]+actually|scratch that)[ ,]+(.+)$", re.I)
_ACTION = re.compile(r"^(?:turn|switch|set|adjust|dim|brighten|make|play|pause|resume|skip|stop|start|cancel|preview|dry run)\\b", re.I)


def corrected_followup(text, previous):
    """Return explicit replacement only after a rejected request; never inherit an action."""
    if not previous or previous.get('outcome') not in {'failed', 'rejected'}:
        return None
    match = _CORRECTION.fullmatch(text.strip())
    if not match:
        return None
    replacement = match[1].strip()
    if not _ACTION.match(replacement):
        raise ValueError('Please state the full corrected command. Nothing was run.')
    return replacement
