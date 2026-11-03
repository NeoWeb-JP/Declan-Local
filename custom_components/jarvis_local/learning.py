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
