# Declan functional documentation

**Draft for owner review.**

- [NOW — Local voice MVP](functional-now.md) defines the active Alexa-replacement scope and acceptance scenarios.
- [FUTURE — Deferred functional work](functional-future.md) indexes homelab operations, predictive optimisation and advanced governance.

## Archive and supporting references

The original requirements, identifiers, source decisions and roadmaps are preserved in place. Historical priorities and review work below are archival. Use NOW for current MVP scope.

- [OD-06 authentication policy](functional-authentication-od06.md)
- [Owner review](functional-specification-owner-review.md)
- [Baseline traceability](functional-requirements-traceability.md) and [optimisation traceability](functional-optimisation-traceability.md)
- [Acceptance cases](functional-requirements-acceptance-cases.md), [definition register](functional-requirements-definition-register.md) and [ID migration proposals](functional-requirement-id-migration.md)

## Documents

| File | Purpose | Status |
|---|---|---|
| [functional-requirements.md](functional-requirements.md) | Original detailed FR-numbered baseline: Declan identity, Guest Mode, voice, context, music, routines, learning, roadmap | Preserved unchanged; draft |
| [functional-optimisation-requirements.md](functional-optimisation-requirements.md) | Original text of 17 optimisation requirements/checkpoint comments | Newly committed; draft |
| [functional-optimisation-governance.md](functional-optimisation-governance.md) | Original text of six governance, contracts, testing, roadmap and owner-decision checkpoints | Newly committed; draft |
| [functional-now-music-reliability.md](functional-now-music-reliability.md) | Release 0.52.0 music reliability requirements and live test matrix | Draft; documentation only |
| [functional-now-routine-outcomes.md](functional-now-routine-outcomes.md) | Generic result contract for routines selected from native HA scripts or automations; routine logic stays in HA | Draft; proposed contract |
| [functional-requirements-reconciliation.md](functional-requirements-reconciliation.md) | Four cross-file reconciliation, master-index, crosswalk and corrected decision checkpoints | Newly committed; draft |
| [legacy-jarvis-reference-audit.md](legacy-jarvis-reference-audit.md) | Legacy identifier inventory, migration risks and questions | Draft; do not bulk rename |
| [guest-persona.md](guest-persona.md) | Guest Mode-only persona, visitor/staying state and handover | Existing PR documentation |
| [branding-declan.md](branding-declan.md) | Identity, personality, voice and compatibility | Existing PR documentation |
| [declan-local-migration.md](declan-local-migration.md) | Historical domain migration instructions | Existing PR documentation |

## Scope and evidence caveats

1. The three new appendices preserve **27 GitHub comments** verbatim, with individual comment links and their original draft caveats. Early grouped comments are not complete transcripts of every earlier detailed conversation.
2. A prior scan identified 105 distinct FR-style IDs in the baseline; this is a targeted scan, not a proof of complete coverage. New `FR-OPT-...` modules were not incorporated into the original baseline text, but are now available in committed appendices.
3. Some historical comments list decisions as open that the baseline had already partly resolved. Prefer the later **FR-OPT-OWNER-DECISIONS-002** corrected status and direct owner-approved wording in the baseline; any true conflict requires owner review.
4. “Source”, “implemented”, “CI passed”, “live verified”, “deployed” and “owner-approved” are distinct states. Documentation alone proves none of the latter.
5. Review original PR comment sources when exact wording or provenance matters. No automatically inferred consent.

## Cross-cutting non-negotiables

- Explicit owner authorisation for consequential household, security, software, financial, trial and deployment actions, scoped to the exact proposal and risk.
- Guest Mode and speaker identification do not grant owner governance authority. Ordinary guest controls remain governed by existing HA permissions.
- Read-only analysis/simulation by default; no autonomous heating, EV, lighting, security, backups, restarts or deployments.
- Five-minute rolling conversational context, distinct from persistent governed preferences/audit.
- Maximum three routine optimisation recommendations in the shared weekly digest; urgent alerts follow separately approved rules.
- No fabricated success, measured savings, health, availability or source verification.
- Preserve existing entity IDs, settings and compatibility until an approved migration is independently verified.

## Historical review work

- Compare all earlier detailed planning conversations against baseline and appendices; identify exact missing acceptance cases.
- Convert duplicate/shared responsibilities into canonical schemas without erasing domain-specific safeguards.
- Resolve outstanding owner decisions in [reconciliation appendix](functional-requirements-reconciliation.md).
- Prepare a requirement-to-test matrix and owner acceptance checklist.
- Separately approve any implementation or release work. **Do not merge this draft merely because the files are present.**
