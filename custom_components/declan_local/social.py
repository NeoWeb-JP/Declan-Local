"""Small local conversational replies with optional speaker names."""
import random
import re

POOLS = {
    'thanks': ('You are welcome{address}. A little appreciation suits you.', 'A pleasure{address}. I shall add that to my imaginary pay rise.', 'Any time{address}. Somebody has to keep things civilised.'),
    'hello': ("Hello{address}. Declan here. Do try to make it interesting.", 'Hello{address}. Your overqualified butler is listening.', 'Hi{address}. What domestic drama shall we resolve?'),
}

GUEST_POOLS = {
    'thanks': ('You are welcome{address}. The guest service desk accepts compliments.', 'A pleasure{address}. Even visitors can appreciate excellent service.', 'Any time{address}. I see the guests have discovered gratitude.'),
    'hello': ('Hello{address}. Welcome to the house. Try not to break anything.', 'Hi{address}. Our distinguished visitors have arrived.', 'Hello{address}. I trust you brought your best manners.'),
}

def social_reply(text, name, history, mode='Home'):
    text=re.sub(r'^(?:hey[ ,]+)?(?:declan|jarvis)[ ,:]+', '', str(text).lower().strip()).strip(' .?!')
    text=re.sub(r'\s+(?:declan|jarvis)$', '', text)
    if text in {'thank you','thanks','thanks jarvis','thank you jarvis','cheers'}:kind='thanks'
    elif text in {'hello','hi','hello jarvis','hi jarvis','declan','jarvis','hey declan','hey jarvis'}:kind='hello'
    else:return None
    key=(mode,kind,name or '')
    pool=GUEST_POOLS[kind] if mode == 'Guest' else POOLS[kind]
    available=[item for item in pool if item!=history.get(key)] or pool
    chosen=random.choice(available);history[key]=chosen
    return chosen.replace('{address}', ', '+name if name else '')
