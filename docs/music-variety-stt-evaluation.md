# Declan music variety and STT comparison

## Music selection (phase 1)

The pure selection policy is in `custom_components/declan_local/music_variety.py`.
It takes category-to-playlist mappings and per-category recent history; it does
not call Spotify, Music Assistant, or Home Assistant. Use a private local config
for real Spotify URIs. Do not commit household playlists or credentials.

**Integration remaining:** identify the existing music intent handler and
Music Assistant target entities, wire selection before play_media, persist
history only after accepted playback, and route Sexy Time and dashboard actions
through the same service. Keep existing playback unchanged until validated.

## STT comparison (phase 2)

Current baseline: local Whisper through the HA Assist pipeline. Keep it active.

1. With consent, record a representative set of short test utterances from
   both household speakers, including difficult device names, room controls,
   music categories, corrections, silence, TV audio and wake-word mistakes.
2. Save expected transcripts separately. Redact private audio and avoid
   committing recordings, API keys or transcripts to the repository.
3. Replay identical clips against current local Whisper and a configurable
   cloud candidate (GPT Transcribe or Deepgram). Do not send clips to a cloud
   provider until the household explicitly approves the privacy trade-off.
4. Measure word error rate, exact-command accuracy, false command activations,
   median and p95 latency, and billed audio duration.
5. Select a replacement only if command accuracy improves substantially without
   unacceptable latency or monthly cost. Add safe rejection of low-confidence
   intents independently of the STT provider.

A STT provider swap cannot alone fix erroneous wake-word detection or intent
routing. Diagnose these separately using the Assist pipeline traces.
