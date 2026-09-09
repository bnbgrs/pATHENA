# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@82aaef0caaa90599f530acc84d728b602dee6739`.
- Error worker before this run: `postmerge/errors@c5a71183986c2bfe356f7737b853269edfc8045d`; ledger update commit in this run: `8de859ec4114f25bb708dab6f5e40909e62cec0b`.
- Current workers reviewed: Backend `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`; Spec/Core `5dd790f9102bed6377b1d7e495ec5e831f64d9ae`; UI `3cbb2aee7fb3e3bc48b7d6a9fefe86ea3132cb9e`.
- Current Develop `integrator.md`, worker `spec-core.md`, `backend.md`, `ui.md`, canonical ledger and this handoff were reviewed. `main` and `bnbgrs/ATHENA` remain read-only/untouched.
- Backend exact canonical Quality `34311050843@5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a = FAILURE`; current UI Quality `34312166038@3cbb2aee7fb3e3bc48b7d6a9fefe86ea3132cb9e` remains `IN_PROGRESS`. No competing Quality was started.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0026 localized on exact Backend successor

Canonical Quality `34311050843` completed on exact Backend head `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`. Windows path safety, Linux storage regressions and Local install smoke passed; specification validator and mypy passed; Ruff and full pytest failed.

The successor comparison from the prior Backend candidate `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` to `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a` contains only `docs/agent_handoffs/integrator.md`, `src/athena/chat/direct.py` and `tests/unit/test_direct_chat_context_budget.py`. `src/athena/storage/schema.py` is unchanged across that successor, yet canonical Ruff remains red. This is new exact evidence that the current `ERR-0026` I001 is not caused by the synchronized DirectChat/develop changes; it remains localized to the pre-existing `schema.py` import block.

The currently visible `schema_contract` import already reflects the most recent attempted `DatabaseCompatibilityError` / `_user_tables` arrangement. Multiple manual reorder guesses have failed. Do not make another ordering guess. The next Backend mutation must be the exact Ruff 0.15.22 formatter/diagnostic diff, or an exact worker successor demonstrably applying that diff, followed by Ruff verification.

Status remains `IN_PROGRESS`; no FIXED/FIXED_PENDING_VERIFY claim is justified.

## Other active root causes

### ERR-0028 — remaining v41 fixture/current-version drift

The `tests/unit/test_grounded_response_receipt.py` subcluster remains CLOSED from exact six-test PASS evidence on `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`. Other independent v41 fixture/current-version failures keep `ERR-0028` globally `IN_PROGRESS`. Preserve strict production v40→v41 migration semantics.

### ERR-0029 — WAL exact-type harness drift

Prior harness-only repairs preserve production exact-type fail-closed guards, but no focused/assertion-level current PASS has been consumed for the remaining WAL cases. Keep `IN_PROGRESS` and do not weaken production guards.

### ERR-0027 — v41 schema-facade re-export

Current Backend tree visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Exact current Backend: `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`, canonical Quality `34311050843 = FAILURE`.
- `ERR-0026`: exact successor evidence proves the Ruff I001 survives with `schema.py` unchanged while only DirectChat/integrator files changed. Treat the fault as localized to the existing schema import block; require exact Ruff formatter-driven correction and real Ruff pass before integration.
- `ERR-0028`: grounded-response-receipt subcluster stays closed; remaining independent v41 fixture failures remain active.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- `ERR-0027`: require focused schema-contract verification before closure.
- Do not consume the current UI synchronized candidate until exact Quality `34312166038` completes; it is unrelated to the active Backend root-cause cluster.
- Preserve Windows path safety, Linux storage, Local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash guards.

## Persistent Beta/release matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures.

## Next verification

Consume an exact Ruff 0.15.22 formatter/diagnostic diff for `src/athena/storage/schema.py` at `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a` or the first Backend successor that applies it. Do not spend another run re-proving that the same unchanged import block is red.
