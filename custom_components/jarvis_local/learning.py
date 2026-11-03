"""Bounded, opt-in evidence for improving Declan's command grammar.

No automatic execution rules are learned from failures: that would let a
misrecognition silently become a device command. Learning examples are saved separately from transient diagnostics.
"""
from collections import Counter
import re
import logging
from datetime import datetime, timezone

_LOGGER = logging.getLogger(__name__)



def _validated_evidence(value):
    """Restore only bounded learning fields, ignoring malformed examples."""
    if not isinstance(value, list):
        return []
    result = []
    for item in value[-40:]:
        if not isinstance(item, dict) or not isinstance(item.get('outcome'), str) or item['outcome'] not in {
                'failed', 'rejected', 'partial', 'completed'}:
            continue
        if not isinstance(item.get('heard'), str) or not item['heard'].strip():
            continue
        corrections = item.get('corrections', [])
        result.append({
            'time': item.get('time') if isinstance(item.get('time'), str) else None,
            'heard': item['heard'][:200],
            'resolved': item.get('resolved', '')[:200] if isinstance(item.get('resolved', ''), str) else '',
            'outcome': item['outcome'],
            'reason': item.get('reason', '')[:160] if isinstance(item.get('reason', ''), str) else '',
            'corrections': [text[:200] for text in corrections[:5] if isinstance(text, str)]
                           if isinstance(corrections, list) else [],
        })
    return result



def _validated_usage(value):
    if not isinstance(value, dict):
        return {}
    result = {}
    for key, item in list(value.items())[:40]:
        if not isinstance(key, str) or not isinstance(item, dict):
            continue
        result[key[:150]] = {
            'successes': max(0, item.get('successes', 0)) if type(item.get('successes', 0)) is int else 0,
            'failures': max(0, item.get('failures', 0)) if type(item.get('failures', 0)) is int else 0,
            'last_success': item.get('last_success') if isinstance(item.get('last_success'), str) else None,
            'last_failure': item.get('last_failure') if isinstance(item.get('last_failure'), str) else None,
            'needs_review': item.get('needs_review') is True,
        }
    return result



def _validated_history(value):
    result=[]
    if not isinstance(value,list):return result
    for item in value[-100:]:
        if not isinstance(item,dict):continue
        if item.get('decision') not in ('approve','approve_manual','edit','reject','remove'):continue
        result.append({key: str(item.get(key) or '')[:200] for key in ('time','decision','heard','before','after')})
    return result


def test_correction(hass, heard, target=None):
    """Plan only: no agent, services, approval, history or conversation mutation."""
    key=normalize_alias(heard)
    data=hass.data.get('jarvis_local',{})
    observed=any(' '.join(str(item.get('heard') or '').casefold().split())==key
                 for item in data.get('learning_evidence',[]))
    if key not in data.get('approved_aliases',{}) and not observed:
        raise ValueError('Choose an observed or approved phrase to test')
    resolved=normalize_alias(target) if target else resolve_alias(hass,heard)
    from .planner import plan
    steps, preview=plan(hass,'preview '+resolved)
    if not preview:raise ValueError('This correction cannot be safely previewed')
    return {'heard':key,'resolved':resolved,'preview':True,
            'summary':'Preview only: '+'; then '.join(step['label'] for step in steps)+'. No actions were run.'}


def _snapshot(data):
    return {'examples': _validated_evidence(data.get('learning_evidence', [])),
            'usage': _validated_usage(data.get('learning_usage', {})),
            'history': _validated_history(data.get('learning_history', []))}


def track_usage(hass, record):
    if record.get('preview') or 'voice correction' in (record.get('transcript_corrections') or []):
        return
    data = hass.data.setdefault('jarvis_local', {})
    try:
        key = normalize_alias(record.get('received_text'))
    except ValueError:
        return
    if key not in data.get('approved_aliases', {}):
        return
    outcome = record.get('outcome')
    steps = record.get('steps') or []
    success = outcome == 'completed' and bool(steps) and not any(step.get('unverified') for step in steps)
    failure = outcome in {'failed', 'rejected', 'partial'}
    if not success and not failure:
        return
    usage = data.setdefault('learning_usage', {})
    item = usage.setdefault(key, {'successes': 0, 'failures': 0, 'needs_review': False})
    if success:
        item['successes'] += 1
        item['last_success'] = record.get('time')
        item['needs_review'] = False
    else:
        item['failures'] += 1
        item['last_failure'] = record.get('time')
        item['needs_review'] = True
    _save_evidence(data)


