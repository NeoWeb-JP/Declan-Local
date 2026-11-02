"""Isolated catalogue choice regression tests (no network)."""
import ast
import asyncio
from pathlib import Path

def test_title_choices():
    source = Path("custom_components/jarvis_local/media_search_adapters.py").read_text()
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "search_streaming")
    calls = []
    async def api(hass, token, path, params=None):
        calls.append(path)
        if path == "search/multi":
            return {"results": [
                {"id": 1, "media_type": "tv", "name": "The Simpsons", "first_air_date": "1989-12-17"},
                {"id": 2, "media_type": "movie", "title": "The Simpsons Movie", "release_date": "2007-07-27"}]}
        return {"results": {"GB": {"flatrate": [{"provider_name": "Disney Plus"}]}}}
    ns = {"current": lambda _: {"tmdb_token": "test", "subscriptions": ["disney"]},
          "_tmdb_json": api, "title_match": lambda q, t: "exact" if q == t else "possible",
          "_provider_key": lambda _: "disney", "_watch_link": lambda _: None,
          "SUBSCRIPTIONS": {"disney": "Disney+"}}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<probe>", "exec"), ns)
    async def run():
        report = await ns[fn.name](None, "Simpsons", None)
        assert report["status"] == "ambiguous"
        assert [c["id"] for c in report["choices"]] == [1, 2]
        assert calls == ["search/multi"]
        report = await ns[fn.name](None, "The Simpsons", None, {"id": 1, "kind": "tv"})
        assert report["matches"][0]["selected_subscriptions"] == ["Disney Plus"]
        assert calls[-1] == "tv/1/watch/providers"
        report = await ns[fn.name](None, "The Simpsons", None, {"id": 999, "kind": "tv"})
        assert report["matches"] == []
    # All API awaits are immediate stubs; drive without a network event loop.
    try:
        run().send(None)
    except StopIteration:
        pass

if __name__ == "__main__":
    test_title_choices()
    print("Title choice and selected provider lookup passed.")
