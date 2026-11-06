"""Pipeline diagnostics must be useful without leaking camera or face data."""
import asyncio
import importlib.util
import logging
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.declan_local.frigate_faces import FaceResult


@pytest.mark.parametrize("failure", [None, "snapshot", "recognition", "timeout", "cancelled"])
def test_private_diagnostics_and_cleanup(tmp_path, monkeypatch, caplog, failure):
    # Isolate HA routing imports; exercise the real orchestration and filesystem.
    stub = ModuleType("custom_components.declan_local.show_cameras")
    stub.camera_for_satellite = lambda *args: object()
    destination = None

    async def capture(*args):
        nonlocal destination
        destination = args[-1]
        destination.parent.mkdir(exist_ok=True)
        destination.write_bytes(b"private-image")
        if failure == "snapshot":
            raise RuntimeError("secret-camera-url")

    stub.capture = capture
    monkeypatch.setitem(sys.modules, stub.__name__, stub)
    path = Path(__file__).parents[1] / "custom_components/declan_local/visual_observation.py"
    spec = importlib.util.spec_from_file_location("custom_components.declan_local._visual_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    error = {"recognition": RuntimeError("secret-token"), "timeout": TimeoutError(), "cancelled": asyncio.CancelledError()}.get(failure)
    module.recognize = AsyncMock(side_effect=error, return_value=FaceResult("Jaco", 0.86))

    async def executor(func, *args):
        return func(*args)

    hass = SimpleNamespace(config=SimpleNamespace(path=lambda part: str(tmp_path / part)), async_add_executor_job=executor)
    caplog.set_level(logging.DEBUG, logger=module.__name__)
    if failure == "cancelled":
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(module.inspect_speaker_camera(hass, "private-satellite", "private-url"))
    else:
        result = asyncio.run(module.inspect_speaker_camera(hass, "private-satellite", "private-url"))
        assert result == (FaceResult("Jaco", 0.86) if failure is None else None)
    assert destination is not None and not destination.exists()
    assert "stage=cleanup outcome=complete" in caplog.text
    for secret in ("Jaco", "0.86", "private-image", "secret-token", "secret-camera-url", "private-satellite", "private-url", str(destination)):
        assert secret not in caplog.text
    if failure == "snapshot":
        module.recognize.assert_not_awaited()


def test_pipeline_does_not_import_identity_or_permission_modules():
    import ast
    path = Path(__file__).parents[1] / "custom_components/declan_local/visual_observation.py"
    tree = ast.parse(path.read_text())
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not imports.intersection({"speaker_identity", "conversation_memory", "guest_authority"})
