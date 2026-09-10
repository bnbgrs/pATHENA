# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T00:50Z
Branch: `develop/pathena-next`
HEAD at run start: `dd27bdc5f7d828b05a1be8614e035fd0055f57b9`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34418784921@dd27bdc5f7d828b05a1be8614e035fd0055f57b9 = SUCCESS`; no exact-current Develop Quality was queued or in progress before mutation.
- Current worker heads reviewed: Errors `611d0e6a9a2681c832dd833009237b84b956c78e`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `5b6e8226b316a8d0c943c71cab907d66360281a2`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- UI exact-head canonical Quality `34413496805@af50dfb76b04e396a2dbf65ec1eeb265f30177fa = SUCCESS` and is not superseded.
- UI delta is bounded to presentation/evidence files and focused Qt tests; Develop commits since the UI merge-base are disjoint release-contract/test/handoff changes.
- Backend remains conservative HOLD because its branch contains broad Storage/WAL/runtime changes.

## Integrated bounded worker slice — Workspace composer scale

- Integrated the verified UI-owned Workspace composer slice from the exact-green UI candidate.
- Composer remains the real chat surface and is fixed at 88 px; prompt at 44 px; real Sources grounding control at 36 px after Qt polish; real send control at 44×44 px outer geometry.
- QSS retains a 42×42 content box plus inherited one-pixel border per side; focused runtime Qt tests independently require exact 44×44 geometry.
- Existing send signal, Ctrl+Enter route, grounding behavior, accessible names/tooltips, model/provider behavior and persistence semantics are preserved.
- Updated the 11-screen manifest, Visual Gap Ledger and UI handoff from the same verified candidate; no screenshot-level MATCH claim is made.
- No Backend, Storage, Recovery, Security, worker/scheduler or packaging implementation semantics changed.
- No Skip/XFail, assertion weakening, force push, history rewrite, auto-merge, or main mutation.

## Persistent release guards

- pypdf packaging remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE topology remains guarded.
- Exactly one Desktop instance with bounded workers remains required.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety cluster remains guarded.
- Duplicate-column/Core-startup/storage-bootstrap signatures remain explicit Windows-Beta regression checks unless exact-current evidence reopens them.

## Next integration

1. Freeze Develop while canonical Quality for this exact integration commit is queued/in progress.
2. Consume that exact-SHA result before any further Develop mutation.
3. Keep Backend/Storage/Migration/Runtime conservative until a bounded exact-green promotable slice is isolated.
4. Continue UI only from new exact-current evidence; do not re-integrate this composer slice.
