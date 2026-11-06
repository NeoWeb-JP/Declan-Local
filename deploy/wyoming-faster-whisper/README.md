# Optional Wyoming faster-whisper deployment

**Not deployed.** This is a starting template for a dedicated Proxmox VM/LXC with Docker and enough RAM/CPU. Model availability and exact CLI flags must be verified against the pinned image before production deployment. Do not use `latest` in production: pin an audited version or digest.

1. Create a dedicated guest with a static LAN address reachable from Home Assistant.
2. Set `WYOMING_BIND_IP` to the guest's private LAN address and `WHISPER_MODEL` to a supported model identifier. Start with `small-int8` only after confirming support.
3. Start manually with `docker compose up -d` and check `docker compose logs -f`.
4. Add **Wyoming Protocol** in Home Assistant, using the guest IP and port **10300**.
5. Create a **separate test Assist pipeline** that selects the new STT provider. Leave Declan's existing production pipeline unchanged.
6. Test identical consented utterances on both pipelines, capturing transcript, room, latency and command result in the offline evaluation file. Do not store audio by default.
7. Confirm offline operation by temporarily blocking internet egress **after** model download. Benchmark latency and accuracy before any switch.

The Wyoming port has no built-in authentication in this template. Restrict inbound access at the host firewall to Home Assistant only; do not expose it to the internet. The service can download model files during initial setup. No cloud audio transcription is needed once the model is cached.
