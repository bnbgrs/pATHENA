# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@38586782fd9b615ecd4226a4b0afe674d5520978`.
- Error worker entered this run at `postmerge/errors@567b61ccb36f5978c50568341318f43bea36fcce`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`; this is the closure evidence for `ERR-0032`.
- Current Develop canonical Quality `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978` is `IN_PROGRESS`. Windows path safety is already `SUCCESS`, including Windows storage regressions, Windows Core/API restart smoke and Windows pypdf packaging metadata verification; Linux storage and Local-install/pypdf are `SUCCESS`; specification validator, Ruff and mypy are `SUCCESS`; full pytest remains active.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`.
- STALE: `ERR-0014`, `ERR-0025`.
- BLOCKED: none.

## Hard progress this run — ERR-0032 exact closure

### ERR-0032 — schema-reinitialization harness row-shape mismatch

Status: `FIXED`, P1 when reproduced on Develop.

The bounded correction on Develop `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17` retained `sqlite3.Row`, both `initialize_schema()` calls and the schema-version invariant, while changing only the two `PRAGMA user_version` assertions to compare scalar `[0]` values.

New completed closure evidence: canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`, including full pytest and complete Windows path safety/storage regressions. This satisfies the prior `FIXED_PENDING_VERIFY` condition. No product schema, migration, Storage, Recovery, Runtime or Security behavior changed.

Current Develop `38586782fd9b615ecd4226a4b0afe674d5520978` is one CI-only commit ahead. Its active canonical Quality `34473603186` already has the Windows storage lane green, so there is no exact-current recurrence of the `ERR-0032` signature. The new commit adds Windows pypdf packaging metadata verification; that Windows packaging smoke has also passed.

No competing canonical Quality was started. No Skip/XFail, exception swallowing, migration idempotency relaxation, assertion removal, Storage/Recovery weakening or main mutation occurred.

## Lower-priority worker clusters held

### ERR-0026 — Backend Ruff/import-layout drift

`IN_PROGRESS`, P2 worker-local. Current Backend handoff marks broad worker history non-authoritative against current Develop. Error/Develop already carry the normalized schema import layout. Do not create a duplicate Error-owned formatter patch; require fresh exact-current Backend evidence before closure or reclassification.

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2 worker-local. Last worker diagnostics decompose into stale terminal-v41 assertions, duplicate-v41-table fixture collisions and downstream storage-bootstrap cascades, but the current Backend handoff explicitly places broad schema-v41 / Storage / Migration history on HOLD. Do not mechanically repair worker-only historical fixtures.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending fresh exact-current Backend evidence. Preserve production exact-type fail-closed guards.

## Integrator handoff

- Current Develop: `38586782fd9b615ecd4226a4b0afe674d5520978`.
- Previous exact closure Quality: `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`.
- Current canonical Quality: `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978`, active.
- `ERR-0032 = FIXED / P1 when reproduced`; exact repaired SHA is canonical-green.
- Current Windows path safety, storage regressions and Windows pypdf packaging metadata smoke are already green on `38586782...`; no new P1 is presently evidenced.
- Do not mutate Develop or start a competing canonical run while `34473603186` is active.
- On the next run consume `34473603186` first. If a distinct exact signature fails, classify it as a new/current cluster rather than reopening `ERR-0032` automatically.
- Keep lower-priority Backend v41/Ruff/WAL clusters on HOLD absent fresh bounded exact-current evidence.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards.
