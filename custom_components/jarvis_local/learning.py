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
    return sorted((group for group in groups.values() if group['count'] >= threshold),
                  key=lambda group: (-group['count'], group['heard']))[:20]
