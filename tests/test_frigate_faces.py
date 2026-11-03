"""Pure Frigate response parsing tests; no Frigate service required."""
from custom_components.jarvis_local.frigate_faces import FaceResult, parse_result


def test_known_faces_above_threshold():
    assert parse_result({"success": True, "face_name": "jaco", "score": 0.95}) == FaceResult("Jaco", 0.95)
    assert parse_result({"success": True, "face_name": "Edd", "score": 0.91}) == FaceResult("Edd", 0.91)


def test_unknown_and_low_confidence_fail_closed():
    assert parse_result({"success": True, "face_name": "Mike", "score": 0.99}).name is None
    assert parse_result({"success": True, "face_name": "Jaco", "score": 0.89}).name is None
    assert parse_result({"success": False, "face_name": "Edd", "score": 0.99}).name is None


def test_invalid_scores_fail_closed():
    for score in (None, True, -1, 2, float("nan"), "0.99"):
        assert parse_result({"success": True, "face_name": "Jaco", "score": score}).name is None