async def load_evidence(hass):
    """Restore examples without approving aliases or executing actions."""
    from homeassistant.helpers.storage import Store
    data = hass.data.setdefault('jarvis_local', {})
    store = Store(hass, 1, 'jarvis_local.learning_evidence')
    data['learning_evidence_store'] = store
    try:
        saved = await store.async_load()
    except (OSError, ValueError):
        _LOGGER.warning('Could not load saved learning examples')
        saved = None
    data['learning_history'] = _validated_history(saved.get('history') if isinstance(saved,dict) else None)
    data['learning_usage'] = _validated_usage(saved.get('usage') if isinstance(saved, dict) else None)
    data['learning_evidence'] = _validated_evidence(
        saved.get('examples') if isinstance(saved, dict) else None)


def _save_evidence(data):
    store = data.get('learning_evidence_store')
    if store is not None:
        # Read at write time to avoid stale snapshots; HA flushes on shutdown.
        store.async_delay_save(
            lambda: _snapshot(data), 1)


async def flush_evidence(hass):
    """Finish pending writes before unloading."""
    data = hass.data.get('jarvis_local', {})
    store = data.get('learning_evidence_store')
    if store is not None:
        await store.async_save(_snapshot(data))


def observe(hass, record):
    track_usage(hass, record)
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
    _save_evidence(data)


def summary(hass):
    evidence = hass.data.get('jarvis_local', {}).get('learning_evidence', [])
    return {'total': len(evidence),
            'outcomes': dict(Counter(item['outcome'] for item in evidence)),
            'correction_samples': sum(bool(item['corrections']) for item in evidence)}


def speech_variants(heard, approved):
    """Review-only close phrases; never turn similarity into an executable alias."""
    from difflib import SequenceMatcher
    cleaned = re.sub(r'[^a-z0-9 ]', '', heard.casefold()).strip()
    matches = []
    for source, target in approved.items():
        reference = re.sub(r'[^a-z0-9 ]', '', source.casefold()).strip()
        if cleaned and reference and cleaned != reference and SequenceMatcher(
                None, cleaned, reference).ratio() >= 0.78:
            matches.append({'heard': source, 'suggested': target})
    return matches[:3]


def failure_category(reason):
    """Keep transport/device faults separate from possible recognition failures."""
    reason = str(reason or '').casefold()
    if any(term in reason for term in ('unavailable', 'timed out', 'timeout',
                                      'service call', 'connection error', 'offline')):
        return 'device_or_service'
    if any(term in reason for term in ('which room', 'which lights', 'ambiguous',
                                      'multiple matches')):
        return 'clarification'
    return 'unrecognised_command'


