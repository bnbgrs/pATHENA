# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Exact Develop parent: `f8a25be7fd7df9f2a8ca281a1567f79ddaabcfb6`.
- Exact canonical Quality on that parent: `34883442620 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- `BUNDLED_SLICES=NONE` — single bounded Core-owned application Knowledge-read wiring slice.

## Iteration — AthenaApplication canonical Knowledge-read wiring

Source head: `9fe5dd44473ae200941d40ba37d14bc8816fdcdf`.
Exact evidence: Core Focused `34886553609 = SUCCESS`; canonical Quality `34886553447 = SUCCESS`.

The effective delta versus the exact Develop parent is bounded to `src/athena/core/application.py`, `tests/unit/test_knowledge_application_read.py`, and the Core worker handoff. No Backend, Storage, Security, Recovery, migration, schema, Qt/UI, or persistence-format file is changed.

`AthenaApplication` now consumes the already integrated `attach_knowledge_read_api()` boundary using the existing canonical `self.knowledge` and `self.api` instances, retains the exact returned service as `self.knowledge_read`, and exposes real Why-known/revision-history capabilities through the attached service rather than synthetic flags. The focused acceptance test starts a real temporary SQLite-backed Core, promotes persisted chat into canonical Knowledge, verifies service identity/capabilities/provenance, creates a direct user revision, and verifies immutable revision history plus the derived body diff.

## Current worker truth at integration time

- Errors: `f7f61c3dd543f8650b8bfc7c41eaa6a05ecb2a66` — evidence/handoff refresh; current reproduced product failures remain UI-owned.
- Spec/Core: `9fe5dd44473ae200941d40ba37d14bc8816fdcdf` — selected bounded application Knowledge-read wiring slice.
- Backend: `764f99c2949a7ff5eeee2199a9a65e4f71f06f13` — Deep-verify registration-boundary lineage; Backup/Recovery-adjacent, never bundled with this Core slice, and its checked-in handoff is stale relative to current exact worker evidence.
- UI: `e149515870b773548a164658775159f29de323af` — current handoff explicitly `Integrator-ready: NO` pending exact visual/technical evidence.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` is historical where newer exact-SHA evidence exists; historical signatures are not OPEN without current reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: only Slot 01 has directly opened reference-pixel evidence in the checked-in manifest, and no screenshot-level `MATCH` is valid without an opened original reference plus a real exact-SHA render. The verified Send target remains 44×44 outer geometry.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require complete canonical Quality `SUCCESS` on the resulting exact Develop SHA before any further Develop mutation. Backend remains a separate conservative candidate only after that new exact Develop gate is terminal green.
