# pATHENA Error Handoff

## Baseline

- Develop source: `develop/pathena-next@e1aca469e4e27356f7de14e59ee63171a0d7111b`.
- Error worker before this run: `postmerge/errors@76032cc170df2758d2ee7737bf919d619f67407a`; this handoff is prepared for one history-preserving NON-FORCE synchronization commit carrying exact current Develop as second parent.
- Current workers reviewed: Backend `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947`; Spec/Core `48ed95dd1a667e58777599998e07751cb9a0e27c`; UI `f02642bda40feebb5c6c91803386ceb0f05e0e1a`.
- Current Integrator handoff on Develop was reviewed. `main` and `bnbgrs/ATHENA` remain read-only/untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- OPEN / FIXED_PENDING_VERIFY / BLOCKED: none.

## Hard progress this run — ERR-0026 current candidate disproven

Backend exact head `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` is the active Fach-Worker candidate for the schema Ruff cluster. It explicitly attempted the isolated import-order repair in `src/athena/storage/schema.py` by placing `DatabaseCompatibilityError` before `_user_tables`; the resulting product blob is `b5658c38ca061095a951bc85f3a2fbc88b53ee76` and no schema/runtime semantics were changed.

Canonical Quality `34299682340@82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` is completed `FAILURE`. Exact gate state: Windows path safety PASS; Local install smoke PASS; Linux storage regressions PASS; specification validator PASS; mypy PASS; Ruff FAIL; full pytest FAIL; diagnostics upload PASS.

This is new completed exact evidence and it disproves the previous two-symbol ERR-0026 correction. `ERR-0026` stays `IN_PROGRESS`; do not mark it `FIXED_PENDING_VERIFY`. The remaining Ruff failure is still the schema import-order family, but another mutation requires the exact current formatter diff rather than a second ordering guess.

The Backend handoff also records `31 failed, 4820 passed, 3 skipped` on the predecessor diagnostics and identifies the remaining independent pytest families as v41 fixture/current-version drift plus WAL harness collaborators. The current overall pytest failure does not by itself close or reopen any bounded subcluster without assertion-level evidence.

## Other active root causes

### ERR-0029 — WAL exact-type harness drift

The harness-only scheduler/guard-text corrections remain aligned with unchanged fail-closed production exact-type guards. Backend states the three predecessor WAL failures are addressed in the current worker lineage, but exact Quality `34299682340` is still globally pytest red. Keep `IN_PROGRESS`; consume focused/assertion-level evidence before closing any WAL subcluster. Do not weaken production `type(...) is ...` guards.

### ERR-0028 — stale v40 schema expectations/legacy fixtures

Root cause remains harness-owned: stale current-version expectations plus reconstructed legacy fixtures retaining v41-only `research_delta_boundaries`. Backend current diagnostics still identify this independent cluster. Repair fixtures/assertions only; keep production v40→v41 migration strict, additive and transactional.

### ERR-0027 — v41 schema-facade re-export

Current Backend tree visibly carries both Research Delta constants, but no exact focused passing contract assertion has been consumed. Keep `IN_PROGRESS`; no false FIXED.

## Non-Backend exact evidence reviewed

- Spec/Core head `48ed95dd1a667e58777599998e07751cb9a0e27c`; handoff records exact-green Quality `34294351333` on verified Core candidate `f8c06909a03a981464bf022ed6a4e30271225b93` for the adaptive DirectChat reserve lineage.
- UI head `f02642bda40feebb5c6c91803386ceb0f05e0e1a`; prior exact UI product candidate `a426469b503c6276cd6d1fd3ed6d89be0af67948` had canonical Quality `34291934346 = SUCCESS` before synchronized ancestry.
- Current Develop `e1aca469e4e27356f7de14e59ee63171a0d7111b` adds the zero-margin 2048-context boundary regression; no historical runtime signature is reopened without exact-current reproduction.

## Integrator handoff

- HOLD Backend v41 / Research-dependent integration while `ERR-0026` through `ERR-0029` remain unresolved.
- Exact current Backend candidate: `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947`, canonical Quality `34299682340 = FAILURE`.
- `ERR-0026`: current import-order fix is disproven by exact Ruff-red successor. Consume exact current formatter/diagnostic diff before any further import-order mutation.
- `ERR-0029`: current harness corrections must receive assertion-level/focused PASS before bounded closure; preserve production WAL exact-type guards.
- `ERR-0028`: harness-only correction; no migration permissiveness.
- `ERR-0027`: require focused schema-contract verification before closure.
- Preserve Windows path safety, Linux storage, Local install/start, Security, Provider/Transport, Recovery, Validator, Ruff, mypy and release crash guards.

## Persistent Beta/release matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen argv; Desktop/Worker two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context reserve including one-token and zero-margin boundaries; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures.

## Next verification

1. Consume the exact Ruff diagnostic/formatter output for `34299682340@82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` or the first Backend successor carrying that exact diagnostic-driven correction.
2. If Ruff clears, verify the highest remaining exact pytest root-cause family with focused evidence; do not conflate v41 fixture drift, schema re-export verification and WAL collaborator drift.
3. Do not reopen stale/historical issues without exact-current reproduction.
