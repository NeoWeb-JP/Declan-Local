# Home and Guest speech (0.36.0)

This is the speech-privacy foundation for issue #4. It does not automatically
enable Guest Mode, assign people in charge, suspend occupancy simulation or
change any existing Home Assistant automation.

In Declan's administrator settings select separate, existing input_boolean
helpers for **Guest mode helper**, **Visitors present (speech privacy only)**
and, optionally, **Quiet hours (plain acknowledgements)**. The integration
does not create helpers or infer visitor presence from recognized voices.

| Visitor helper | Guest authority helper | Speech |
| --- | --- | --- |
| off | off | Home |
| on | any state | Guest |
| any state | on | Guest |
| missing, unknown or unavailable signal | any state | Guest |

Both signals must explicitly be healthy and off for private Home replies.
Existing installations without the new visitor setting therefore use Guest
speech until it is configured. Declaring visitors changes the speech policy;
it grants no new permissions. Authority continues to use the existing explicit
handover commands and configured Guest Mode helper.

Only Home and Guest response catalogues remain. Home has short original,
sharp butler banter and occasional clothing-optional jokes; Guest has impersonal
cheek without private host details. Lighting confirmations are selected locally,
with action-specific recent-reply avoidance. Same-category cached alternatives
use the same privacy policy. Dynamic facts and errors are not replaced by jokes.

Recognized names and custom private morning replies are suppressed in Guest
speech. Self-correction acknowledgements use the same catalogue policy instead
of checking a hardcoded Guest Mode entity. Speaker identification remains
personalization only and never confers authority.

Quiet hours use plain acknowledgements. A configured quiet helper that is
missing or unavailable also uses plain speech. If no quiet helper is selected,
the configured legacy personality script is consulted only to preserve Night
behavior; its old Classic/Sassy/Savage/Guest choices and response text cannot
override the local privacy decision. With an explicit quiet helper, lighting
responses need no personality-script round trip. Existing phonetic conversion
remains optional.

The morning routine's returned private greeting is replaced in Guest mode.
Other existing HA routines may make their own announcements; their external
speech and automation policy are not rewritten by this repository change.
Changing persona does not install a new wake-word or voice model.

## Remaining issue #4 work

- Explicit staying and guests-left declarations independent of authority.
- Persisted manual versus automatic handover ownership.
- Continuous two-minute absence of both explicitly configured owners, safe
  restart/unavailable-state handling, and removal of only automatic authority
  when an owner returns.
- Explicit occupancy-simulation coordination and live acceptance testing.

No automatic authority should be inferred from this speech-policy milestone.
