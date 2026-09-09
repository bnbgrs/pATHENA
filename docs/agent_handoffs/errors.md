# pATHENA Error Handoff

## Baseline

- Develop source: `develop/pathena-next@a32c63f39a2abca8a080ee78b97bd6b067eae52b`.
- Error worker is synchronized history-preservingly and NON-FORCE with exact current Develop in the commit carrying this handoff update.
- Current workers reviewed: Backend `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`; Spec/Core `57fa4db7283afd4b95458ad22cc991dad9c35065`; UI `2a09d487fe8ceb3db7e526e826fd7008d0002f30`.
- Current Integrator handoff on Develop was reviewed. `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0028 grounded-response-receipt subcluster closed

Backend exact candidate `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` is harness-only in `tests/unit/test_grounded_response_receipt.py`: latest-schema assertions use `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION` / `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`, and the v39 reconstruction drops the v41-only `research_delta_boundaries` table before replaying unchanged production migrations.

Canonical Quality `34303936995@102aecd2c61415b0a428f6e69bba61bd3fb54f0b` completed `FAILURE` globally, but its full pytest log provides the previously missing assertion-level evidence: `tests/unit/test_grounded_response_receipt.py ...... [24%]`. All six tests in the exact focused file passed on the exact candidate SHA. This closes the bounded grounded-response-receipt root-cause subcluster with real verification.

`ERR-0028` overall remains `IN_PROGRESS`: the same full-pytest run still contains other independent v41 fixture/current-version failures. Do not reinterpret the global pytest failure as failure of this now-green file, and do not close unrelated ERR-0028 subclusters without their own exact evidence. Production schema/migration/recovery behavior was not weakened or changed.

## Other active root causes

### ERR-0026 — schema Ruff I001

Exact Backend Quality `34303936995` remains Ruff red in `src/athena/storage/schema.py`. Previous import-order guesses did not clear it. Consume the exact current formatter diff before another mutation; do not guess ordering.

### ERR-0029 — WAL exact-type harness drift

Prior harness-only repairs preserve production exact-type fail-closed guards, but no focused/assertion-level current PASS has been consumed for the remaining WAL cases. Keep `IN_PROGRESS`.

### ERR-0027 — v41 schema-facade re-export

Current Backend tree visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Exact Backend candidate: `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`, canonical Quality `34303936995 = FAILURE`.
- `ERR-0028`: the `tests/unit/test_grounded_response_receipt.py` subcluster is now CLOSED by exact six-test PASS evidence from the canonical full-pytest log; do not reopen it absent exact-current regression. Remaining independent v41 fixture/current-version failures keep ERR-0028 globally `IN_PROGRESS`.
- `ERR-0026`: require exact formatter-driven correction and real Ruff pass.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- `ERR-0027`: require focused schema-contract verification before closure.
- Preserve Windows path safety, Linux storage, Local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash guards.

## Persistent Beta/release matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context reserve including one-token and zero-margin boundaries; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures.

## Next verification

Consume the highest-impact remaining exact failure from the same Backend Quality diagnostics. Do not spend another run on the grounded-response-receipt subcluster unless an exact-current regression reappears.
