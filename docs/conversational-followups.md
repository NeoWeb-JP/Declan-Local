# Corrections and information follow-ups (0.38.0)

Declan interprets these requests locally, without an LLM. The final request is
validated before any device action. Correction handling is bounded grammar;
it does not guess arbitrary names, actions or missing targets.

## Corrections

- “Turn the office lights on, actually turn the bedroom lights off.”
- “Dinner on, no I mean movie time.” Only the final validated routine runs.
- “Actually make them a bit dimmer.” Uses this conversation's recent lights.
- “Rather turn them off.” A new off command after a previous action completed.
- “Adjust them to 30 percent.” Uses the same revalidated lighting targets.
- “Turn the office lights on, no, stop.” Discards the on command and silently
  requests playback stop only for the originating satellite's configured player.

Explicit no-I-mean, sorry-I-meant and scratch-that markers are supported.
Short actually/rather/sorry forms require a supported command beginning after
the marker. Quoted titles and aliases remain literal. Rather-than phrases are
not interpreted as corrections. Ambiguous negative short-marker requests ask
for the final command and run nothing. Incomplete corrections also run nothing.

Preview/dry-run wrappers survive correction: “preview lights on, no I mean
lights off” remains a preview. Previews run no household actions or forecast
requests and do not replace a pending clarification. Real explicit corrections
supersede their own pending clarification before the final command is planned.

## Information dialogue

Ask current weather, time, indoor temperature or outside temperature as before.
Then use a short follow-up in the same conversation:

| Request | Result |
| --- | --- |
| “What's the weather?” → “and tomorrow?” | Tomorrow's dated daily forecast |
| “What's the weather?” → “what about later?” | Nearest future hourly forecast within six hours |
| “What's the temperature?” → “what about outside?” | Fresh reading from the configured weather entity |
| “What's the temperature?” → “and tomorrow?” | Explicitly outdoor forecast, never a predicted indoor reading |
| “Weather tomorrow” | Forecast without a previous topic |

Select an existing weather entity in Settings. Tomorrow requires that provider
to support daily forecasts; later requires hourly forecasts. The integration
calls HA weather.get_forecasts with a ten-second deadline. It selects the
requested date/time in HA's configured timezone, handles timezone offsets and
the repeated daylight-saving hour, and skips naive/invalid/stale-period entries.
Missing or unsupported forecasts are reported directly, without substituting
current weather as a forecast. Invalid numeric values are not spoken as readings.

Only the topic is remembered, never readings or forecast values. Every factual
answer rereads its source; the provider itself may cache data. Context expires
after two minutes, is bounded, and is separated by HA user, conversation,
originating satellite/device and reliable recognized speaker profile. Different
recognized speakers do not share lighting or information follow-ups. Unknown
voices cannot be distinguished within the same user/conversation/device; the
integration does not invent a speaker identity or use it for authorization.
Unrelated completed requests clear the information topic. Without a matching
topic, “and tomorrow?” asks for clarification rather than guessing.

## Cancellation limits

Stop clears its own remembered dialogue and suppresses a late in-flight
information reply. It does not cancel unrelated requests or HA automations.
Stopping after lights have already turned on does not turn them off; request
an explicit off command for that. Corrections to completed actions are new,
validated commands, not rollback. Cancellation/compensation for long-running
household routines and their full action lifecycle remain separate issue #5
work. Hardware microphone barge-in remains unverified.

No live HA deployment, pipeline/model changes or paid TTS generation were part
of this implementation. Unit/agent tests use controlled HA fixtures; live
forecast-provider and satellite behavior still need verification after deployment.
