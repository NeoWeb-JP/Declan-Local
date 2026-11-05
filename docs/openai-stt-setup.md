# Optional OpenAI STT for Declan

The integration now includes an opt-in STT entity. **Local Whisper remains the
default until the Assist pipeline is changed manually.** No API calls are made
until the OpenAI STT entity is selected and receives audio.

## Configuration

1. Obtain a separate OpenAI Platform API key with billing limits. A ChatGPT
   subscription does not include API transcription usage.
2. In Home Assistant, open **Settings > Devices & services > Home Voice Assistant
   > Configure**. Enable OpenAI STT, select `gpt-transcribe` (recommended)
   and paste the key in the password field. Save. Do not commit the key.
3. Confirm `stt.declan_openai_transcription` is available. If it is not,
   reload the integration and check Home Assistant logs.
4. Go to **Settings > Voice assistants**, clone the existing Declan Assist
   pipeline, and select **Declan OpenAI Transcription** as its STT provider.
   Keep the original local Whisper pipeline as a fallback.
5. Test the cloned pipeline on one satellite before changing other Echo Shows.

The STT entity accepts 16 kHz mono signed 16-bit PCM, wraps it as WAV, and
submits to the OpenAI audio transcriptions endpoint with a household vocabulary
hint. A maximum 60-second utterance and 25-second network timeout prevent
unbounded requests. API errors return STT failure, not invented text.

**Privacy:** selected utterance audio is sent to OpenAI for transcription.
**Costs:** API usage is billed separately. Monitor usage and set a billing
limit. Do not use a live pipeline until you accept this trade-off.

## Validation

Compare at least 30 identical recordings against local Whisper, including
silence/TV, country music everywhere, fairy lights, and both speakers. Measure
word error rate, exact-intent correctness, false activations and response time.
Wake-word detection is upstream of STT; cloud transcription does not cure false
wake-word triggers.

## Remaining integration work

Playlist variety selection exists as a pure policy but needs wiring into
Music Assistant and a private playlist catalogue. Sexy Time is currently a
Home Assistant script and must be updated there (or migrated to a shared
service) without breaking the other scene actions. Tessera/dashboard controls
must be adapted to the installed UI and actual player entities.
