"""Private settings, persisted in Home Assistant storage."""
import json
import logging
from urllib.parse import urlsplit
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)
KEY = 'jarvis_local.settings'
FIELDS = {'weather':'weather', 'thermostat':'climate', 'car_cable_sensor':'binary_sensor', 'car_battery_sensor':'sensor', 'guest_mode':'input_boolean', 'guest_names':'input_text', 'music_script':'script', 'personality_script':'script', 'phonetic_script':'script'}
PRIVACY_FIELDS = {'visitors_present': 'input_boolean', 'quiet_hours': 'input_boolean'}
PRIVACY_FIELDS.update({'guests_staying':'input_boolean', 'guest_auto_enable':'input_boolean',
    'guest_owner_one':'person', 'guest_owner_two':'person', 'guest_away_suspend':'input_boolean',
    'guest_staying_names':'input_text'})
FIELDS.update(PRIVACY_FIELDS)

def validate_frigate_url(value):
    if not isinstance(value, str):
        raise ValueError('Invalid Frigate URL')
    if not value:
        return ''
    parsed = urlsplit(value)
    if (parsed.scheme not in ('http', 'https') or not parsed.hostname
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('', '/')):
        raise ValueError('Frigate URL must be a base HTTP(S) URL without credentials or a path')
    return value.rstrip('/')


def _read_legacy(path):
    try:
        with open(path, encoding='utf-8') as stream:
            data=json.load(stream)
        if not isinstance(data, dict):
            raise ValueError('settings must be an object')
        return data
    except FileNotFoundError:
        return {}

async def load(hass):
    store=Store(hass, 1, KEY)
    data=await store.async_load()
    if data is None:
        data=await hass.async_add_executor_job(_read_legacy, hass.config.path('jarvis_local_settings.json'))
    if not isinstance(data, dict):
        raise ValueError('Home Voice Assistant settings must be an object')
    return data

async def save(hass, data):
    if not isinstance(data, dict) or set(data)-set(FIELDS)-{'switch_lights', 'satellite_media_players', 'music_players', 'frigate_url'}:
        raise ValueError('Invalid settings fields')
    cleaned={}
    for key, domain in FIELDS.items():
        previous=hass.data.get('declan_local', {}).get('settings', {}).get(key, '')
        value=data.get(key, previous)
        if not isinstance(value, str):
            raise ValueError('Invalid '+key)
        if value:
            allowed_domains = domain.split('|')
            unchanged = value == previous
            if not any(value.startswith(item+'.') for item in allowed_domains) or (hass.states.get(value) is None and not unchanged):
                raise ValueError('Choose an existing '+ ' or '.join(allowed_domains) +' entity for '+key)
            cleaned[key]=value
    cleaned['frigate_url'] = validate_frigate_url(data.get('frigate_url',
        hass.data.get('declan_local', {}).get('settings', {}).get('frigate_url', '')))
    mappings=data.get('switch_lights', {})
    if not isinstance(mappings, dict) or len(mappings)>50:
        raise ValueError('Invalid switch mappings')
    switches={}
    for name, entity in mappings.items():
        if not isinstance(name,str) or not name.strip() or len(name)>100 or not isinstance(entity,str) or not entity.startswith('switch.') or hass.states.get(entity) is None:
            raise ValueError('Each switch needs a name and an existing switch entity')
        name=' '.join(name.lower().split())
        if name in switches:raise ValueError('Switch names must be unique')
        switches[name]=entity
    cleaned['switch_lights']=switches
    # Older sidebar clients omit this field; preserve their existing mappings.
    players=data.get('satellite_media_players',
        hass.data.get('declan_local', {}).get('settings', {}).get('satellite_media_players', {}))
    if not isinstance(players, dict) or len(players)>50:
        raise ValueError('Invalid satellite media player mappings')
    import re
    for satellite, player in players.items():
        if (not isinstance(satellite, str) or not re.fullmatch(r'assist_satellite\.[a-z0-9_]+', satellite)
                or not isinstance(player, str) or not re.fullmatch(r'media_player\.[a-z0-9_]+', player)):
            raise ValueError('Each satellite needs an explicit media_player entity')
    previous=hass.data.get('declan_local', {}).get('settings', {}).get('satellite_media_players', {})
    for satellite, player in players.items():
        # Keep unchanged mappings even when a saved entity is temporarily missing.
        if isinstance(previous, dict) and previous.get(satellite) == player:
            continue
        if hass.states.get(satellite) is None or hass.states.get(player) is None:
            raise ValueError('Choose an existing Assist satellite and media player for each new mapping')
    cleaned['satellite_media_players']=dict(players)
    previous=hass.data.get('declan_local', {}).get('settings', {}).get('music_players', {})
    music_players=data.get('music_players', previous)
    if not isinstance(music_players, dict) or len(music_players)>100:
        raise ValueError('Invalid music destination mappings')
    cleaned_music_players={}
    for label, entity in music_players.items():
        if not isinstance(label, str) or not label.strip() or len(label)>80:
            raise ValueError('Each music destination needs a short room name')
        label=' '.join(label.casefold().split())
        if label in cleaned_music_players:
            raise ValueError('Music destination names must be unique')
        if not isinstance(entity, str) or not entity.startswith('media_player.'):
            raise ValueError('Each music destination needs a media_player entity')
        unchanged=isinstance(previous, dict) and previous.get(label)==entity
        if hass.states.get(entity) is None and not unchanged:
            raise ValueError('Choose an existing media_player for each new music destination')
        cleaned_music_players[label]=entity
    cleaned['music_players']=cleaned_music_players

    privacy_ids=[cleaned[key] for key in ('guest_mode', 'visitors_present', 'quiet_hours', 'guests_staying', 'guest_auto_enable', 'guest_away_suspend') if cleaned.get(key)]
    if len(privacy_ids) != len(set(privacy_ids)):
        raise ValueError('Guest authority, visitor presence and quiet hours need separate helpers')
    for first, second in (('guest_owner_one', 'guest_owner_two'), ('guest_names', 'guest_staying_names')):
        if cleaned.get(first) and cleaned.get(first) == cleaned.get(second):
            raise ValueError('Guest owner sensors and name helper roles must be distinct')
    controller=hass.data.get('declan_local', {}).get('guest_authority')
    if controller:
        await controller.prepare_settings(cleaned)
    await Store(hass, 1, KEY).async_save(cleaned)
    hass.data['declan_local']['settings']=cleaned
    if blacklist := hass.data['declan_local'].get('music_blacklist'):
        blacklist.refresh_destinations()

def get(hass, key, default=None):
    value=hass.data.get('declan_local', {}).get('settings', {}).get(key, default)
    if not value and key == 'thermostat':
        candidates=hass.states.async_all('climate')
        if len(candidates)==1:
            return candidates[0].entity_id
    return value
