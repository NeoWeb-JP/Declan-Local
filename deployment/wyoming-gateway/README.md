# Declan Wyoming speaker gateway (LXC 107)

This is a **test candidate**, not a production deployment. It proxies Wyoming
PCM audio from port **10301** to the existing faster-whisper service at
**10300** and emits a private \`jarvis-speaker\` event immediately before
the normal Wyoming \`Transcript\` event.

## Safety and limitations

- LXC 107's existing \`declan-stt.service\` is **not modified**. Do not change
  Home Assistant's STT pipeline during testing.
- Default bind is **127.0.0.1:10301** (local only). Do not expose the speaker
  endpoint to untrusted networks: Wyoming TCP has no authentication.
- Only Jaco and Edd are enrolment choices. An absent model, missing profiles,
  unrecognised voice, or identification exception produces
  \`speaker=Unknown, confidence=0.0\` with the normal transcript.
- Voiceprint identity is **not authentication**. The confidence is a cosine
  similarity score and requires calibration on actual microphones/rooms.
  Threshold 0.75 and margin 0.08 are conservative starting points, not
  validated values for the chosen model.
- This branch does **not** implement OpenAI learning or automatic enrolment.
  It neither uploads recordings nor updates profiles from live voice commands.
- The Home Assistant integration currently uses a \`str\` subclass for
  speaker metadata; verify that Home Assistant preserves it across STT and
  conversation stages. This has not been proven in a live pipeline.

## Test on LXC 107, once PR is checked out

The already-installed Python runtime at
\`/opt/wyoming-faster-whisper/.venv/bin/python\` includes Wyoming 1.11.0.
Run the gateway **as an unprivileged test process** with the repository
checkout at \`/opt/declan-gateway-candidate\`. No systemd changes needed.

\`\`\`bash
cd /opt/declan-gateway-candidate/deployment/wyoming-gateway
/opt/wyoming-faster-whisper/.venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=. /opt/wyoming-faster-whisper/.venv/bin/python -m declan_wyoming_gateway.server \
  --listen-host 127.0.0.1 --listen-port 10301 \
  --upstream-host 127.0.0.1 --upstream-port 10300
\`\`\`

Set \`PYTHONPATH=.\` for tests too if your working directory does not
automatically make the package importable:

\`\`\`bash
PYTHONPATH=. /opt/wyoming-faster-whisper/.venv/bin/python -m unittest discover -s tests -v
\`\`\`

In a second shell, use a Wyoming client and a **real 16-kHz mono PCM16 WAV**
to test the gateway. Confirm the final \`jarvis-speaker\` then \`transcript\`
order. The server currently accepts only 16-kHz 16-bit mono audio and
rejects other formats instead of silently corrupting audio.

## Optional voice recognition setup

The gateway starts in **Unknown-only mode** without \`--model\`. Before
enabling voiceprints, assess RAM/CPU, provision a trusted local WeSpeaker
ONNX file compatible with your pinned \`wespeakerruntime\` version, and
install \`wespeakerruntime\` into a **separate virtual environment** that
has Wyoming 1.11.0. Model fetching and installation are deliberately
not automatic.

Record at least three **separate** consented voice clips from each person,
16-kHz mono PCM16 WAV, ideally across the Kitchen, Lounge and Bedroom.
Use only local/private paths:

\`\`\`bash
PYTHONPATH=. python -m declan_wyoming_gateway.enrol Jaco jaco1.wav jaco2.wav jaco3.wav \
  --model /opt/declan-stt/speaker-model.onnx
PYTHONPATH=. python -m declan_wyoming_gateway.enrol Edd edd1.wav edd2.wav edd3.wav \
  --model /opt/declan-stt/speaker-model.onnx
\`\`\`

Start gateway with \`--model /opt/declan-stt/speaker-model.onnx\`.
The profiles default to \`/opt/declan-stt/speakers.json\` with mode 0600,
containing stored embeddings but no raw WAVs. Keep its backups private;
delete source WAVs when no longer needed. Recognition is never enabled
without explicit enrolment.

## Promotion criteria

Before changing production ports: run the real-Wyoming test suite;
exercise the gateway against 10300 with real speech; measure latency, CPU,
RAM, and matching in each room; test identical utterances by two people;
test unrecognised speaker; test upstream outage and gateway restart; and
verify speaker personalization survives the current HA pipeline.

Only after those pass should an independently reviewed cutover move
Whisper to 10302 and this gateway to 10300. This PR makes no such changes.
