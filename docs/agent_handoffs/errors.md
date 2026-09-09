# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@0abc53a35e6c99bf7070875633d3f81f6bc09395`.
- Error worker pre-run head: `postmerge/errors@72b6c7bf0ed148ce1f2f274ae6940a14053c6655`.
- Current workers: Spec/Core `850b631007ba3f359b9b16c619c692d853d75663`; Backend `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`; UI `24d703dd1711ad663779784f96119dade62fe732`.
- Exact Develop canonical Quality `34331712073@0abc53a35e6c99bf7070875633d3f81f6bc09395` is `IN_PROGRESS`; no competing canonical run was started.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 backup-retention subcluster CLOSED

Backend exact head `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f` completed canonical Quality `34329321526 = FAILURE`, with diagnostics artifact `10096038673`. Windows path safety, Local install smoke (including pypdf packaging metadata), Linux storage regressions, specification validator and mypy passed; Ruff and full pytest remained red. Full pytest ended with `23 failed, 4836 passed, 3 skipped`.

Assertion-level evidence resolves the bounded backup-retention v41 fixture repair: the canonical pytest log contains `tests/unit/test_backup_retention.py ..... [7%]`, so all five tests in that file passed on the exact candidate. The candidate's repair is harness-only: reconstructed v34 state drops the v41-only `research_delta_boundaries` table and post-upgrade expectations use `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`. Production schema/migration/Storage/WAL/Recovery behavior remains unchanged.

Therefore this backup-retention subcluster is CLOSED. `ERR-0028` overall remains `IN_PROGRESS` because the same exact canonical suite still reports independent v41 fixture failures in other test families. Do not reopen the backup-retention subcluster without an exact-current regression.

## Other active root causes

### ERR-0026 — schema Ruff I001

Exact Backend Quality `34329321526@5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f` still reports one Ruff `I001` import-block defect in `src/athena/storage/schema.py`; Ruff states it is fixable with `--fix`. Do not commit another hand-sorted import guess; require exact Ruff 0.15.22 autofix output plus focused Ruff PASS.

### ERR-0029 — WAL exact-type harness drift

Production exact-type fail-closed guards remain authoritative. No current focused/assertion-level PASS has been consumed for remaining WAL harness cases; keep `IN_PROGRESS`.

### ERR-0027 — v41 schema-facade re-export

Current Backend lineage visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration.
- Exact Backend head: `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f`; canonical Quality `34329321526 = FAILURE`; diagnostics artifact `10096038673`.
- `ERR-0028` backup-retention subcluster: `FIXED`/CLOSED on exact `5d8b73eeae04fb5d4a0f3c0bc7f31d767c30b82f` with all five `tests/unit/test_backup_retention.py` tests passing. Overall `ERR-0028` remains `IN_PROGRESS` for other independent v41 fixture failures.
- `ERR-0026`: still Ruff red; require formatter-generated fix and focused Ruff PASS.
- `ERR-0027`: require focused schema-contract verification before closure.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- Develop `0abc53a35e6c99bf7070875633d3f81f6bc09395` has exact Quality `34331712073` currently in progress; do not supersede or infer its result.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume the completed exact Develop Quality first when available. For Backend error work, select the highest still-active independent root cause from exact diagnostics; do not spend another run on the now-closed backup-retention subcluster. ERR-0026 requires the exact Ruff 0.15.22 autofix result before mutation; remaining ERR-0028 fixture failures require bounded assertion-level evidence before repair/closure.