"""Music Assistant playback and controls routed to the same known room player."""
import math
import re

ROOMS = {
    'kitchen': 'media_player.kitchen_declan_voice_assistant',
    'bedroom': 'media_player.bedroom_declan_voice_assistant',
    'living room': 'media_player.living_room_declan',
    'lounge': 'media_player.living_room_declan',
    'downstairs': 'media_player.downstairs_2',
    'everywhere': 'media_player.everywhere_2',
}
_ROOM_PATTERN='|'.join(re.escape(name) for name in sorted(ROOMS,key=len,reverse=True))


def _player(hass, room, area):
    room=(room or getattr(area,'name','') or '').lower().strip()
    room={'master bedroom':'bedroom'}.get(room,room)
    if room not in ROOMS:
        raise ValueError('Which room should I control the music in? Please name a configured room. Nothing was run.')
    entity=ROOMS[room];state=hass.states.get(entity)
    if state is None or state.state in {'unknown','unavailable'}:
        raise ValueError('The music player for '+room+' is unavailable. Nothing was run.')
    return room,entity,state


def _support(state, name):
    attrs=getattr(state,'attributes',{})
    if 'supported_features' not in attrs:return
    from homeassistant.components.media_player import MediaPlayerEntityFeature as Feature
    flag=getattr(Feature,name,None)
    if flag is None or type(attrs['supported_features']) is not int or not attrs['supported_features'] & int(flag):
        raise ValueError('That music player does not report support for this action. Nothing was run.')


def _control(service, room, entity, **data):
    return {'kind':'media_control','name':service,'data':{'entity_id':entity,**data},
            'target_label':room.title(),'label':service.replace('_',' ')+' in '+room}


def plan_music(hass,text,area=None):
    raw=text.strip().rstrip('.!?')
    prefix=re.match(r'^(?:please\s+)?play\s+',raw,re.I)
    if not prefix:return None
    request=raw[prefix.end():]
    request=re.sub(r'\s+please$','',request,flags=re.I)
    match=re.fullmatch(r'(.+?)\s+(?:(?:in|on|through)\s+(?:the\s+)?)?('+_ROOM_PATTERN+r')',request,re.I)
    if match:query,room=match.groups()
    else:query,room=request,None
    # An explicit unknown destination must not silently play in the source room.
    if not match and re.search(r'\s+(?:in|through)\s+(?:the\s+)?[a-z -]+$',request,re.I) and not re.search(r'["\x27]',request):
        raise ValueError('I could not identify that music room. Name a configured room, or quote the song title. Nothing was run.')
    room,entity,state=_player(hass,room,area)
    query=re.sub(r'^(?:some|me some)\s+','',query,flags=re.I).strip()
    if re.search(r'\band (?:then )?(?:turn|switch|set|unlock|open|stop)\b',query,re.I):
        raise ValueError('Please give one music request at a time. Nothing was run.')
    kind='artist';artist=None
    typed=re.match(r'^(?:(?:the|my|a) )?(playlist|album|song|track|artist)\s+(.+)$',query,re.I)
    if typed:
        kind={'song':'track'}.get(typed[1].lower(),typed[1].lower());query=typed[2].strip()
    elif query.lower().endswith(' music') and query.lower()[:-6].strip() in {
            'country','rock','pop','jazz','classical','blues','dance','folk','reggae','soul','ambient','electronic','hip hop'}:
        kind='playlist';query=query[:-6].strip()
    if kind in {'artist','track','album'} and ' by ' in query.lower():
        query,artist=[part.strip() for part in re.split(r'\s+by\s+',query,maxsplit=1,flags=re.I)]
        if kind=='artist':kind='track'
    query=query.strip('"\x27')
    if not query or len(query)>150 or artist is not None and not artist:
        raise ValueError('Please name music to play. Nothing was run.')
    if kind == 'playlist' and query.lower() in {'country','rock','pop','jazz','classical','blues','dance','folk','reggae','soul','ambient','electronic','hip hop','braai','romantic'}:
        category = query.lower()
        return {'kind': 'music_category', 'category': category, 'room': room,
                'label': 'play rotating ' + category + ' music in ' + room}
    data={'media_id':query,'media_type':kind}
    if artist:data['artist']=artist
    return {'kind':'music_assistant_play','name':'play_media','data':data,'entity_id':entity,
            'target_label':room.title(),'label':'play '+query+' in '+room}


