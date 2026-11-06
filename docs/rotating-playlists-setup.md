# Declan rotating playlists: Home Assistant setup

Place `declan_music_playlists.json` in `/config` on Home Assistant.
Example (replace every placeholder with a real Spotify playlist URI):

```json
{
  "country": {"playlists": ["spotify://playlist/REPLACE_1", "spotify://playlist/REPLACE_2", "spotify://playlist/REPLACE_3", "spotify://playlist/REPLACE_4"]},
  "braai": {"playlists": ["spotify://playlist/REPLACE_5", "spotify://playlist/REPLACE_6"]},
  "romantic": {"playlists": ["spotify://playlist/REPLACE_7", "spotify://playlist/REPLACE_8"]},
  "sexy_time": {"playlists": ["spotify://playlist/REPLACE_9", "spotify://playlist/REPLACE_10"]}
}
```

After deploying the integration and restarting HA, test the new service:

```yaml
action: declan_local.play_music_category
data:
  category: country
  room: everywhere
```

The same service can be used by Easy Home and Tessera action tiles.
Supported rooms are kitchen, bedroom, lounge, living room, downstairs and
everywhere. The player entities are inherited from the existing Music
Assistant voice mapping. Verify them against your live installation.

Voice: "play country music everywhere" selects a configured playlist rather
than repeating a generic Music Assistant search. "play braai music in kitchen"
works once the catalogue contains braai entries. A missing category returns a
clear service error; no unconfigured playlist is invented.

For the existing `declan_sexy_time` Home Assistant script, replace ONLY its
music playback action with:

```yaml
- action: declan_local.play_music_category
  data:
    category: sexy_time
    room: bedroom
```

Keep the rest of the Sexy Time lighting and device actions unchanged. If the
script handles both start and end, insert the action only in the start branch.

History is stored in Home Assistant storage after a successful Music Assistant
service call; this means the service accepted the request, not necessarily
that a speaker has started playing. Never commit the private catalogue or keys.
