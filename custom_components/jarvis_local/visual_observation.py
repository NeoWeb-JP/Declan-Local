"""Best-effort, opt-in Echo Show to Frigate recognition.

Visual observations are advisory and must not select speaker memory or authorise
commands. No image or recognition result is retained after the request.
"""
import asyncio
import logging
from pathlib import Path
from uuid import uuid4

from .frigate_faces import recognize
from .show_cameras import camera_for_satellite, capture


_LOGGER = logging.getLogger(__name__)


async def inspect_speaker_camera(hass, satellite_id, frigate_url):
    """Return a visual observation, or None when unavailable or ambiguous."""
    if not satellite_id or not frigate_url:
        return None
    _LOGGER.debug("Visual observation stage=camera_resolution outcome=started")
    camera = camera_for_satellite(hass, satellite_id)
    if camera is None:
        _LOGGER.debug("Visual observation stage=camera_resolution outcome=unavailable_or_ambiguous")
        return None
    destination = Path(hass.config.path("declan_snapshots")) / (uuid4().hex + ".jpg")
    stage = "snapshot"
    try:
        # Snapshot and recognition must never block voice commands indefinitely.
        async with asyncio.timeout(5):
            await capture(hass, camera, destination)
            _LOGGER.debug("Visual observation stage=snapshot outcome=complete")
            stage = "recognition"
            result = await recognize(hass, destination, frigate_url)
            outcome = "advisory_match" if result.name else "no_approved_match"
            _LOGGER.debug("Visual observation stage=recognition outcome=%s", outcome)
            return result
    except (Exception, asyncio.CancelledError) as error:
        if isinstance(error, asyncio.CancelledError):
            _LOGGER.debug("Visual observation stage=%s outcome=cancelled", stage)
            raise
        outcome = "timeout" if isinstance(error, TimeoutError) else "failed"
        _LOGGER.debug("Visual observation stage=%s outcome=%s", stage, outcome)
        return None
    finally:
        try:
            await hass.async_add_executor_job(destination.unlink, True)
            _LOGGER.debug("Visual observation stage=cleanup outcome=complete")
        except OSError:
            _LOGGER.warning("Visual observation stage=cleanup outcome=failed")
