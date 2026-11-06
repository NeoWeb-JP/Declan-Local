# Proxmox pve: isolated Declan Wyoming STT test guest

Target host: existing `pve` (i7-4770, 32 GB RAM, GTX 1650). This is a **proposed** setup, not an executed deployment.

## Guest sizing and isolation

- New Debian 12 LXC, unprivileged, dedicated to Wyoming STT. Choose a **free** CT ID; do not assume 106 or any other existing ID is available.
- Initial allocation: 3 vCPU, 4096 MiB RAM, 1024 MiB swap, 16 GiB root disk.
- Assign a reserved LAN IP, not an assumed address. Expose TCP 10300 only to Home Assistant.
- CPU-first benchmark. GPU passthrough to an LXC requires additional host configuration and is **not** part of the initial rollout.
- Docker inside LXC needs nesting and may be less robust than a VM or native Python service. Validate the host's LXC nesting/storage settings before installing Docker. If unsuitable, use a small dedicated VM instead.
- Confirm available RAM, CPU load and disk space on `pve` before creating the guest. Existing HA, Frigate and Ollama workloads take priority.

## Preflight (run on Proxmox host, read-only)

```bash
pveversion
pct list
qm list
free -h
df -h
pvesm status
lscpu | grep -E 'Model name|CPU\(s\)'
```

Do **not** run `pct create` until a CT ID, storage pool, network bridge, template and IP are confirmed.

## Test deployment

See `deploy/wyoming-faster-whisper/compose.yaml` and its README. The Compose template is a starting point only; verify model names and CLI arguments against the pinned Wyoming image version before deployment. Download the model once, then benchmark with internet egress disabled.

In Home Assistant: add the Wyoming Protocol integration pointing to the test guest IP on port 10300. Create a **separate** Assist pipeline with Wyoming STT and Declan conversation agent. Do not modify existing production pipeline or Echo Show defaults.

## Acceptance gates

- Minimum 20 consented, reviewed utterances per target room, including fairy lights, dining room, house status, morning operations briefing and multi-step rejection cases.
- Compare per-room WER, command success, median and p95 end-to-end latency against current OpenAI STT on the **same** consented utterances.
- Verify native Home Assistant automation triggers separately from STT accuracy.
- Verify offline transcription after initial model download.
- Preserve current pipeline for immediate rollback. Promotion requires explicit approval.
