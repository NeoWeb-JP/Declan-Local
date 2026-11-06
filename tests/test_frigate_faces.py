"""Pure Frigate response parsing tests; no Frigate service required."""
from custom_components.declan_local.frigate_faces import FaceResult, parse_result


def test_known_faces_above_threshold():
    assert parse_result({"success": True, "face_name": "jaco", "score": 0.95}) == FaceResult("Jaco", 0.95)
    assert parse_result({"success": True, "face_name": "Edd", "score": 0.91}) == FaceResult("Edd", 0.91)


def test_unknown_and_low_confidence_fail_closed():
    assert parse_result({"success": True, "face_name": "Mike", "score": 0.99}).name is None
    assert parse_result({"success": True, "face_name": "Jaco", "score": 0.79}).name is None
    assert parse_result({"success": False, "face_name": "Edd", "score": 0.99}).name is None


def test_invalid_scores_fail_closed():
    for score in (None, True, -1, 2, float("nan"), "invalid"):
        assert parse_result({"success": True, "face_name": "Jaco", "score": score}).name is None


def test_module_import_and_parser_without_aiohttp():
    """A fresh module import must work when the HTTP dependency is absent."""
    from pathlib import Path
    import subprocess
    import sys

    module_path = Path(__file__).resolve().parents[1] / "custom_components" / "declan_local" / "frigate_faces.py"
    script = """
import builtins
import importlib.util
import sys
original_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name == "aiohttp" or name.startswith("aiohttp."):
        raise ModuleNotFoundError("aiohttp intentionally unavailable")
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
spec = importlib.util.spec_from_file_location("isolated_frigate", sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
assert module.parse_result({"success": True, "face_name": "jaco", "score": 0.95}).name == "Jaco"
"""
    subprocess.run([sys.executable, "-c", script, str(module_path)], check=True)


def test_numeric_and_string_scores_and_boundaries():
    for score in (0.86, "0.86", 0.80, "0.80", 1, "1"):
        assert parse_result({"success": True, "face_name": "Jaco", "score": score}) == FaceResult("Jaco", float(score))
    for score in (0, "0", 0.799999, "0.799999"):
        assert parse_result({"success": True, "face_name": "Jaco", "score": score}) == FaceResult(None, float(score))


def test_invalid_and_nonfinite_scores():
    for score in (False, [], {}, "", "bad", "NaN", "inf", "-inf", "1e999", float("inf"), float("-inf"), "-0.01", "1.01", 10**1000):
        assert parse_result({"success": True, "face_name": "Jaco", "score": score}) == FaceResult(None, None)


def test_invalid_thresholds_fail_closed():
    for minimum in (True, "0.8", None, -1, 2, float("nan"), float("inf")):
        assert parse_result({"success": True, "face_name": "Jaco", "score": "0.86"}, minimum) == FaceResult(None, None)
