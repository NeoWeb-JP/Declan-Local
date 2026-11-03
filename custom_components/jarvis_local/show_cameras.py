"""EchoLocal camera discovery and opt-in, ephemeral snapshot capture.

Camera presence is not evidence of speaker identity. Never use a face match
for authorisation or attach it to a transcript without independent verification.
"""
from dataclasses import dataclass
from pathlib import Path
import re

from homeassistant.helpers import entity_registry as er, device_registry as dr

DOMAIN = "jarvis_local"
# Entity-registry IDs supplied by the owner, not camera entity IDs.
KNOWN_CAMERA_REGISTRY_IDS = {
    "kitchen": "71bf6fb2c44c5cb131e72b68e9333c45",
    "lounge": "24246c6c9354f59ee207d0aa954ee6bb",
}
BEDROOM_CAMERA = "camera.master_bedroom_master_bedroom_echo_show_camera_camera"


@dataclass(frozen=True)
class ShowCamera:
    entity_id: str
    device_id: str | None
    area_id: str | None


def discover(hass):
    """Return eligible cameras, keyed by entity ID, without a device-count limit."""
    registry = er.async_get(hass)
    devices = dr.async_get(hass)
    known_ids = set(KNOWN_CAMERA_REGISTRY_IDS.values())
    found = {}
    for entry in registry.entities.values():
        if entry.domain != "camera" or entry.disabled_by is not None:
            continue
        device = devices.async_get(entry.device_id) if entry.device_id else None
        platform = (entry.platform or "").casefold()
        identifiers = str(getattr(device, "identifiers", "")).casefold()
        eligible = (
            entry.entity_id == BEDROOM_CAMERA
            or entry.id in known_ids
            or "echolocal" in platform
            or "echolocal" in identifiers
        )
        if not eligible:
            continue
        state = hass.states.get(entry.entity_id)
        if state is None or state.state in ("unavailable", "unknown"):
            continue
        found[entry.entity_id] = ShowCamera(
            entry.entity_id, entry.device_id,
            entry.area_id or (device.area_id if device else None),
        )
    return found


def camera_for_satellite(hass, satellite_entity_id, cameras=None):
    """Match via shared HA device first, then unique area; fail closed on ambiguity."""
    cameras = discover(hass) if cameras is None else cameras
    registry = er.async_get(hass)
    satellite = registry.async_get(satellite_entity_id)
    if satellite is None:
        return None
    device = dr.async_get(hass).async_get(satellite.device_id) if satellite.device_id else None
    area = satellite.area_id or (device.area_id if device else None)
    by_device = [c for c in cameras.values() if c.device_id and c.device_id == satellite.device_id]
    if len(by_device) == 1:
        return by_device[0]
    if len(by_device) > 1:
        return None
    by_area = [c for c in cameras.values() if area and c.area_id == area]
    return by_area[0] if len(by_area) == 1 else None


async def capture(hass, camera, destination):
    """Explicit capture only; caller owns prompt deletion of temporary image."""
    path = Path(destination).resolve()
    root = Path(hass.config.path("declan_snapshots")).resolve()
    if path.parent != root or path.suffix.lower() not in (".jpg", ".jpeg"):
        raise ValueError("Snapshot destination must be a JPEG in the private Declan snapshot directory")
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", path.name):
        raise ValueError("Invalid snapshot filename")
    await hass.async_add_executor_job(root.mkdir, 0o700, True, True)
    try:
        await hass.services.async_call(
            "camera", "snapshot",
            {"entity_id": camera.entity_id, "filename": str(path)},
            blocking=True,
        )
        return path
    except Exception:
        path.unlink(missing_ok=True)
        raise
