"""Spotify playlist discovery and category curation without AI processing."""
import base64
import json
import re

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

QUERIES = {
    "country": ("country music", "modern country"),
    "braai": ("braai music", "south african braai"),
    "romantic": ("romantic songs", "love songs"),
    "sexy_time": ("romantic evening", "slow romantic"),
    "rock": ("classic rock", "rock anthems"),
    "afrikaans": ("afrikaans treffers", "afrikaans musiek"),
    "80s": ("80s hits", "best of the 80s"),
    "90s": ("90s hits", "best of the 90s"),
    "work_focus": ("deep focus instrumental", "music for concentration"),
    "adhd_focus": ("adhd focus music", "adhd concentration instrumental"),
    "massage": ("relaxing massage music", "spa massage instrumental"),
}
MAX_PLAYLISTS = 25


def uri(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"spotify(?::|://)playlist[:/]([A-Za-z0-9]{22})", value.strip())
    if not match:
        match = re.fullmatch(r"https://open\.spotify\.com/playlist/([A-Za-z0-9]{22})(?:\?[^#]*)?", value.strip())
    return "spotify://playlist/" + match.group(1) if match else None


def curate(existing, discovered, capacity=MAX_PLAYLISTS):
    """Exclusions override pins; pins survive refresh; discovery stays capped."""
    if not 1 <= capacity <= MAX_PLAYLISTS:
        raise ValueError("Invalid playlist capacity")
    output = {}
    for category in QUERIES:
        previous = existing.get(category, {}) if isinstance(existing, dict) else {}
        previous = previous if isinstance(previous, dict) else {}
        excluded = list(dict.fromkeys(x for x in map(uri, previous.get("excluded", [])) if x))
        banned = set(excluded)
        favourites = list(dict.fromkeys(x for x in map(uri, previous.get("favourites", [])) if x and x not in banned))
        candidates = list(dict.fromkeys(x for x in map(uri, discovered.get(category, [])) if x and x not in banned and x not in favourites))
        discovered_now = candidates[:max(0, capacity - len(favourites))]
        output[category] = {"favourites": favourites, "excluded": excluded,
                            "discovered": discovered_now, "playlists": favourites + discovered_now}
    return output


async def credentials(hass):
    def read():
        with open(hass.config.path("declan_spotify_credentials.json"), encoding="utf-8") as stream:
            data = json.load(stream)
        return data["client_id"], data["client_secret"]
    return await hass.async_add_executor_job(read)


async def search(hass, client_id, client_secret):
    """Fetch up to 10 results per search; abort on API errors."""
    session = async_get_clientsession(hass)
    timeout = aiohttp.ClientTimeout(total=20)
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    async with session.post("https://accounts.spotify.com/api/token",
                            data={"grant_type": "client_credentials"},
                            headers={"Authorization": "Basic " + basic}, timeout=timeout) as response:
        response.raise_for_status()
        token = (await response.json())["access_token"]
    result = {}
    for category, terms in QUERIES.items():
        found = []
        for term in terms:
            async with session.get("https://api.spotify.com/v1/search",
                                   params={"q": term, "type": "playlist", "limit": 10},
                                   headers={"Authorization": "Bearer " + token}, timeout=timeout) as response:
                response.raise_for_status()
                payload = await response.json()
            for item in (payload.get("playlists") or {}).get("items") or []:
                if isinstance(item, dict):
                    candidate = uri(item.get("uri"))
                    if candidate and candidate not in found:
                        found.append(candidate)
        result[category] = found
    return result
