"""Isolated behavioral coverage for optional camera observation."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch


def load_observation():
    root = Path(__file__).resolve().parents[1] / "custom_components" / "declan_local"
    package = "_visual_test"
    modules = {
        package: types.ModuleType(package),
        package + ".frigate_faces": types.SimpleNamespace(recognize=AsyncMock()),
        package + ".show_cameras": types.SimpleNamespace(
            camera_for_satellite=Mock(), capture=AsyncMock()),
    }
    spec = importlib.util.spec_from_file_location(package + ".visual_observation", root / "visual_observation.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class VisualObservation(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.module = load_observation()
        self.hass = types.SimpleNamespace(
            config=types.SimpleNamespace(path=lambda name: str(Path("/private") / name)),
            async_add_executor_job=AsyncMock(),
        )

    async def test_registry_failure_is_optional(self):
        self.module.camera_for_satellite.side_effect = RuntimeError("private registry details")
        self.assertIsNone(await self.module.inspect_speaker_camera(self.hass, "satellite", "http://frigate"))
        self.module.capture.assert_not_awaited()
        self.hass.async_add_executor_job.assert_not_awaited()

    async def test_ambiguous_camera_skips_snapshot(self):
        self.module.camera_for_satellite.return_value = None
        self.assertIsNone(await self.module.inspect_speaker_camera(self.hass, "satellite", "http://frigate"))
        self.module.capture.assert_not_awaited()
        self.hass.async_add_executor_job.assert_not_awaited()

    async def test_snapshot_and_recognition_failures_cleanup(self):
        for stage, error in (("capture", RuntimeError("snapshot failure")),
                             ("recognize", TimeoutError("recognition timeout"))):
            with self.subTest(stage=stage):
                self.setUp()
                getattr(self.module, stage).side_effect = error
                self.assertIsNone(await self.module.inspect_speaker_camera(self.hass, "satellite", "http://frigate"))
                self.hass.async_add_executor_job.assert_awaited_once()
                if stage == "capture":
                    self.module.recognize.assert_not_awaited()

    async def test_cancellation_propagates_and_cleans_up(self):
        self.module.capture.side_effect = asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await self.module.inspect_speaker_camera(self.hass, "satellite", "http://frigate")
        self.hass.async_add_executor_job.assert_awaited_once()

    async def test_success_returns_only_advisory_result_and_cleans_up(self):
        expected = types.SimpleNamespace(name="Jaco")
        self.module.recognize.return_value = expected
        self.assertIs(await self.module.inspect_speaker_camera(self.hass, "satellite", "http://frigate"), expected)
        self.hass.async_add_executor_job.assert_awaited_once()
