# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@82aaef0caaa90599f530acc84d728b602dee6739`.
- Error worker synchronized non-force/history-preserving through `51e34888084bfbd67f20e6b11bb8ee3622879b27`; ledger correction commit this run: `c20cdf1f14a94693f5eaf5aafae10a4f5ea4da5d`.
- Current workers reviewed: Backend `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`; Spec/Core `850b631007ba3f359b9b16c619c692d853d75663`; UI `41e05a7a8c22d9cd430ddb7f8a3518ee3b125af4`.
- Backend canonical Quality `34311050843@5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a = FAILURE`; Windows path safety, Linux storage, Local install, specification validator and mypy passed; Ruff and full pytest failed.
- UI canonical Quality `34315977802@41e05a7a8c22d9cd430ddb7f8a3518ee3b125af4` remains `IN_PROGRESS`; no competing run was started.
- `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0026 root-cause interpretation corrected

Exact Backend Quality `34311050843` remains red on Ruff I001 in `src/athena/storage/schema.py`; the Python quality check has four annotations and exact diagnostics artifact `10088876913` for head `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`.

The important new evidence is historical-but-exact to the current schema blob: Backend commit `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` explicitly says its one-line `DatabaseCompatibilityError` / `_user_tables` reorder was taken from exact `ruff.txt`. That candidate nevertheless remained canonical Ruff-I001 red, and current Backend keeps the same `schema.py` blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76` while Ruff is still red. Therefore the prior hand-transcribed two-symbol sort interpretation is not a sufficient root cause or fix and must not be retried in either direction.

The defect remains localized to import normalization in `schema.py`, but the only authorized next mutation is the exact Ruff 0.15.22 autofix/annotation payload applied to the current blob, followed first by focused Ruff verification. No further manual order guess is acceptable.

## Other active root causes

### ERR-0028 — remaining v41 fixture/current-version drift

The `tests/unit/test_grounded_response_receipt.py` subcluster stays CLOSED from exact six-test PASS evidence on `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`. Other independent v41 fixture/current-version failures keep `ERR-0028` globally `IN_PROGRESS`. Preserve strict production v40→v41 migration semantics.

### ERR-0029 — WAL exact-type harness drift

Prior harness-only repairs preserve production exact-type fail-closed guards, but no focused/assertion-level current PASS has been consumed for the remaining WAL cases. Keep `IN_PROGRESS` and do not weaken production guards.

### ERR-0027 — v41 schema-facade re-export

Current Backend tree visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Exact current Backend: `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`, canonical Quality `34311050843 = FAILURE`.
- `ERR-0026`: do not accept either prior manual `DatabaseCompatibilityError` / `_user_tables` ordering as proven. Require exact Ruff 0.15.22 autofix/annotation-driven correction on the current schema blob plus real Ruff PASS before integration.
- `ERR-0028`: grounded-response-receipt subcluster remains closed; independent v41 fixture failures remain active.
- `ERR-0029`: preserve production WAL exact-type guards and require focused evidence before closure.
- `ERR-0027`: require focused schema-contract verification before closure.
- Do not consume current UI head until exact Quality `34315977802` completes.
- Preserve Windows path safety, Linux storage, Local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash guards.

## Persistent Beta/release matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures.

## Next verification

Obtain the exact Ruff 0.15.22 annotation/autofix payload for `src/athena/storage/schema.py@b5658c38ca061095a951bc85f3a2fbc88b53ee76` from Quality `34311050843` / artifact `10088876913`, or consume the first Backend successor demonstrably generated from that payload. Apply no additional hand-guessed import reorder.
