"""Explicit guest handover phrases using existing HA helpers."""
import re
from .settings import get

def recognize(text):
    text=text.strip().rstrip('.!?').strip()
    if re.fullmatch(r'(?:who is in charge|who is looking after the house)',text,re.I):return {'operation':'status'}
    if re.fullmatch(r'(?:(?:the |our )?guests have left)',text,re.I):return {'operation':'clear'}
    if re.fullmatch(r'(?:clear the guests in charge|cancel (?:the )?guest handover|cancel guest authority)',text,re.I):return {'operation':'cancel'}
    staying=re.fullmatch(r'(.+?) (?:are|is) staying with us',text,re.I)
    if staying:
        names=staying[1].strip()
        _validate_names(names)
        return {'operation':'staying','names':names}
    patterns=[r'put (.+?) in charge',r'we are going out and (.+?) (?:are|is) in charge',r'we are going out and leaving (.+?) in charge']
    for pattern in patterns:
        match=re.fullmatch(pattern,text,re.I)
        if match:
            names=match[1].strip()
            # Restrict to names and punctuation, avoiding accidental embedded commands.
            _validate_names(names)
            return {'operation':'set','names':names}
    return None

def _validate_names(names):
    if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ .,'’&-]{0,254}",names):
        raise ValueError('I could not safely identify those names. Nothing was changed.')
    if re.search(r'\b(?:turn|switch|delete|unlock|open|close|set|clear|stop|start)\b',names,re.I):
        raise ValueError('The guest names were unclear. Nothing was changed.')

def build(hass, data):
    mode_id=get(hass, 'guest_mode'); names_id=get(hass, 'guest_names')
    if not (isinstance(mode_id, str) and mode_id.startswith('input_boolean.') and isinstance(names_id, str) and names_id.startswith('input_text.')):
        raise ValueError('Guest helpers are not configured. Nothing was changed.')
    mode=hass.states.get(mode_id);names=hass.states.get(names_id)
    if not mode or mode.state not in {'on','off'} or not names or names.state in {'unknown','unavailable'}:
        raise ValueError('Guest Mode or the guest names helper is unavailable. Nothing was changed.')
    if data['operation'] in {'staying','clear'}:
        for key, domain in (('visitors_present','input_boolean'),('guests_staying','input_boolean'),('guest_staying_names','input_text')):
            entity=get(hass,key)
            value=hass.states.get(entity) if isinstance(entity,str) else None
            if not isinstance(entity,str) or not entity.startswith(domain+'.') or not value or value.state in {'unknown','unavailable'} or (domain=='input_boolean' and value.state not in {'on','off'}):
                raise ValueError('Configure healthy visitor and staying helpers first. Nothing was changed.')
    if data['operation'] in {'set','staying'}:
        target=names if data['operation']=='set' else hass.states.get(get(hass,'guest_staying_names'))
        maxlen=target.attributes.get('max',255)
        if len(data['names'])>maxlen:raise ValueError('The guest names are too long for the helper. Nothing was changed.')
    label={'status':'check who is in charge','clear':'clear visitor/staying declarations and only automatic guest authority',
        'cancel':'cancel guest handover', 'staying':'record '+data.get('names','')+' as staying without granting authority',
        'set':'assign '+data.get('names','')+' and turn on Guest Mode'}[data['operation']]
    return {'kind':'guest','data':data,'label':label}
