# pATHENA Error Handoff

## Baseline

- Develop source: `develop/pathena-next@363d6ca497b12cf9f04d9c9392d945960eade3d3`.
- Error worker synchronized history-preservingly and NON-FORCE with exact current Develop via `9090e7e730ff519bad9146c6fcba5328e1d3a926`.
- Current workers reviewed: Backend `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`; Spec/Core `9e0f1df1a0321c2568993f974a4b1dcf316e6b21`; UI `2cb2feb3685358f629095445554c9d04fd56efd1`.
- Current Integrator handoff on Develop was reviewed. `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 grounded-response-receipt fixture candidate consumed

Backend exact head `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` is the current Fach-Worker candidate for one bounded v41 fixture/current-version subcluster. The mutation is harness-only in `tests/unit/test_grounded_response_receipt.py`: latest-schema assertions now use `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION` / `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`, and the v39 reconstruction explicitly drops the v41-only `research_delta_boundaries` table before replaying unchanged production migrations. No production schema, migration, recovery, WAL or security semantics changed.

Canonical Quality `34303936995@102aecd2c61415b0a428f6e69bba61bd3fb54f0b` is completed `FAILURE`. Exact gate state: Windows path safety PASS; Local install smoke PASS; Linux storage regressions PASS; specification validator PASS; mypy PASS; Ruff FAIL; full pytest FAIL; diagnostics upload PASS.

This is new completed exact-SHA evidence: the bounded candidate definitely landed on the tested worker SHA and preserved the non-pytest guard surface. It does not establish assertion-level PASS for the two grounded-response-receipt failures because the uploaded diagnostics archive is binary/non-UTF8 and is not readable through the available GitHub connector. `ERR-0028` therefore stays `IN_PROGRESS`; no `FIXED_PENDING_VERIFY` or `FIXED` claim is made.

Required next verification for this subcluster is a focused/assertion-level result for `tests/unit/test_grounded_response_receipt.py` on exact `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` or an exact direct successor. If those tests are green, close only this bounded fixture subcluster and continue with the remaining independent v41 fixture/current-version failures.

## Other active root causes

### ERR-0026 — schema Ruff I001

Latest Backend exact Quality `34303936995` remains Ruff red in the known `src/athena/storage/schema.py` I001 family. Previous import-order guesses did not clear it. Consume the exact current formatter diff before another mutation; do not guess ordering.

### ERR-0029 — WAL exact-type harness drift

Backend predecessor diagnostics recorded the prior three WAL exact-type harness failures as absent after harness-only repairs, but no focused/assertion-level current PASS has been consumed. Keep `IN_PROGRESS`; preserve production `type(...) is ...` fail-closed guards.

### ERR-0027 — v41 schema-facade re-export

Current Backend tree visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`; no false FIXED.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Exact current Backend candidate: `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`, canonical Quality `34303936995 = FAILURE`.
- `ERR-0028`: grounded-response-receipt harness candidate is bounded and semantically correct at code level, but lacks assertion-level PASS; do not promote it as closed.
- `ERR-0026`: current Quality remains Ruff red; require exact formatter-driven correction.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- `ERR-0027`: require focused schema-contract verification before closure.
- Preserve Windows path safety, Linux storage, Local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash guards.

## Persistent Beta/release matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context reserve including one-token and zero-margin boundaries; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures.

## Next verification

1. Obtain focused/assertion-level evidence for `tests/unit/test_grounded_response_receipt.py` on `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` or the first exact direct successor.
2. If green, close only that ERR-0028 subcluster and move to the highest remaining independent exact failure family.
3. Do not reopen stale/historical issues without exact-current reproduction.
