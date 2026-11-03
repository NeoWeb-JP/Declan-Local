"""Bounded, opt-in evidence for improving Declan's command grammar.

No automatic execution rules are learned from failures: that would let a
misrecognition silently become a device command. Diagnostics remain in memory.
"""
from collections import Counter


def observe(hass, record):
    data = hass.data.setdefault('jarvis_local', {})
    if not data.get('debug_enabled', False) or record.get('preview'):
        return
    outcome = record.get('outcome')
    corrections = record.get('transcript_corrections') or []
    if outcome not in {'failed', 'rejected', 'partial'} and not corrections:
        return
    # Only retain a small sample, not a second unbounded transcript history.
    evidence = data.setdefault('learning_evidence', [])
    evidence.append({
        'time': record.get('time'),
        'heard': str(record.get('received_text') or '')[:200],
        'resolved': str(record.get('resolved_text') or '')[:200],
        'outcome': outcome,
        'reason': str(record.get('error') or '')[:160],
        'corrections': list(corrections)[:5],
    })
    del evidence[:-40]


def summary(hass):
    evidence = hass.data.get('jarvis_local', {}).get('learning_evidence', [])
    return {'total': len(evidence),
            'outcomes': dict(Counter(item['outcome'] for item in evidence)),
            'correction_samples': sum(bool(item['corrections']) for item in evidence)}


def suggestions(hass, minimum_occurrences=2):
    """Review-only repeated failures and explicit correction pairs.

    Never install aliases, infer devices or run actions from observations.
    """
    import re
    evidence = hass.data.get('jarvis_local', {}).get('learning_evidence', [])
    groups = {}
    for item in evidence:
        heard = ' '.join(str(item.get('heard') or '').casefold().split())
        if not heard or len(heard) > 200:
            continue
        # Avoid promoting arbitrary utterances into executable commands.
        if item.get('outcome') in {'failed', 'rejected', 'partial'}:
            key = ('failed', heard)
            group = groups.setdefault(key, {'type': 'repeated_failure',
                                             'heard': heard, 'count': 0,
                                             'reason': str(item.get('reason') or '')[:160]})
            group['count'] += 1
        if 'superseded earlier command' in (item.get('corrections') or []) and item.get('outcome') == 'completed':
            resolved = ' '.join(str(item.get('resolved') or '').casefold().split())
            if not resolved or resolved == heard:
                continue
            key = ('correction', heard, resolved)
            group = groups.setdefault(key, {'type': 'correction_candidate',
                                             'heard': heard, 'suggested': resolved, 'count': 0})
            group['count'] += 1
    threshold = max(2, int(minimum_occurrences))
    rejected = set(hass.data.get('jarvis_local', {}).get('rejected_aliases', []))
    approved = hass.data.get('jarvis_local', {}).get('approved_aliases', {})
    return sorted((group for group in groups.values() if group['count'] >= threshold
                   and group['heard'] not in rejected and group['heard'] not in approved),
                  key=lambda group: (-group['count'], group['heard']))[:20]


def validate_manual_light_command(text):
    """Only allow explicit lighting commands for manually taught STT aliases."""
    import re
    value = normalize_alias(text)
    if not re.fullmatch(r'(?:turn|switch) (?:on|off) (?:the )?[a-z0-9][a-z0-9 -]*', value):
        raise ValueError('Enter a complete lighting command, e.g. turn off fairy lights')
    if any(word in value.split() for word in ('and', 'then', 'or', 'all', 'every', 'everything')):
        raise ValueError('Only one specific lighting target can be taught at a time')
    return value


def normalize_alias(text):
    import re
    if not isinstance(text, str):
        raise ValueError('Alias must be text')
    value = ' '.join(text.casefold().split())
    if not 3 <= len(value) <= 150 or not re.fullmatch(r"[a-z0-9 ,.!?' -]+", value):
        raise ValueError('Alias must be 3-150 plain-text characters')
    return value


def resolve_alias(hass, text):
    """Only explicit admin-approved exact phrases; never infer an action."""
    try:
        key = normalize_alias(text)
    except ValueError:
        return text
    return hass.data.get('jarvis_local', {}).get('approved_aliases', {}).get(key, text)


async def review(hass, heard, decision, suggested=None):
    """Administrator API handler. Persist decisions, never execute anything."""
    from homeassistant.helpers.storage import Store
    key = normalize_alias(heard)
    if decision not in {'approve', 'approve_manual', 'reject', 'remove'}:
        raise ValueError('Unknown review decision')
    data = hass.data.setdefault('jarvis_local', {})
    aliases = dict(data.get('approved_aliases', {}))
    rejected = set(data.get('rejected_aliases', []))
    if decision == 'approve':
        target = normalize_alias(suggested)
        candidates = suggestions(hass)
        if not any(c['type'] == 'correction_candidate' and c['heard'] == key
                   and c['suggested'] == target for c in candidates):
            raise ValueError('Only repeated, successful correction candidates can be approved')
        if key == target or key in aliases and aliases[key] != target:
            raise ValueError('Conflicting or identical alias')
        if len(aliases) >= 40 and key not in aliases:
            raise ValueError('Maximum approved aliases reached')
        aliases[key] = target
        rejected.discard(key)
    elif decision == 'approve_manual':
        target = validate_manual_light_command(suggested)
        if key == target or key in aliases and aliases[key] != target:
            raise ValueError('Conflicting or identical alias')
        if not any(c['type'] == 'repeated_failure' and c['heard'] == key
                   for c in suggestions(hass)):
            raise ValueError('Only observed repeated failures can be taught manually')
        if len(aliases) >= 40 and key not in aliases:
            raise ValueError('Maximum approved aliases reached')
        aliases[key] = target
        rejected.discard(key)
    elif decision == 'reject':
        aliases.pop(key, None)
        rejected.add(key)
    else:
        aliases.pop(key, None)
        rejected.discard(key)
    await Store(hass, 1, 'jarvis_local.learning_aliases').async_save(
        {'approved': aliases, 'rejected': sorted(rejected)[:80]})
    data['approved_aliases'] = aliases
    data['rejected_aliases'] = sorted(rejected)[:80]
    return {'approved': aliases, 'rejected': sorted(rejected)[:80]}
