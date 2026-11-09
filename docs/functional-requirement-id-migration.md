# PR #46: Requirement identifier collision resolution and migration register

**Documentation-only.** Eight duplicate definition IDs were resolved in `docs/functional-requirements.md` on the PR branch, retaining the full text and recorded status of every requirement. No code, HA, merge or deployment changes.

## Canonical identifier mapping

| Previously ambiguous ID | Preserved meaning under original ID | Renamed second definition | Meaning of new ID |
|---|---|---|---|
| FR-040 | Five-minute conversational context reset on restart | **FR-GUEST-040** | Staying declarations and manual guest handover |
| FR-041 | Multiple commands per utterance | **FR-GUEST-041** | Automatic guest handover opt-in and eligibility |
| FR-042 | One-off delayed/scheduled voice commands | **FR-GUEST-042** | Guest handover controller sequence and suspension |
| FR-043 | Conditional voice requests | **FR-GUEST-043** | Automatic guest authority revocation on owner return |
| FR-044 | Recurring voice schedules/reminders | **FR-GUEST-044** | Guest authority restart/reconfiguration provenance |
| FR-045 | Contextual follow-up action modification | **FR-GUEST-045** | External occupancy simulation suspension check |
| FR-045CY | Maintenance-session planning | **FR-MAINT-RECOVERY-001** | Recovery of abandoned/interrupted Maintenance Mode sessions |
| FR-050 | Music Assistant/Spotify playback | **FR-GUEST-FAREWELL-001** | No departing-guest farewell and owner return greeting |

## Preservation and traceability
- This is a **definition-ID-only** edit. The substantive requirement descriptions, statuses and surrounding sections were not rewritten.
- Original IDs remain assigned to the meanings listed in column two. Renamed meanings are retained with unique, descriptive IDs.
- Existing historical PR comments and external links may still use the old ambiguous ID. Resolve such references by **section and semantic meaning**, not by blind string replacement.
- A subsequent audit must classify all in-document inbound references to these eight old IDs as unambiguous, ambiguous, or requiring correction. Do not silently redirect a reference if it could mean either requirement.
- Update the prior [occurrence register](functional-requirements-definition-register.md) or replace it with a refreshed register; its original line numbers and collision flags represent the pre-remediation state.
- The broader `FR-OPT` consolidation remains a draft; renumbering does not imply feature approval, implementation or test completion.

## Acceptance evidence
The updated baseline was checked for unique requirement definition identifiers: **273 definitions and 273 unique IDs**, with no duplicate definition identifiers detected by the definition pattern. This is a structural check, not an independent semantic or test-coverage audit.

**No merge or deployment authorised.**