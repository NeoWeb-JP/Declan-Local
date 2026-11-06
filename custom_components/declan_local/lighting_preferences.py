"""Explicit, room-scoped lighting snapshots with persistent storage."""
import asyncio
from copy import deepcopy
import re
from .discovery import inventory

_RESERVED = {'light', 'lighter', 'brighter', 'darker', 'on', 'off', 'bright', 'dark'}


def preference_request(hass, text, area=None):
    text=re.sub(r' please$', '', text.lower().strip().rstrip('.?!'))
    match=re.fullmatch(r'(?:please )?(remember (?:these|the) lights as|make it|update) ([a-z][a-z0-9 -]{0,31})(?: please)?',text)
    if not match or match[2] in _RESERVED:return None
    operation='remember' if match[1].startswith('remember') else 'apply' if match[1]=='make it' else 'update'
    if area is None:
        raise ValueError('Which room? Use a voice device assigned to a room or select a chat room. Nothing was changed.')
    rooms,_=inventory(hass)
    if area.id not in rooms:raise ValueError('That room is unavailable. Nothing was changed.')
    return {'kind':'lighting_preference','operation':operation,'name':match[2].strip(),
            'room_id':area.id,'room':rooms[area.id]['name'],
            'label':operation+' '+match[2].strip()+' lighting in '+rooms[area.id]['name']}


def _valid(saved):
    result={}
    if not isinstance(saved,dict):return result
    for room,names in list(saved.items())[:50]:
        if not isinstance(room,str) or not isinstance(names,dict):continue
        for name,lights in list(names.items())[:20]:
            if not isinstance(name,str) or not re.fullmatch(r'[a-z][a-z0-9 -]{0,31}',name) or name in _RESERVED or not isinstance(lights,dict):continue
            clean={}
            for entity,item in list(lights.items())[:100]:
                if not isinstance(entity,str) or not re.fullmatch(r'light\.[a-z0-9_]+',entity) or not isinstance(item,dict):continue
                if item.get('state') not in ('on','off'):continue
                value=item.get('brightness')
                if value is not None and (type(value) is not int or not 1<=value<=255):continue
                clean[entity]={'state':item['state'],'brightness':value}
            if clean:result.setdefault(room,{})[name]=clean
    return result


async def _load(hass):
    from homeassistant.helpers.storage import Store
    data=hass.data.setdefault('declan_local',{})
    lock=data.setdefault('lighting_preferences_lock',asyncio.Lock())
    async with lock:
        if 'lighting_preferences' not in data:
            store=Store(hass,1,'jarvis_local.lighting_preferences')
            try:saved=await store.async_load()
            except (OSError,ValueError) as err:
                raise ValueError('Could not read saved lighting preferences. Nothing was changed.') from err
            data['lighting_preferences_store']=store
            data['lighting_preferences']=_valid(saved)
    return data


def _room_ids(hass,request):
    rooms,_=inventory(hass)
    if request['room_id'] not in rooms:raise ValueError('That room no longer exists. Nothing was changed.')
    return set(rooms[request['room_id']]['lights'])


def _dimmable(state):
    modes=set(state.attributes.get('supported_color_modes') or [])
    features=state.attributes.get('supported_features',0)
    return bool(modes.intersection({'brightness','color_temp','hs','xy','rgb','rgbw','rgbww','white'})) or (isinstance(features,int) and bool(features & 1))


async def prepare_preference(hass,request):
    data=await _load(hass)
    names=data['lighting_preferences'].get(request['room_id'],{})
    name=request['name'];operation=request['operation']
    if operation=='remember' and name in names:
        raise ValueError('That preference already exists in this room. Say update '+name+' to replace it.')
    if operation!='remember' and name not in names:
        raise ValueError('There is no '+name+' lighting preference in this room yet.')
    if operation!='apply':return request
    ids=_room_ids(hass,request)
    calls=[]
    for entity,saved in names[name].items():
        state=hass.states.get(entity)
        if entity not in ids or state is None or state.state not in {'on','off'}:
            raise ValueError('A saved light is unavailable or no longer exposed in this room. Nothing was changed.')
        value=saved['brightness']
        if saved['state']=='on' and value is not None and not _dimmable(state):
            raise ValueError('A saved light no longer supports dimming. Nothing was changed.')
        calls.append({'service':'turn_'+saved['state'],'data':{'entity_id':[entity],
                     **({'brightness':value} if saved['state']=='on' and value is not None else {})}})
    return {'kind':'brightness','calls':calls,'target_label':request['room'],
            'label':'restore '+name+' lighting in '+request['room']}


async def save_preference(hass,request):
    data=await _load(hass)
    async with data['lighting_preferences_lock']:
        names=data['lighting_preferences'].get(request['room_id'],{})
        name=request['name']
        if request['operation']=='remember' and name in names:
            raise ValueError('That preference already exists. Say update '+name+' to replace it.')
        if request['operation']=='update' and name not in names:
            raise ValueError('That preference no longer exists.')
        if name not in names and len(names)>=20:raise ValueError('This room already has 20 lighting preferences.')
        if request['room_id'] not in data['lighting_preferences'] and len(data['lighting_preferences'])>=50:
            raise ValueError('Lighting preferences already cover 50 rooms.')
        ids=_room_ids(hass,request)
        if not ids or len(ids)>100:raise ValueError('A preference needs between one and 100 exposed lights.')
        lights={}
        for entity in sorted(ids):
            state=hass.states.get(entity)
            if state is None or state.state not in {'on','off'}:
                raise ValueError('A room light is unavailable. No preference was saved.')
            value=state.attributes.get('brightness') if state.state=='on' and _dimmable(state) else None
            if state.state=='on' and _dimmable(state) and (type(value) is not int or not 1<=value<=255):
                raise ValueError('A room light has unknown brightness. No preference was saved.')
            lights[entity]={'state':state.state,'brightness':value}
        updated=deepcopy(data['lighting_preferences'])
        updated.setdefault(request['room_id'],{})[name]=lights
        try:await data['lighting_preferences_store'].async_save(updated)
        except (OSError,ValueError) as err:
            raise ValueError('Could not save the lighting preference. Please try again.') from err
        data['lighting_preferences']=updated
    return ('Updated ' if request['operation']=='update' else 'Saved ')+name+' lighting for '+request['room']+'.'