def plan_stop_music(hass,text,area=None):
    match=re.fullmatch(r'(?:please )?(?:(?:stop|turn off)(?: the)? music|music off)'
        r'(?: (?:(?:in|on) (?:the )?)?('+_ROOM_PATTERN+r'))?(?: please)?[.!?]?',text.strip(),re.I)
    if not match:return None
    room,entity,state=_player(hass,match[1],area)
    _support(state,'STOP')
    return _control('media_stop',room,entity)


def plan_music_transport(hass,text,area=None):
    shuffle=re.fullmatch(
        r'(?:please )?(?:(?:turn|switch) (?:the )?shuffle (on|off)|(enable|disable) (?:the )?shuffle|'
        r'shuffle(?: (?:music|songs|tracks))?(?: (on|off))?)'
        r'(?: in (?:the )?(.+?))?(?: please)?[.!?]?',text.strip(),re.I)
    if shuffle:
        mode=(shuffle[1] or shuffle[2] or shuffle[3] or 'on').lower()
        room,entity,state=_player(hass,shuffle[4],area)
        _support(state,'SHUFFLE_SET')
        return _control('shuffle_set',room,entity,shuffle=mode in {'on','enable'})

    match=re.fullmatch(r'(?:please )?(pause|resume|continue|skip|next|previous|restart)'
        r'(?: (?:the |this )?(?:music|song|track|it))?'
        r'(?: (?:(?:in|on) (?:the )?)?('+_ROOM_PATTERN+r'))?(?: please)?[.!?]?',text.strip(),re.I)
    if not match:return None
    room,entity,state=_player(hass,match[2],area)
    action=match[1].lower()
    service,feature={'pause':('media_pause','PAUSE'),'resume':('media_play','PLAY'),
        'continue':('media_play','PLAY'),'skip':('media_next_track','NEXT_TRACK'),
        'next':('media_next_track','NEXT_TRACK'),'previous':('media_previous_track','PREVIOUS_TRACK'),
        'restart':('media_seek','SEEK')}[action]
    _support(state,feature)
    return _control(service,room,entity,**({'seek_position':0} if action=='restart' else {}))


def plan_music_volume(hass,text,area=None):
    text=text.lower().strip().rstrip('.?!')
    amount=None;delta=None;room=None
    match=re.fullmatch(r'(?:please )?set (?:the )?(?:music )?volume(?: in (?:the )?(.+?))? to (\d+(?:\.\d+)?)\s*(?:percent|%)(?: in (?:the )?(.+?))?(?: please)?',text)
    if match:
        if match[1] and match[3]:raise ValueError('Please name one music room. Nothing was run.')
        room=match[1] or match[3];amount=float(match[2])
        if not 0<=amount<=100:raise ValueError('Volume must be between zero and 100 percent. Nothing was run.')
    else:
        match=re.fullmatch(r'(?:please )?(?:turn (?:the )?(?:music|volume|it) (up|down)|(louder|quieter))'
            r'(?: in (?:the )?(.+?))?(?: please)?',text)
        if not match:return None
        delta=0.1 if (match[1] or match[2]) in {'up','louder'} else -0.1
        room=match[3]
    room,entity,state=_player(hass,room,area)
    _support(state,'VOLUME_SET')
    if delta is not None:
        current=getattr(state,'attributes',{}).get('volume_level')
        if isinstance(current,bool) or not isinstance(current,(int,float)) or not math.isfinite(current) or not 0<=current<=1:
            raise ValueError('That player does not report its current volume. Please give a percentage. Nothing was run.')
        amount=max(0,min(1,current+delta))*100
    return _control('volume_set',room,entity,volume_level=round(amount/100,4))


def plan_music_status(hass,text,area=None):
    match=re.fullmatch(r'(?:what(?: is|\x27s) playing|what song is (?:this|playing))'
        r'(?: in (?:the )?(.+?))?[?!.]?',text.lower().strip())
    if not match:return None
    room,entity,state=_player(hass,match[1],area)
    attrs=getattr(state,'attributes',{})
    title=attrs.get('media_title');artist=attrs.get('media_artist')
    if state.state not in {'playing','paused'}:
        response='Home Assistant reports no active music in '+room+'.'
    elif not isinstance(title,str) or not title.strip():
        response='The '+room+' player is '+state.state+', but it has not reported a track title.'
    else:
        response='Home Assistant reports '+title[:150]+(' by '+artist[:150] if isinstance(artist,str) and artist.strip() else '')+' '+state.state+' in '+room+'.'
    return {'kind':'text','response':response,'label':'check music in '+room}

