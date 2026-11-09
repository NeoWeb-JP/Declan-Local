"""Regression checks for fast cached category playback and weekly refresh."""
import ast
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] /
          "custom_components/declan_local/music_controller.py").read_text()


def test_cache_is_initialised_and_read_before_storage():
    tree = ast.parse(SOURCE)
    register = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef)
                    and n.name == "async_register")
    functions = {n.name: n for n in register.body if isinstance(n, ast.AsyncFunctionDef)}
    load = functions["load"]
    assert any(isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
               and isinstance(n.test.left, ast.Name)
               and n.test.left.id == "cached_catalogue" for n in load.body)
    assert "cached_history is None" in SOURCE
    assert "cached_weights is None" in SOURCE


def test_refresh_and_edits_invalidate_cached_values():
    assert "cached_catalogue = updated" in SOURCE
    assert "cached_catalogue = catalogue" in SOURCE
    assert "cached_weights = weights" in SOURCE
    assert "cached_history = next_history" in SOURCE


def test_weekly_refresh_is_preserved():
    assert "async_track_time_interval(hass, scheduled_refresh, timedelta(days=7))" in SOURCE
