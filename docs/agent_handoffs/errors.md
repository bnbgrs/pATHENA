# pATHENA Error Handoff

## Baseline

- Develop source: `develop/pathena-next@b04b0107f55d8af8b0398e48066481a84d27775f`.
- Error worker: `postmerge/errors` only; history-preserving NON-FORCE synchronization commit `46f3f7c35e2623c499d5c24735bf70219ac81443` carries current Develop plus canonical Error Ledger/Handoff.
- Current workers reviewed: Backend `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837`; Spec/Core `06b121edfcc80d0a9e50ffa4173baaea8060d3f9`; UI `2b54226815b0bb3b49832f1d64f1ac5b46716d41`.
- Current Integrator handoff on Develop was reviewed. `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0029 exact candidate result consumed

Backend advanced to exact candidate `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` with the bounded WAL orchestrator harness repair in `tests/unit/test_wal_maintenance_interval_runner.py` and `tests/unit/test_wal_schedule_overflow.py`. The tests use canonical concrete `WalMaintenanceOrchestrator` instances while preserving production exact-type fail-closed guards. Relative to predecessor `4495cab0492f0c70e6d0b5cbda1136c1d960ab86`, the candidate also history-preservingly carries current Develop DirectChat changes and updated handoffs; it does not weaken production WAL semantics.

Canonical Quality `34286119711@e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` is now completed `FAILURE`, replacing the previous pending state. Exact gate state: Windows path safety PASS; Local install smoke PASS; Linux storage regressions PASS; specification validator PASS; mypy PASS; Ruff FAIL; full pytest FAIL; diagnostics upload PASS. Artifact `10080190842` exists.

Therefore this WAL candidate is not globally verified and `ERR-0029` remains `IN_PROGRESS`. The available GitHub connector exposes artifact metadata but not the binary diagnostics payload, so this handoff does not fabricate assertion-level PASS/FAIL for the two focused orchestrator test files. The next Backend/Error run must consume readable current diagnostics or focused exact evidence before deciding whether that subcluster cleared. Separate fake-`DurableJobScheduler` cases in `test_wal_job_hook.py` remain pending under the same ERR family.

## Other active root causes

### ERR-0026 — Backend schema Ruff I001

- Current exact Backend Quality `34286119711` again has Ruff FAILURE.
- File/rule family remains `src/athena/storage/schema.py` / `I001`.
- Prior import reorder candidate `95b077af9e8e648f67863d36b5ddbbc2ec19051c` remains disproven.
- Do not guess another ordering change; require exact current formatter/diagnostic output first.

### ERR-0027 — v41 schema-facade re-export

Current Backend tree visibly carries both Research Delta constants, but no exact focused passing contract assertion is available in this run. Keep `IN_PROGRESS`; no false FIXED.

### ERR-0028 — stale v40 schema expectations/legacy fixtures

Root cause remains harness-owned: stale current-version expectations plus legacy fixtures precreating v41-only `research_delta_boundaries`. Repair fixtures/assertions only; keep production v40→v41 migration strict and transactional.

## Integrator handoff

- HOLD Backend v41 / Research §75 integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Exact current Backend candidate: `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837`, canonical Quality `34286119711 = FAILURE`.
- `ERR-0029`: do not mark the orchestrator harness candidate FIXED from overall pytest-red evidence. Consume readable diagnostics/focused evidence next; continue remaining fake scheduler collaborator cases only if exact evidence still points there. Preserve production `type(...) is ...` fail-closed guards.
- `ERR-0026`: Ruff remains red; require exact current I001 formatter diff before mutation.
- `ERR-0027`: require focused schema-contract verification before closure.
- `ERR-0028`: harness-only correction; no migration permissiveness.
- Preserve Windows path safety, Linux storage, Local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash guards.

## Current non-Backend evidence

- Spec/Core `06b121edfcc80d0a9e50ffa4173baaea8060d3f9` is reported by current Integrator handoff as canonical Quality `34285298078 = SUCCESS`, independently verifying the adaptive DirectChat product/test tree inherited by Develop.
- UI exact head `2b54226815b0bb3b49832f1d64f1ac5b46716d41` currently has Quality `34287102867` still `IN_PROGRESS`; it is not consumed as READY evidence here.

## Persistent Beta/release matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context reserve including one-token boundary; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures.

## Next verification

1. Consume readable diagnostics or exact focused evidence for `34286119711@e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` and classify the bounded `ERR-0029` orchestrator subcluster without relying on overall pytest status.
2. If it is green, record that subcluster closure while keeping remaining `ERR-0029` fake scheduler cases active; if red, repair only the demonstrated harness defect.
3. Then proceed to the highest remaining exact integration-impact root cause; do not reopen stale/historical issues without exact-current reproduction.
