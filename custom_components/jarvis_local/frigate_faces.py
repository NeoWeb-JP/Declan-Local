"""Optional local Frigate face recognition client.

Recognition is advisory only. A face match does not establish speaker identity.
No camera images, credentials, or response bodies are logged or persisted here.
"""
import asyncio
from dataclasses import dataclass
import math
from urllib.parse import urlsplit

import aiohttp

ALLOWED = {"jaco": "Jaco", "edd": "Edd"}
MIN_SCORE = 0.90
MAX_IMAGE_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class FaceResult:
    name: str | None
    score: float | None


def parse_result(payload, minimum=MIN_SCORE):
    """Reject malformed, ambiguous or unapproved Frigate responses."""
    if not isinstance(payload, dict) or payload.get("success") is not True:
        return FaceResult(None, None)
    name = payload.get("face_name")
    score = payload.get("score")
    if (not isinstance(name, str) or isinstance(score, bool)
            or not isinstance(score, (float, int)) or not math.isfinite(score)
            or not 0 <= score <= 1):
        return FaceResult(None, None)
    recognised = ALLOWED.get(name.strip().casefold())
    if recognised is None or score < minimum:
        return FaceResult(None, float(score))
    return FaceResult(recognised, float(score))


async def recognize(hass, image_path, base_url, token=None, timeout=3.0):
    """Submit a temporary JPEG to a trusted local Frigate endpoint.

    Use Frigate's authenticated HTTPS reverse proxy with a scoped credential
    when available. Do not configure an untrusted/public endpoint.
    """
    parsed = urlsplit(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
        raise ValueError("Invalid Frigate base URL")
    if not (0 < timeout <= 10):
        raise ValueError("Invalid timeout")
    path = str(image_path)
    def read_image():
        with open(path, "rb") as file:
            image = file.read(MAX_IMAGE_BYTES + 1)
        if not image or len(image) > MAX_IMAGE_BYTES:
            raise ValueError("Invalid snapshot size")
        return image
    image = await hass.async_add_executor_job(read_image)
    form = aiohttp.FormData()
    form.add_field("file", image, filename="snapshot.jpg", content_type="image/jpeg")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = base_url.rstrip("/") + "/api/faces/recognize"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout), trust_env=False) as session:
        async with session.post(url, data=form, headers=headers, allow_redirects=False) as response:
            response.raise_for_status()
            return parse_result(await response.json(content_type="application/json"))
