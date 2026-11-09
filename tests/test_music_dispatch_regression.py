"""Guard against slow music dispatch and a broken Spotify session import."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'custom_components' / 'declan_local'


def test_spotify_search_initialises_ha_session():
    tree = ast.parse((ROOT / 'spotify_discovery.py').read_text())
    search = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'search')
    assert any(isinstance(n, ast.ImportFrom) and n.module == 'homeassistant.helpers.aiohttp_client'
               for n in ast.walk(search))
    assert any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'session'
               for t in n.targets) for n in ast.walk(search))


def test_music_assistant_dispatch_does_not_block_agent():
    tree = ast.parse((ROOT / 'agent.py').read_text())
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and n.func.attr == 'async_call'
             and len(n.args) >= 2 and all(isinstance(a, ast.Constant) for a in n.args[:2])
             and [a.value for a in n.args[:2]] == ['music_assistant', 'play_media']]
    assert calls
    assert all(any(k.arg == 'blocking' and isinstance(k.value, ast.Constant) and k.value.value is False
                   for k in n.keywords) for n in calls)


def test_category_dispatch_is_bounded_and_history_follows_dispatch():
    tree = ast.parse((ROOT / 'music_controller.py').read_text())
    register = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef)
                    and n.name == 'async_register')
    play = next(n for n in register.body if isinstance(n, ast.AsyncFunctionDef)
                and n.name == 'play')
    waits = [n for n in ast.walk(play) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute)
             and n.func.attr == 'wait_for']
    assert waits
    assert any(k.arg == 'timeout' and isinstance(k.value, ast.Constant)
               and k.value.value <= 3 for n in waits for k in n.keywords)
    service_calls = [n for n in ast.walk(play) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute)
                     and n.func.attr == 'async_call']
    assert any(any(k.arg == 'blocking' and isinstance(k.value, ast.Constant)
                   and k.value.value is True for k in n.keywords)
               for n in service_calls)
    source = (ROOT / 'music_controller.py').read_text()
    assert source.index('await asyncio.wait_for(', source.index('async def play(call)')) < source.index(
        'await history_store.async_save(next_history)', source.index('async def play(call)'))
