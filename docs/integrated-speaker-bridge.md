# Integrated Wyoming speaker recognition

Declan now includes the original Jarvis-Voice-Bridge Wyoming STT implementation inside `declan_local`. You do not need a separate `jarvis_voice_bridge` custom component.

1. In **Settings → Devices & Services → Home Voice Assistant → Configure**, enable **Wyoming bridge**, enter the host/IP of the Wyoming speech service and its TCP port (default 10300). Save and reload the integration.
2. In **Settings → Voice assistants**, choose **Declan Wyoming Speaker Recognition** as speech-to-text and **Home Voice Assistant** as conversation agent for the same Assist pipeline. Repeat for pipelines used by all devices.
3. Ensure the Wyoming server emits a `jarvis-speaker` event containing `speaker`, `confidence`, and `interaction_id` **before** the final `Transcript` event. A normal Whisper/Wyoming server without this event cannot identify speakers.
4. Existing voice profiles still come from `/config/jarvis_voice_id.json`; do not delete or rename this file. Confirm the profile keys match the speaker IDs emitted by the server.
5. Check Declan diagnostics for `speaker_personalized` after speaking as Jaco and Edd separately. Test an unknown speaker as well.

**Important:** This integration transports existing speaker recognition results. It does not train or run a speaker identification model. The original bridge relied on Home Assistant preserving an in-process `str` subclass across the STT-to-conversation boundary. If the current HA version normalises the transcript to a plain string, speaker metadata will be lost; this requires live verification and potentially a different transport. Never use voice identification for access control.

No automatic change is made to the active Assist pipeline or live Home Assistant installation.
