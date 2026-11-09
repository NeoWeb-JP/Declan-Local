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


def test_category_dispatch_does_not_hold_shared_cache_lock():
    tree = ast.parse(SOURCE)
    register = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef)
                    and n.name == "async_register")
    play = next(n for n in register.body if isinstance(n, ast.AsyncFunctionDef)
                and n.name == "play")
    category_scope = next(n for n in ast.walk(play) if isinstance(n, ast.AsyncWith)
                          and any(isinstance(item.context_expr, ast.Subscript)
                                  and isinstance(item.context_expr.value, ast.Name)
                                  and item.context_expr.value.id == "category_locks"
                                  for item in n.items))
    dispatches = [n for n in ast.walk(category_scope)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                  and n.func.attr == "async_call"]
    assert len(dispatches) == 1
    shared_scopes = [n for n in ast.walk(category_scope) if isinstance(n, ast.AsyncWith)
                     and any(isinstance(item.context_expr, ast.Name)
                             and item.context_expr.id == "lock" for item in n.items)]
    assert len(shared_scopes) == 2
    assert all(not any(call is child for child in ast.walk(scope))
               for scope in shared_scopes for call in dispatches)
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == "updated_history" for n in ast.walk(shared_scopes[-1]))


def test_discovery_cooldown_preserves_catalogue_and_skips_requests():
    assert "except SpotifyRateLimited as exc:" in SOURCE
    assert "discovery_retry_at = monotonic() + exc.retry_after" in SOURCE
    assert "if monotonic() < discovery_retry_at:" in SOURCE
    assert "return" in SOURCE.split("if monotonic() < discovery_retry_at:", 1)[1].split("try:", 1)[0]
    assert "cached_catalogue = updated" in SOURCE


def test_dispatch_outcomes_are_reported_without_playlist_identifiers():
    assert SOURCE.count('hass.bus.async_fire("declan_music_dispatch"') == 3
    assert '"status": "accepted"' in SOURCE
    assert '"status": "failed"' in SOURCE
    assert '"status": "unknown_timeout"' in SOURCE
    for line in SOURCE.splitlines():
        if 'hass.bus.async_fire("declan_music_dispatch"' in line:
            assert '"category": category' in line
            assert '"room": room' in line
            assert 'selected' not in line


def test_player_observation_is_nonblocking_and_does_not_claim_playlist_verified():
    tree = ast.parse(SOURCE)
    register = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef)
                    and n.name == "async_register")
    observe = next(n for n in register.body if isinstance(n, ast.AsyncFunctionDef)
                   and n.name == "observe_player")
    assert any(isinstance(n, ast.Compare) and isinstance(n.left, ast.Attribute)
               and n.left.attr == "state" for n in ast.walk(observe))
    assert '"player_started"' in SOURCE
    assert '"already_playing"' in SOURCE
    assert '"status": "unconfirmed"' in SOURCE
    assert "hass.async_create_task(observe_player(category, room, entity, was_playing))" in SOURCE
    assert "playlist_verified" not in SOURCE


def test_playback_observation_captures_baseline_before_dispatch():
    assert 'was_playing = state.state == "playing"' in SOURCE
    assert 'status = "already_playing" if was_playing else "player_started"' in SOURCE
