# Declan local STT autonomy (long-term project)

Status: **early implementation on the isolated draft branch**. Preview guidance and an offline STT transcript evaluation tool are implemented; local inference and production rollout are not. This branch is intentionally isolated from the Home Assistant conversation-trigger fix in PR #29. Do not deploy or merge as part of that fix.

## Goal
Make local speech recognition the default for Declan, while retaining optional OpenAI transcription as a reference and fallback. Improve accuracy for household names, devices, accents and microphones without uploading recordings by default.

## Proposed implementation
1. **Baseline**: inventory active voice pipelines and identify the current local STT backend; measure word error rate, command success, latency and per-satellite failures on a consented evaluation set.
2. **Local inference**: deploy a Wyoming-compatible faster-whisper service in a dedicated Proxmox guest. Benchmark small and medium models and available CPU/GPU acceleration before selecting hardware or model.
3. **Vocabulary and corrections**: expose a local vocabulary of HA friendly names and aliases, plus opt-in correction records. Distinguish transcription errors from intent-routing errors.
4. **Shadow comparisons**: only with explicit opt-in, transcribe the same utterance locally and with OpenAI. Record both outputs, source, timing, confidence where meaningful, and reviewed ground truth. Never assume the cloud transcript is correct.
5. **Data controls**: audio capture disabled by default; per-speaker consent, configurable retention, local storage, redaction/deletion/export and no collection of background conversations.
6. **Model adaptation**: prepare reviewed audio/transcript datasets; investigate a fine-tunable Whisper-compatible model and conversion to faster-whisper. Keep training separate from inference.
7. **Safe rollout**: evaluate candidate models on a held-out dataset, use explicit accuracy and latency gates, require approval before promotion, and support immediate rollback.

## Architecture boundaries
- Home Assistant voice pipeline chooses the STT provider.
- A dedicated STT service performs inference; the Jarvis Local integration remains responsible for conversation/intent execution.
- A separate learning service stores opted-in examples and review decisions.
- OpenAI comparison is optional and must never be a prerequisite for local command execution.
- No automatic retraining, cloud uploads, microphone recording, or production pipeline changes in this planning branch.

## Acceptance criteria for future implementation
- Works with internet disconnected.
- Does not regress existing Declan command handling or HA conversation triggers.
- Shows per-room transcription accuracy and command completion separately.
- Allows correction, review, deletion and export of retained examples.
- Candidate model is benchmarked and can be rolled back.
- Existing pipeline remains unchanged until separately approved.

## Current development milestone
- Run offline baseline: `python tools/stt_baseline.py path/to/reviewed-transcripts.json`.
- Input JSON is an array of objects: `{"reference":"turn on fairy lights","hypothesis":"turn on ferry lights","room":"kitchen","command_success":false}`.
- Metrics report per-room and overall word error rate (WER), plus separately measured command success rate.
- Only use consented, reviewed transcript pairs; do not collect audio automatically.
- Added optional Wyoming faster-whisper Docker Compose template and isolated test-pipeline setup notes under `deploy/wyoming-faster-whisper/` (not deployed or benchmarked).
- Added offline opt-in correction review: `python tools/stt_review.py reviewed.jsonl approved.json`; each JSONL record requires `reference`, `hypothesis`, `reviewed` and `consent`. Only explicitly consented and reviewed pairs are exported.
- Next: benchmark a dedicated Wyoming host, add reviewed HA-friendly-name vocabulary and correction UI, and test end-to-end latency.
- Keep the existing STT pipeline and Home Assistant deployment unchanged until explicit approval.
