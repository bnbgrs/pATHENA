# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@fafbeabdde1207ebc97712aa61ee947410cbf691`.
- Error worker pre-run head: `postmerge/errors@1a658432d623def854a726a954deadc256610545`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `5b6e8226b316a8d0c943c71cab907d66360281a2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` is still in progress, but `Windows path safety` has already completed `FAILURE` at `Run Windows storage path regressions`.
- On the same exact SHA, `Linux storage regressions = SUCCESS` and `Local install smoke = SUCCESS`; specification validator, Ruff and mypy are green while full pytest remains in progress.
- Exact current Backend Quality remains `34417344758@5b6e8226b316a8d0c943c71cab907d66360281a2 = FAILURE`.
- `postmerge/errors` had no canonical Quality runs before the ledger update and still had none before this handoff mutation.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`.
- OPEN: `ERR-0031`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- BLOCKED: none at top level.

## Hard progress this run — new current Develop Windows storage-bootstrap regression isolated

### ERR-0031 — Windows storage-bootstrap regression exposed by canonical lane coverage

Status: `OPEN`, P1 current Develop integration blocker.

Exact reproduction is canonical Quality `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691`. The completed `Windows path safety` job fails specifically at step `Run Windows storage path regressions`; the immediately preceding deterministic Windows-locality step succeeds. The later API-runtime step is skipped because that storage step failed.

The same exact SHA completes `Linux storage regressions = SUCCESS`. Commit `fafbeabdde1207ebc97712aa61ee947410cbf691` adds `tests/unit/test_storage_bootstrap.py` to the existing Windows storage-regression command and otherwise changes only the Integrator handoff. No production Storage/Recovery implementation was changed by this commit. This bounds the newly exposed cluster to Windows execution of the storage-bootstrap test surface, but assertion-level root cause is not yet claimed because the canonical diagnostic/log payload is not yet available while full pytest is still running.

Do not weaken `storage-bootstrap`, Storage, Recovery, lane-lock, path-safety or fail-closed behavior. Do not Skip/XFail. The next run must consume the completed exact-SHA canonical diagnostics first and identify the exact failing test/assertion before any minimal fix.

## Lower-priority active worker clusters

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2. Backend remains `5b6e8226b316a8d0c943c71cab907d66360281a2` with Quality `34417344758 = FAILURE`. Two independent harness root causes remain exact on that worker SHA: stale terminal-current-schema v40 expectations after successful v41 upgrade, and current-schema-derived legacy fixtures retaining the v41 Delta table before version rewind. These remain below the newly reproduced Develop P1.

### ERR-0026 — Backend schema Ruff I001

`IN_PROGRESS`, P2. Exact Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` / Quality `34417344758` still reports Ruff `I001` at `src/athena/storage/schema.py:3:1`. Backend must produce real Ruff PASS; no Ruff weakening or bypass.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2. Preserve production exact-type fail-closed guards; no new focused closure evidence was consumed for this cluster in this run.

## Integrator handoff

- Develop `fafbeabdde1207ebc97712aa61ee947410cbf691` is currently **HOLD** because canonical Quality `34435069158` has a completed Windows-path-safety failure.
- `ERR-0031 = OPEN`, P1. Exact completed evidence: `Windows path safety -> Run Windows storage path regressions = FAILURE`; Linux storage is green on the same SHA.
- The triggering integration delta adds only `tests/unit/test_storage_bootstrap.py` to the Windows storage lane; no production Storage/Recovery code changed in that commit.
- No assertion-level fix should be attempted until the exact canonical diagnostics are consumed. Preserve all existing fail-closed storage/recovery guards.
- Backend `5b6e8226b316a8d0c943c71cab907d66360281a2` remains independently non-promotable; its P2 clusters remain active but lower priority than current Develop `ERR-0031`.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume completed `34435069158@fafbeabdde1207ebc97712aa61ee947410cbf691` first. Extract the exact Windows `test_storage_bootstrap.py` failure/assertion, reproduce that focused check before any mutation, and then apply only the smallest root-cause fix on the responsible owner branch. Do not resume Backend P2 work while this current Develop P1 remains reproduced.
