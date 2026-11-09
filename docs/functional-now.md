# NOW — Declan local voice MVP

**Draft scope for review.** Declan replaces everyday Alexa interactions with a Home Assistant voice agent. A configured Assist satellite is the primary entry point. The household must be able to use ordinary local device controls without Alexa or a cloud intent service. External speech, music and weather providers have their own availability boundaries.

| Everyday interaction | MVP acceptance scenario | Source |
| --- | --- | --- |
| Wake and respond | Invoke Declan through a configured satellite and receive a response through its configured output. Verify the wake model on hardware and check that the active Assist pipeline uses the intended conversation, STT and TTS entities. | FR-001–004, FR-070, FR-077 |
| Choose the responding satellite | When two satellites using Declan’s Wyoming speech path hear the same command and produce matching text within the arbitration window, the louder capture wins. Only the winning satellite executes the command and replies. | FR-045AP (MVP slice) |
| Control the room | Turn on an exposed light and set brightness using room context. An ambiguous target prompts clarification without changing anything. In “turn on the kitchen light, actually the hall light”, only the final validated target changes. | FR-020–021, FR-024, FR-026–027, FR-034 |
| Continue and stop | Resolve a simple follow-up within the five-minute rolling context. Expired context or a different speaker cannot reuse private details. Unknown speakers remain within the current safe session. Test an explicit Stop against the mapped output and ensure unrelated playback continues. | FR-025, FR-028, FR-031–035, FR-040, FR-061 |
| Play music | Start playback on a configured player using an existing category or playlist. Distinguish a dispatched request from verified playback and explain provider failures. | FR-050, FR-054 |
| Ask and set a timer | Answer time, weather and ordinary exposed device status from configured data. Set a valid timer associated with the originating satellite when known. Missing data and invalid durations get clear responses. | FR-060–062 |
| Run household routines | Invoke administrator-selected Home Assistant scripts or automations through native HA configuration. Their action sequences and targets stay in HA. Declan reports the common result contract, including uncertainty and partial completion, without hardcoded routine names or entity IDs. See [NOW routine outcomes](functional-now-routine-outcomes.md). | FR-003–004, FR-007–009, FR-063–064 |
| Respect household privacy | Test Home, Guest and unavailable Guest Mode. Unavailable selects Guest speech. Guest speech suppresses private details. Quiet hours affect delivery without selecting the persona. A recognised voice grants no additional permissions. | FR-010–018, FR-020A, FR-071 |

Source IDs refer to the [archived requirements](functional-requirements.md). Existing Home Assistant configuration and permissions define the eligible devices and routines. Unknown, sensitive and high-risk actions are blocked from the MVP voice path. [OD-06](functional-authentication-od06.md) preserves the policy for authenticated HA app approval of high-risk actions and a separately controlled PIN limited to explicitly allowlisted local interactions. Implementing those approval channels belongs in [FUTURE](functional-future.md).

## Satellite selection status

**Implemented for the NOW slice.** The owner reported passing the three two-satellite checks on 9 November 2026, covering a single action and reply, winner changes when speaking nearer each satellite, and closely spaced commands. This is owner-reported hardware evidence for the tested setup. The code commit and CI status were not supplied. The full archived FR-045AP remains broader, including selection without comparable audio, failover, diagnostics and privacy behaviour.

## Follow-up context status

**FR-031 NOW slice implemented in the local review patch.** Focused checks passed for lighting and information context after two minutes, the rolling five-minute expiry, preview behaviour, and speaker and session isolation. Satellite verification of conversation ID continuity remains open.

## Release evidence

- Exercise each scenario through Assist with the configured household devices. Record source implementation, CI and live results separately.
- Disconnect internet access while keeping HA and the local network reachable. Verify local intent and device execution through available local inputs. Record which satellite responses can use exact cached audio and which provider-dependent requests are unavailable. FR-072/073 record the ElevenLabs and cache policy. Confirm the installed configuration independently before claiming offline spoken coverage.
- Verify denial, ambiguity and unavailable-provider paths produce no unintended action and no false success. Record open decisions and any unverified scenario before MVP sign-off.

[Specification navigation](functional-specification-index.md) · [FUTURE index](functional-future.md)
