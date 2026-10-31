"""Read-only information dialogue. Remember topics, never measured values."""
import asyncio
from datetime import datetime, timedelta, timezone
import math
import re
from zoneinfo import ZoneInfo
from homeassistant.exceptions import HomeAssistantError
from .settings import get
from .status import answer
FORECAST_TIMEOUT = 10

WEATHER = {"what's the weather", "what is the weather", "what's the weather like",
           "what is the weather like", "how's the weather", "how is the weather",
           "tell me the weather", "weather", "weather please"}
INDOOR = {"what's the temperature", "what is the temperature", "what's the temperature inside",
          "what is the temperature inside", "what's the temperature in the house",
          "what is the temperature in the house", "how warm is it", "how warm is the house",
          "what's the indoor temperature"}
OUTDOOR = {"what's the temperature outside", "what is the temperature outside", "how cold is it outside",
           "how warm is it outside", "what's the outdoor temperature", "outside temperature"}
TIME = {"what time is it", "what's the time", "tell me the time", "what is the time", "time please"}
CONDITIONS = {'clear-night':'clear', 'cloudy':'cloudy', 'fog':'foggy', 'hail':'hail',
              'lightning':'thunderstorms', 'lightning-rainy':'thunderstorms with rain',
              'partlycloudy':'partly cloudy', 'pouring':'heavy rain', 'rainy':'rain',
              'snowy':'snow', 'snowy-rainy':'sleet', 'sunny':'sunny',
              'windy':'windy', 'windy-variant':'windy and cloudy', 'exceptional':'exceptional conditions'}


def parse(text, previous=None):
    text = text.lower().replace('’', "'").strip()
    preview = False
    for prefix in ('preview ', 'dry run ', 'what would you do if i said '):
        if text.startswith(prefix):
            preview, text = True, text[len(prefix):]
            break
    text = re.sub(r"[?.,!]", "", text).strip()
    text = re.sub(r'\s+(?:declan|jarvis)$', '', text)
    period = None
    topic = None
    followup = False
    query = None
    if text in WEATHER: topic, query = 'weather', text
    elif text in INDOOR: topic, query = 'temperature', text
    elif text in OUTDOOR: topic, query = 'temperature', text
    elif text in TIME: topic, query = 'time', text
    else:
        match = re.fullmatch(r"(?:(?:what(?:'s| is)|how(?:'s| is)|tell me|what about) )?(?:the )?(weather|temperature)(?: forecast| like)?(?: for)? (tomorrow|later(?: today)?|today)", text)
        if match:
            topic, period = match[1], match[2]
        else:
            match = re.fullmatch(r"(?:and |what about )?(tomorrow|outside|later(?: today)?)", text)
            if not match:
                return None
            followup = True
            if previous not in {'weather', 'temperature'}:
                return {'kind':'information', 'clarify':True, 'preview':preview,
                        'label':'clarify the information topic', 'followup':True}
            topic, period = previous, match[1]
            if period == 'outside':
                query = "what's the temperature outside" if topic == 'temperature' else "what's the weather"
                period = None
    if period == 'today':
        query = "what's the weather"
        period = None
    request = {'kind':'information', 'topic':topic, 'period':period,
               'query':query, 'preview':preview, 'followup':followup,
               'label':('read '+topic+' forecast for '+period if period else 'read current '+topic)}
    return request


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def select_forecast(entries, period, now):
    valid = []
    for entry in entries[:1000]:
        if not isinstance(entry, dict) or not isinstance(entry.get('datetime'), str):
            continue
        try:
            at = datetime.fromisoformat(entry['datetime'].replace('Z', '+00:00'))
            if at.tzinfo is None:
                continue
            at = at.astimezone(now.tzinfo)
        except (ValueError, OverflowError):
            continue
        if period == 'tomorrow':
            matches = at.date() == (now + timedelta(days=1)).date()
        else:
            matches = now.astimezone(timezone.utc) < at.astimezone(timezone.utc) <= now.astimezone(timezone.utc) + timedelta(hours=6)
        if matches:
            valid.append((at, entry))
    return min(valid, key=lambda item:item[0].astimezone(timezone.utc)) if valid else None


async def read(hass, request, context=None, now=None):
    if request.get('clarify'):
        return 'Were you asking about the weather or the temperature?', False
    if not request.get('period'):
        response = answer(hass, request['query'])
        available = bool(response) and 'unavailable' not in response.lower() and not response.startswith('Choose ')
        return response, available
    entity_id = get(hass, 'weather')
    state = hass.states.get(entity_id) if entity_id else None
    if not isinstance(entity_id, str) or not entity_id.startswith('weather.') or not state or state.state in {'unknown','unavailable'}:
        return 'The configured weather forecast is unavailable.', False
    kind = 'daily' if request['period'] == 'tomorrow' else 'hourly'
    try:
        async with asyncio.timeout(FORECAST_TIMEOUT):
            result = await hass.services.async_call('weather', 'get_forecasts',
                {'entity_id':entity_id, 'type':kind}, blocking=True,
                return_response=True, context=context)
    except (HomeAssistantError, ValueError, OSError, TimeoutError):
        return 'The requested weather forecast is unavailable.', False
    payload = result.get(entity_id) if isinstance(result, dict) else None
    entries = payload.get('forecast') if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return 'The requested weather forecast is unavailable.', False
    if now is None:
        now = datetime.now(timezone.utc).astimezone(ZoneInfo(hass.config.time_zone))
    selected = select_forecast(entries, request['period'], now)
    if selected is None:
        return 'No forecast is available for that period.', False
    at, forecast = selected
    condition_key = forecast.get('condition')
    condition = CONDITIONS.get(condition_key) if isinstance(condition_key,str) else None
    high, low = forecast.get('temperature'), forecast.get('templow')
    unit = state.attributes.get('temperature_unit') or hass.config.units.temperature_unit
    parts = []
    if condition: parts.append(condition)
    if numeric(high):
        if kind == 'daily' and numeric(low) and low <= high:
            parts.append(f'{low:g} to {high:g} {unit}')
        else:
            parts.append(('up to ' if kind == 'daily' else '') + f'{high:g} {unit}')
    if not parts:
        return 'The requested forecast has no usable conditions or temperature.', False
    label = 'Tomorrow' if request['period'] == 'tomorrow' else 'At ' + at.strftime('%I:%M %p').lstrip('0')
    if request['topic'] == 'temperature':
        label = label + ' outdoors'
    return label + ', the forecast is ' + ', '.join(parts) + '.', True
