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


def test_remote_discovery_does_not_hold_playback_lock():
    tree = ast.parse(SOURCE)
    register = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef)
                    and n.name == "async_register")
    refresh = next(n for n in register.body if isinstance(n, ast.AsyncFunctionDef)
                   and n.name == "refresh")
    remote_calls = [n for n in ast.walk(refresh) if isinstance(n, ast.Await)
                    and isinstance(n.value, ast.Call)
                    and isinstance(n.value.func, ast.Name)
                    and n.value.func.id in ("credentials", "search")]
    assert len(remote_calls) == 2
    for call in remote_calls:
        assert any(isinstance(n, ast.AsyncWith)
                   and any(isinstance(item.context_expr, ast.Name)
                           and item.context_expr.id == "refresh_lock"
                           for item in n.items)
                   for n in refresh.body)
        assert all(not (isinstance(n, ast.AsyncWith)
                        and any(isinstance(item.context_expr, ast.Name)
                                and item.context_expr.id == "lock"
                                for item in n.items)
                        and any(descendant is call for descendant in ast.walk(n)))
                   for n in ast.walk(refresh))


def test_music_timings_exclude_playlist_identifiers():
    assert "selection_ms=%d dispatch_ms=%d" in SOURCE
    assert "category, room, selection_ms" in SOURCE
