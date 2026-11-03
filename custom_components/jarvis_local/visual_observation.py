"""Best-effort, opt-in Echo Show to Frigate recognition.

Visual observations are advisory and must not select speaker memory or authorise
commands. No image or recognition result is retained after the request.
"""
import asyncio
from pathlib import Path
from uuid import uuid4

from .frigate_faces import recognize
from .show_cameras import camera_for_satellite, capture


async def inspect_speaker_camera(hass, satellite_id, frigate_url):
    """Return a visual observation, or None when unavailable or ambiguous."""
    if not satellite_id or not frigate_url:
        return None
    camera = camera_for_satellite(hass, satellite_id)
    if camera is None:
        return None
    destination = Path(hass.config.path("declan_snapshots")) / (uuid4().hex + ".jpg")
    try:
        # Snapshot and recognition must never block voice commands indefinitely.
        async with asyncio.timeout(5):
            await capture(hass, camera, destination)
            return await recognize(hass, destination, frigate_url)
    except (Exception, asyncio.CancelledError) as error:
        if isinstance(error, asyncio.CancelledError):
            raise
        return None
    finally:
        await hass.async_add_executor_job(destination.unlink, True)
