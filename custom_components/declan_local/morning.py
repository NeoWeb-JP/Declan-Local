"""Speaker-aware morning replies, without guessing who is speaking."""
import random

NEUTRAL = (
    'Good morning. The routine is underway. Naturally, I did the organising.',
    'Good morning. The morning routine is underway. My imaginary pay rise remains overdue.',
    'Morning. I have started the routine. Another triumph for your overqualified butler.',
)
NAMED = (
    'Good morning, {name}. The routine is underway. Your butler remains scandalously underpaid.',
    'Morning, {name}. The routine is underway. I trust you can manage the waking-up part.',
    'Good morning, {name}. The routine is underway. Another day of impeccable service, my bru.',
)

def morning_reply(name, profiles, history=None):
    """Use only trusted profile's local phrases, otherwise safe generic replies."""
    if not isinstance(name, str) or not name:
        return _choose(NEUTRAL, 'unknown', history)
    profile = next((item for item in profiles.values() if isinstance(item, dict)
                    and item.get('name') == name), {}) if isinstance(profiles, dict) else {}
    phrases = profile.get('morning_responses')
    if isinstance(phrases, list):
        valid = [p.strip() for p in phrases if isinstance(p, str) and p.strip() and len(p) <= 500]
        if valid:
            return _choose(valid, name, history).replace('{name}', name)
    return _choose(NAMED, name, history).replace('{name}', name)


def _choose(pool, key, history):
    previous = history.get(key) if isinstance(history, dict) else None
    options = [value for value in pool if value != previous] or list(pool)
    selected = random.choice(options)
    if isinstance(history, dict): history[key] = selected
    return selected
