"""Spotify 429 response handling is bounded and requires no API calls."""
import importlib.util
from pathlib import Path

import pytest

path = Path(__file__).resolve().parents[1] / "custom_components/declan_local/spotify_discovery.py"
spec = importlib.util.spec_from_file_location("spotify_discovery_rate_test", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Response:
    def __init__(self, status, retry_after=None):
        self.status = status
        self.headers = {} if retry_after is None else {"Retry-After": retry_after}


def test_non_rate_limited_response_is_untouched():
    assert module.check_rate_limit(Response(200)) is None
    assert module.check_rate_limit(Response(500)) is None


@pytest.mark.parametrize(("raw", "expected"), [
    ("22", 22), ("0", 1), ("999999", 86400),
    ("invalid", 60), ("-4", 1), (None, 60),
])
def test_retry_after_is_bounded(raw, expected):
    with pytest.raises(module.SpotifyRateLimited) as caught:
        module.check_rate_limit(Response(429, raw))
    assert caught.value.retry_after == expected
