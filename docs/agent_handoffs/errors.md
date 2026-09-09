# pATHENA Error Handoff

## Baseline

- Develop source: `develop/pathena-next@8b7d83ba170a121414a26055f0c5df9acf97914e`.
- Error worker: `postmerge/errors` only; history-preserving NON-FORCE synchronization commit `566fa0a6c0e598a2353bafa0d51889fa0a3463a5` carries current Develop plus canonical Error Ledger/Handoff.
- Current workers reviewed: Backend `3fbd8c238b8e926c5c175e37805c3033cb90e6b6`; Spec/Core `f8c06909a03a981464bf022ed6a4e30271225b93`; UI `33dcfb65e386e5a230ca476f4d9be1f36b56853d`.
- Current Integrator handoff on Develop was reviewed. `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0029 dependency-boundary candidate consumed

Backend exact head `3fbd8c238b8e926c5c175e37805c3033cb90e6b6` is a one-line harness-only correction in `tests/unit/test_wal_scheduler_dependency_boundary.py`: the expected `TypeError` regex now matches the existing production fail-closed diagnostic `requires canonical WalJobSchedulerHook`. The candidate changes no production WAL code and does not weaken the canonical `WalJobSchedulerHook` exact-type boundary.

Canonical Quality `34290849093@3fbd8c238b8e926c5c175e37805c3033cb90e6b6` is completed `FAILURE`. Exact gate state: Windows path safety PASS; Local install smoke PASS; Linux storage regressions PASS; specification validator PASS; mypy PASS; Ruff FAIL; full pytest FAIL; diagnostics upload PASS.

This is new completed exact evidence, but not assertion-level evidence that the dependency-boundary test itself passed. Therefore `ERR-0029` remains `IN_PROGRESS`; the corrected boundary-expectation subcluster is code-level aligned but not marked FIXED. Consume focused/assertion-level diagnostics before closure. Remaining fake-`DurableJobScheduler` harness cases in `test_wal_job_hook.py` stay separate inside the same root-cause family. Production exact-type guards remain immutable.

## Other active root causes

### ERR-0026 — Backend schema Ruff I001

- Current exact Backend Quality `34290849093` again has Ruff FAILURE.
- File/rule family remains `src/athena/storage/schema.py` / `I001`.
- Prior import reorder candidate `95b077af9e8e648f67863d36b5ddbbc2ec19051c` remains disproven.
- Do not guess another ordering change; require exact current formatter/diagnostic output first.

### ERR-0027 — v41 schema-facade re-export

Current Backend tree visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`; no false FIXED.

### ERR-0028 — stale v40 schema expectations/legacy fixtures

Root cause remains harness-owned: stale current-version expectations plus legacy fixtures precreating v41-only `research_delta_boundaries`. Repair fixtures/assertions only; keep production v40→v41 migration strict and transactional.

## Integrator handoff

- HOLD Backend v41 / Research §75 integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Exact current Backend candidate: `3fbd8c238b8e926c5c175e37805c3033cb90e6b6`, canonical Quality `34290849093 = FAILURE`.
- `ERR-0029`: boundary regex correction is harness-only and aligned with the unchanged production guard, but not yet assertion-level verified. Do not close from overall pytest-red evidence. Continue fake scheduler collaborator cases only with exact evidence; preserve production `type(...) is ...` fail-closed guards.
- `ERR-0026`: Ruff remains red; require exact current I001 formatter diff before mutation.
- `ERR-0027`: require focused schema-contract verification before closure.
- `ERR-0028`: harness-only correction; no migration permissiveness.
- Preserve Windows path safety, Linux storage, Local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash guards.

## Current non-Backend evidence

- Current Develop is `8b7d83ba170a121414a26055f0c5df9acf97914e`, integrating the exact-green UI black/orange foundation; no exact-current Develop canonical Quality run is associated with that head yet.
- Spec/Core current worker is `f8c06909a03a981464bf022ed6a4e30271225b93`; its prior exact verified candidate `06b121edfcc80d0a9e50ffa4173baaea8060d3f9` had canonical Quality `34285298078 = SUCCESS` for the adaptive DirectChat reserve lineage.
- UI current worker is `33dcfb65e386e5a230ca476f4d9be1f36b56853d`; exact UI product candidate `a426469b503c6276cd6d1fd3ed6d89be0af67948` had canonical Quality `34291934346 = SUCCESS` before synchronized documentation ancestry.

## Persistent Beta/release matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context reserve including one-token boundary; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures.

## Next verification

1. Consume readable assertion-level diagnostics or exact focused evidence for `34290849093@3fbd8c238b8e926c5c175e37805c3033cb90e6b6` and classify the bounded `ERR-0029` dependency-boundary subcluster without relying on overall pytest status.
2. If that exact test is green, record the subcluster closure while keeping remaining `ERR-0029` fake scheduler cases active; if red, repair only the demonstrated harness defect.
3. Then proceed to the highest remaining exact integration-impact root cause; do not reopen stale/historical issues without exact-current reproduction.
