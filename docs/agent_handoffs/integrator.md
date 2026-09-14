# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Exact Develop parent before this integration: `3a8120805e41d0fe9d283fc948d6e52b327a8e58`.
- Exact canonical Quality on that parent: `34893392725 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- `BUNDLED_SLICES=NONE` — the selected Backend slice is Backup/Recovery-adjacent and is integrated conservatively as a single bounded extraction.

## Iteration — durable Deep backup verification pipeline

Source head: `13ccd56eb7c4451e0b5b06532e98a67ec989c774`.
Exact evidence: Backend Focused `34899421459 = SUCCESS`; canonical Quality `34899421431 = SUCCESS`.

The extracted product/test scope is restricted to the Deep-verify payload, registration, worker, occurrence materializer, admission boundary, and their five focused unit-test files. Worker history is not merged.

The pipeline keeps backup verification separate from backup creation: payloads use exact keys, canonical UUID text, non-negative true integers and a pinned pipeline version; registration is CONTROL-lane-safe and explicitly forbids retry through `backup.create`; occurrence materialization is side-effect-free and deterministic; admission revalidates job type, payload identity, occurrence identity and idempotency before durable write; execution operates only on an existing snapshot, honors lease/cancel/RUNNING state, waits safely on busy/offline storage, heartbeats before Deep verification, checkpoints confirmed output, and fails closed on an active corrupt snapshot. No schema, migration, Security guard, Recovery guard or backup-create behavior is relaxed.

## Current worker truth at integration time

- Errors: `44930e07f8cb422a13da9b4036c6187aa4a770eb` — evidence/handoff lineage; no independent selected product slice.
- Spec/Core: `95a60521bb06cb883e14bdc5803181b224f53f64` — current head is not selected for this integration.
- Backend: `13ccd56eb7c4451e0b5b06532e98a67ec989c774` — selected exact-green bounded Deep-verify pipeline.
- UI: `e149515870b773548a164658775159f29de323af` — no exact-green bounded UI slice selected.

## Source-of-truth notes

- Historical Error-Ledger signatures are not OPEN without current reproduction.
- Eleven-screen visual status remains fail-closed; no screenshot-level `MATCH` may be claimed without opened original-reference evidence plus a real exact-SHA render and reviewed comparison.
- Persistent release guards remain mandatory and unchanged.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require complete canonical Quality `SUCCESS` on the resulting exact Develop SHA before any further Develop mutation.
