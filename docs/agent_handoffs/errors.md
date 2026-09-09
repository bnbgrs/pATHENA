# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@2a90e71bc2c604cd745766a608481fc14106ec07`.
- Error worker pre-run head: `postmerge/errors@39066efeba8b1d6e69437050f7b490af39986d24`.
- Current workers: Spec/Core `571ecf65e3892a424afe8cbc5393e3ef0679ef76`; Backend `8dd0f50db0d593808093a8a0538097cc2e5c2d24`; UI `04a4e5d29421dc786c4894fd2091726fdeb5813a`.
- Exact Develop canonical Quality `34331712073@0abc53a35e6c99bf7070875633d3f81f6bc09395 = SUCCESS`.
- Current Develop exact Quality `34337745698@2a90e71bc2c604cd745766a608481fc14106ec07` is `IN_PROGRESS`; no competing canonical run was started.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 operational-error physical-cleanup subcluster CLOSED

Backend exact head `8dd0f50db0d593808093a8a0538097cc2e5c2d24` completed canonical Quality `34335076750 = FAILURE`, with diagnostics artifact `10097975314`. Windows path safety, Local install smoke and Linux storage regressions passed; Python quality remained red.

Assertion-level evidence resolves the bounded physical-cleanup v41 fixture repair: canonical `pytest.txt` contains `tests/unit/test_operational_error_physical_cleanup.py ..... [60%]`, so all five tests in that file passed on the exact candidate. The candidate repair is harness-only: reconstructed pre-v41 state removes the v41-only `research_delta_boundaries` object and current migration expectations use the truthful v41 Research Delta contract. Production schema, migration, physical-cleanup, Storage, WAL and Recovery behavior remain unchanged.

Therefore this physical-cleanup subcluster is `FIXED`/CLOSED. `ERR-0028` overall remains `IN_PROGRESS` because the same exact canonical suite still reports independent v41 fixture/current-version failures in other test families. Do not reopen grounded-response-receipt, backup-retention or physical-cleanup subclusters without an exact-current regression.

## Other active root causes

### ERR-0026 — schema Ruff I001

Exact Backend Quality `34335076750@8dd0f50db0d593808093a8a0538097cc2e5c2d24` remains Python-quality red. Prior exact diagnostics established one autofixable Ruff `I001` in `src/athena/storage/schema.py`. Do not commit another hand-sorted import guess; require exact Ruff 0.15.22 `--fix` output plus focused Ruff PASS.

### ERR-0029 — WAL exact-type harness drift

Production exact-type fail-closed guards remain authoritative. No current focused/assertion-level PASS has been consumed for remaining WAL harness cases; keep `IN_PROGRESS`.

### ERR-0027 — v41 schema-facade re-export

Current Backend lineage visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration.
- Exact Backend head: `8dd0f50db0d593808093a8a0538097cc2e5c2d24`; canonical Quality `34335076750 = FAILURE`; diagnostics artifact `10097975314`.
- `ERR-0028` operational-error physical-cleanup subcluster: `FIXED`/CLOSED on exact `8dd0f50db0d593808093a8a0538097cc2e5c2d24` with all five `tests/unit/test_operational_error_physical_cleanup.py` tests passing. Overall `ERR-0028` remains `IN_PROGRESS` for other independent v41 fixture/current-version failures.
- `ERR-0026`: still Ruff red; require formatter-generated fix and focused Ruff PASS.
- `ERR-0027`: require focused schema-contract verification before closure.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- Exact Develop `0abc53a35e6c99bf7070875633d3f81f6bc09395` is canonical green (`34331712073 = SUCCESS`). Current Develop `2a90e71bc2c604cd745766a608481fc14106ec07` already has Quality `34337745698` in progress; do not supersede or infer its result.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume the completed exact-current Develop Quality `34337745698` first when available. For Backend error work, select the highest still-active independent root cause from exact diagnostics; do not spend another run on the now-closed physical-cleanup subcluster. ERR-0026 requires exact Ruff 0.15.22 autofix output before mutation; remaining ERR-0028 fixture failures require bounded assertion-level evidence before repair/closure.