# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `ae6ca984040c36a52c96c3e578cb0fee1e64136f`.
- Exact parent canonical Quality `34748637687 = SUCCESS`.
- Selected Backend source candidate: `aab04d0c4564a07f9af5c12e6fa496a5e1038ff7`.
- Exact candidate Storage Focused `34749553305 = SUCCESS`; canonical Quality `34749553299 = SUCCESS`.

## Iteration 1 — paired WAL/SHM startup identity guard integrated

Only `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py` are extracted from the exact-green Backend candidate. A complete simultaneous WAL+SHM identity rotation is rejected fail-closed before live-writer startup, while validated complete publication and withdrawal transitions remain permitted. Partial sidecar transitions, primary replacement, and invalid replacement remain rejected.

The worker branch history is not merged. The bounded product/test slice is extracted onto the exact Develop parent.

## Current worker state observed before mutation

- Errors: `c64e6be7d2c4b1bde22426c610925564684652c6`.
- Spec/Core: `e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`; current Core Focused and canonical runs are red, so no Core promotion.
- Backend: `aab04d0c4564a07f9af5c12e6fa496a5e1038ff7`; bounded Storage delta exact-green and selected.
- UI: `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc`; sync head only, no UI promotion without current exact evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail. `main` and `bnbgrs/ATHENA` remain read-only.

## Visual truth

Eleven-screen parity remains fail-closed: no `MATCH` without opened original reference plus real exact-SHA render. Historical `ERROR_LEDGER.md` state does not override current exact-SHA evidence.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
