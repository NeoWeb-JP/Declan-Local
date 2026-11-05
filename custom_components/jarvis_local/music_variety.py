"""Playlist selection policy for Declan.

Pure logic: Home Assistant playback, history persistence and Spotify playlist
configuration belong to the calling integration. No API calls are made here.
"""
from __future__ import annotations

import random
from collections.abc import Mapping, Sequence


def choose_playlist(
    category: str,
    playlists: Mapping[str, Sequence[str]],
    history: Mapping[str, Sequence[str]] | None = None,
    *,
    avoid_last: int = 3,
    rng: random.Random | None = None,
) -> str:
    """Choose a configured playlist, avoiding recent selections where possible.

    If all playlists are excluded, relax the exclusion progressively so that
    the engine still plays something. Repeated playlist IDs are deduplicated.
    """
    if avoid_last < 0:
        raise ValueError("avoid_last must be non-negative")
    candidates = list(dict.fromkeys(
        uri.strip() for uri in playlists.get(category, ()) if isinstance(uri, str) and uri.strip()
    ))
    if not candidates:
        raise ValueError(f"No playlists configured for category: {category}")
    recent = list((history or {}).get(category, ()))
    excluded_count = min(avoid_last, len(recent))
    while excluded_count:
        excluded = set(recent[-excluded_count:])
        available = [uri for uri in candidates if uri not in excluded]
        if available:
            break
        excluded_count -= 1
    else:
        available = candidates
    return (rng or random.SystemRandom()).choice(available)


def updated_history(
    category: str,
    selected: str,
    history: Mapping[str, Sequence[str]] | None = None,
    *,
    max_entries: int = 20,
) -> dict[str, list[str]]:
    """Return a new bounded history mapping after successful playback.

    Call only after the media player confirms the play request was accepted.
    """
    if max_entries < 1:
        raise ValueError("max_entries must be positive")
    result = {key: list(values) for key, values in (history or {}).items()}
    result[category] = (result.get(category, []) + [selected])[-max_entries:]
    return result
