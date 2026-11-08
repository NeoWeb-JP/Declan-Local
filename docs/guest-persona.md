# Home/Guest speech and guest handover (current behaviour)

> Updated for the Guest Mode-only persona policy merged after 0.40.3 development. The visitor and staying helpers remain relevant to handover, **not** direct personality selection.

The speech-privacy foundation remains active. Automatic guest handover is
now available as a separately configured opt-in. Nothing is enabled merely
by installing this update, and no existing HA automation is edited.

In Declan's administrator settings, select the existing **Guest Mode**
input_boolean helper. The optional visitor, staying and quiet-hours helpers
have independent responsibilities. The integration does not create them.

| Guest Mode helper state | Spoken persona |
| --- | --- |
| `off` | Home: full savage household banter |
| `on` | Guest: playful, impersonal guest roasts |
| missing, unknown or unavailable | Guest: privacy-safe fallback |

Only the Guest Mode helper selects the persona. Visitor presence, staying
declarations, owner presence, speaker identity and quiet hours do **not**
directly select it. The separate automatic guest handover controller may
**change Guest Mode itself** after its eligibility checks; that state change
then changes the persona. Visitor declarations alone grant no permissions.

Only Home and Guest response catalogues remain. Home has short original,
sharp butler banter and occasional clothing-optional jokes; Guest has impersonal
cheek without private host details. Lighting confirmations are selected locally,
with action-specific recent-reply avoidance. Same-category cached alternatives
use the same privacy policy. Dynamic facts and errors are not replaced by jokes.

Recognized names and custom private morning replies are suppressed in Guest
speech. Self-correction acknowledgements use the same catalogue policy instead
of checking a hardcoded Guest Mode entity. Speaker identification remains
personalization only and never confers authority.

Quiet hours do not change the Home/Guest personality or force plain
acknowledgements. Delivery and audio-level behaviour are separate concerns.
Legacy personality-script choices do not override Guest Mode. Optional
phonetic conversion remains independent.

The morning routine's returned private greeting is replaced in Guest mode.
Other existing HA routines may make their own announcements; their external
speech and automation policy are not rewritten by this repository change.
Changing persona does not install a new wake-word or voice model.

## Staying declarations and manual authority

- “Mike and Kathy are staying with us” records separate staying names and
  turns on the visitor/staying helpers. It does not immediately grant authority
  or overwrite an existing manual handover's names.
- “We are going out and Mike and Kathy are in charge” and “put Kathy in charge”
  retain explicit manual handover. “Who is in charge?” reports its ownership.
- “Guests have left” clears visitors and staying, removes only automatic
  authority, and preserves an explicit manual handover. Use “cancel guest
  handover” or “clear the guests in charge” to cancel manual authority too.
- Explicit cancellation inhibits automatic regrant until an owner returns,
  staying is cleared, or a new staying declaration is made.
- Previewing these phrases validates the helpers and describes the plan
  without changing them. Embedded control instructions are rejected as names.

## Configure automatic handover

Select these existing entities in Settings; no entity IDs or owners are guessed:

| Setting | Type / purpose |
| --- | --- |
| Guest authority helper | input_boolean; existing Guest Mode |
| Names currently in charge | input_text; existing authorized names |
| Visitors present | input_boolean; automatic handover eligibility, not persona |
| Guests staying | input_boolean; explicit staying declaration |
| Staying guest names | separate input_text; never the authority names helper |
| Enable automatic handover | separate input_boolean; must be on to opt in |
| First / second owner presence | two distinct person entities |
| Away-simulation suspension signal | dedicated input_boolean; see below |

Automatic authority requires complete, healthy configuration, opt-in on,
visitors on, staying on and usable staying names. Both configured owners
must remain exactly `not_home` continuously for at least 120 seconds. Custom
zone names, missing, unknown and unavailable states do not qualify. State
changes reset the observation window even between five-second reconciliation
checks. Checking status does not reset the window.

The integration first raises the dedicated suspension signal, copies staying
names into the authority names helper, then enables Guest Mode. It rechecks
eligibility between awaited writes. A return or uncertain presence removes
only recorded automatic authority; the Guest persona then follows the actual Guest Mode state. Manual handovers survive owner return. Taking over an
automatic handover with an explicit manual command persists that decision.

## Occupancy simulation coordination

The suspension entity is a dedicated signal, not the occupancy automation's
enable switch. The existing away-simulation automation must check this signal
is off before starting its actions. Retain its ordinary owner-presence and
manual Guest Mode conditions as well. This update does not insert that
condition into your HA configuration and cannot stop an already-running
simulation. No automation is cancelled or disabled by the integration.

Only a suspension signal raised by this controller is cleared when its guest
authority ends. A preexisting on signal is left on. If explicit manual
handover takes over automatic authority, the owned suspension stays on until
that handover is explicitly cancelled. Keep this helper dedicated; use the
handover commands for explicit takeover rather than turning an already-on
helper on again, which produces no observable state transition.

## Restart, reconfiguration and verification

Authority provenance and suspension ownership are stored privately in HA
storage. Restart never trusts a persisted elapsed-away timer: recorded
automatic authority is removed and a fresh two-minute observation begins.
Manual authority is retained. Existing on authority without automatic ownership
is treated as manual. Unavailable helpers and failed writes are retried by
reconciliation, with no new grants from uncertain data. Partial grants remain
recorded for cleanup after interruption. Reconfiguration releases old automatic
ownership before applying new entity bindings; it cannot redirect revocation
to a newly selected manual helper.

Unloading/removing the integration attempts to release automatic authority and
its owned suspension signal, while retaining manual handovers. If a configured
helper is unavailable, that cleanup cannot be confirmed; the failure is logged
and its persisted ownership remains available for reconciliation on reload.

Tests cover delays, transient unavailable states, owner-return races, manual
takeover, restart, failed storage/helpers, cancellation, partial cleanup,
preexisting suspension and preview routing. Live HA helper/event behavior and
the occupancy automation's suspension condition still need acceptance testing.
No live helpers, permissions, pipeline or automation were modified in development.