def suggestions(hass, minimum_occurrences=1):
    """Review failures immediately and repeated explicit correction pairs.

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
                                             'reason': str(item.get('reason') or '')[:160],
                                             'category': failure_category(item.get('reason'))})
            group['count'] += 1
        if any(marker in (item.get('corrections') or []) for marker in ('superseded earlier command', 'voice correction')) and item.get('outcome') == 'completed':
            resolved = ' '.join(str(item.get('resolved') or '').casefold().split())
            if not resolved or resolved == heard:
                continue
            key = ('correction', heard, resolved)
            group = groups.setdefault(key, {'type': 'correction_candidate',
                                             'heard': heard, 'suggested': resolved, 'count': 0})
            group['count'] += 1
            if 'voice correction' in (item.get('corrections') or []):
                group['source'] = 'voice'
    for key, group in list(groups.items()):
        if group.get('source') == 'voice':
            groups.pop(('failed', group['heard']), None)
    threshold = max(1, int(minimum_occurrences))
    rejected = set(hass.data.get('jarvis_local', {}).get('rejected_aliases', []))
    approved = hass.data.get('jarvis_local', {}).get('approved_aliases', {})
    pending = [group for group in groups.values() if group['count'] >= (max(2, threshold) if group['type'] == 'correction_candidate' and group.get('source') != 'voice' else threshold)
               and group['heard'] not in rejected and group['heard'] not in approved]
    for group in pending:
        if group['type'] == 'repeated_failure' and group['category'] == 'unrecognised_command':
            group['similar_approved'] = speech_variants(group['heard'], approved)
            options = command_suggestions(hass, group['heard'], group['similar_approved'])
            if options:
                group['options'] = options
    return sorted(pending, key=lambda group: (-group['count'], group['heard']))



def command_suggestions(hass, heard, approved_matches):
    """Rank review-only phrases; use only Assist-exposed live light inventory."""
    from difflib import SequenceMatcher
    options = [{'command': item['suggested'], 'source': 'approved phrase'}
               for item in approved_matches]
    # Do not guess an action, polarity or multi-step request from fuzzy speech.
    action = re.search(r'\b(on|off)\b', heard)
    unsafe = re.search(r"\b(?:don't|not|never|then|and|unlock|lock|open|close)\b", heard)
    if action and not unsafe and callable(getattr(getattr(hass, 'states', None), 'async_all', None)):
        from .discovery import inventory, display_name, lighting
        rooms, unassigned = inventory(hass)
        ids = set(unassigned) | {entity for room in rooms.values() for entity in room['lights']}
        ranked = []
        for entity in sorted(ids):
            state = hass.states.get(entity)
            if state is None or state.state in {'unknown', 'unavailable'}:
                continue
            command = 'turn ' + action[1] + ' ' + display_name(state).casefold()
            score = SequenceMatcher(None, heard, command).ratio()
            if score < 0.55:
                continue
            try:
                step = lighting(hass, command)
            except ValueError:
                continue
            if step and step.get('kind') == 'light' and step.get('data', {}).get('entity_id') == [entity]:
                ranked.append((score, {'command': command, 'source': 'known light'}))
        options += [option for _, option in sorted(ranked, key=lambda pair: -pair[0])[:3]]
    unique = {}
    for option in options:
        unique.setdefault(option['command'], option)
    return list(unique.values())[:3]


def validate_manual_light_command(text):
    """Normalize one explicitly named light action without broadening its scope."""
    import re
    value = normalize_alias(text).strip(' .!?')
    if any(word in value.split() for word in ('and', 'then', 'or', 'all', 'every', 'everything')):
        raise ValueError('Only one specific lighting target can be taught at a time')
    match = re.fullmatch(r'(?:turn|switch) (on|off) (?:the )?([a-z0-9][a-z0-9 -]*lights?)', value)
    if match:
        action, target = match.groups()
    else:
        match = re.fullmatch(r'(?:the )?([a-z0-9][a-z0-9 -]*lights?) (on|off)', value)
        if not match:
            raise ValueError('Enter a named light and action, e.g. fairy lights off')
        target, action = match.groups()
    return f'turn {action} {target}'



def validate_taught_command(hass, text):
    """Allow named exposed lights, keeping manual training narrowly scoped."""
    try:
        return validate_manual_light_command(text)
    except ValueError:
        value = normalize_alias(text).strip(' .!?')
        if not re.fullmatch(r'(?:turn|switch) (?:on|off) [a-z0-9 -]+', value) or any(
                word in value.split() for word in ('all', 'every', 'everything', 'and', 'then', 'or')):
            raise ValueError('Teach one explicitly named light action')
        if not callable(getattr(getattr(hass, 'states', None), 'async_all', None)):
            raise ValueError('Teach one known light action')
        from .discovery import lighting
        step = lighting(hass, value)
        if not step or step.get('kind') != 'light' or len(step.get('data', {}).get('entity_id', [])) != 1:
            raise ValueError('Teach one known light action')
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
    if decision not in {'approve', 'approve_manual', 'edit', 'reject', 'remove'}:
        raise ValueError('Unknown review decision')
    data = hass.data.setdefault('jarvis_local', {})
    aliases = dict(data.get('approved_aliases', {}))
    previous_target=aliases.get(key,'')
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
    elif decision in {'approve_manual', 'edit'}:
        if decision == 'edit' and key not in aliases:
            raise ValueError('Only approved phrases can be edited')
        target = validate_taught_command(hass, suggested)
        if key == target or (decision != 'edit' and key in aliases and aliases[key] != target):
            raise ValueError('Conflicting or identical alias')
        if decision != 'edit' and not any(c['heard'] == key
                   for c in suggestions(hass)):
            raise ValueError('Only observed failures can be taught manually')
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
    if decision in {'edit', 'remove', 'reject'}:
        data.get('learning_usage', {}).pop(key, None)
        _save_evidence(data)
    data['approved_aliases'] = aliases
    data['rejected_aliases'] = sorted(rejected)[:80]
    history=data.setdefault('learning_history',[])
    history.append({'time':datetime.now(timezone.utc).isoformat(),'decision':decision,
                    'heard':key,'before':previous_target,'after':aliases.get(key,'')})
    del history[:-100]
    _save_evidence(data)
    return {'approved': aliases, 'rejected': sorted(rejected)[:80]}
