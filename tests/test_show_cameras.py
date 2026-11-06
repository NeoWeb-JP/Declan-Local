"""Tests for Echo Show camera discovery and conservative routing."""
import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest

from custom_components.declan_local import show_cameras as sc


def test_three_existing_cameras_have_explicit_references():
    assert sc.KNOWN_CAMERA_REGISTRY_IDS["kitchen"] == "71bf6fb2c44c5cb131e72b68e9333c45"
    assert sc.KNOWN_CAMERA_REGISTRY_IDS["lounge"] == "24246c6c9354f59ee207d0aa954ee6bb"
    assert sc.BEDROOM_CAMERA.startswith("camera.")


def test_device_match_precedes_area_match(monkeypatch):
    satellite = SimpleNamespace(device_id="device-a", area_id="kitchen")
    monkeypatch.setattr(sc.er, "async_get", lambda hass: SimpleNamespace(async_get=lambda entity: satellite))
    monkeypatch.setattr(sc.dr, "async_get", lambda hass: SimpleNamespace(async_get=lambda device: SimpleNamespace(area_id="kitchen")))
    cameras = {
        "camera.a": sc.ShowCamera("camera.a", "device-a", "kitchen"),
        "camera.b": sc.ShowCamera("camera.b", "device-b", "kitchen"),
    }
    assert sc.camera_for_satellite(object(), "assist_satellite.a", cameras).entity_id == "camera.a"


def test_ambiguous_device_match_fails_closed(monkeypatch):
    satellite = SimpleNamespace(device_id="device-a", area_id="kitchen")
    monkeypatch.setattr(sc.er, "async_get", lambda hass: SimpleNamespace(async_get=lambda entity: satellite))
    monkeypatch.setattr(sc.dr, "async_get", lambda hass: SimpleNamespace(async_get=lambda device: SimpleNamespace(area_id="kitchen")))
    cameras = {
        "camera.a": sc.ShowCamera("camera.a", "device-a", "kitchen"),
        "camera.b": sc.ShowCamera("camera.b", "device-a", "kitchen"),
    }
    assert sc.camera_for_satellite(object(), "assist_satellite.a", cameras) is None


def test_snapshot_rejects_outside_private_directory(tmp_path):
    hass = SimpleNamespace(config=SimpleNamespace(path=lambda path: str(tmp_path / path)))
    camera = sc.ShowCamera("camera.a", None, None)
    with pytest.raises(ValueError):
        asyncio.run(sc.capture(hass, camera, tmp_path / "outside.jpg"))


def test_snapshot_invokes_camera_service(tmp_path):
    service = MagicMock()
    service.async_call = __import__("unittest.mock", fromlist=["AsyncMock"]).AsyncMock()
    hass = SimpleNamespace(config=SimpleNamespace(path=lambda path: str(tmp_path / path)), services=service, async_add_executor_job=lambda func, *args: __import__("asyncio").to_thread(func, *args))
    camera = sc.ShowCamera("camera.a", None, None)
    destination = tmp_path / "declan_snapshots" / "temporary.jpg"
    result = asyncio.run(sc.capture(hass, camera, destination))
    assert result == destination
    service.async_call.assert_awaited_once()
