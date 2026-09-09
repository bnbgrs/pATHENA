# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `develop/pathena-next@e1aca469e4e27356f7de14e59ee63171a0d7111b`.
- Error worker before this run: `postmerge/errors@76032cc170df2758d2ee7737bf919d619f67407a`; this ledger is prepared for one history-preserving NON-FORCE synchronization commit carrying exact current Develop as second parent.
- Current workers reviewed: Backend `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947`; Spec/Core `48ed95dd1a667e58777599998e07751cb9a0e27c`; UI `f02642bda40feebb5c6c91803386ceb0f05e0e1a`.
- Current Backend exact canonical Quality: `34299682340@82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY: none.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact rule/file family: Ruff `I001` in `src/athena/storage/schema.py`.
- Predecessor evidence: Quality `34290849093@3fbd8c238b8e926c5c175e37805c3033cb90e6b6` had exactly one Ruff I001 in this file and `31 failed, 4820 passed, 3 skipped` in pytest.
- Backend candidate `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` explicitly attempted the isolated import-order correction by placing `DatabaseCompatibilityError` before `_user_tables`; no schema/runtime semantics changed.
- New exact completed evidence: canonical Quality `34299682340@82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947 = FAILURE`. Windows path safety PASS; Local install smoke PASS; Linux storage regressions PASS; specification validator PASS; mypy PASS; Ruff FAIL; full pytest FAIL; diagnostics upload PASS.
- Current product blob `src/athena/storage/schema.py@b5658c38ca061095a951bc85f3a2fbc88b53ee76` contains the attempted `DatabaseCompatibilityError` / `_user_tables` ordering and still reproduces canonical Ruff failure. Therefore that two-symbol reorder is disproven and must not be treated as `FIXED_PENDING_VERIFY`.
- Root-cause refinement: the remaining I001 is still inside the large `athena.storage.schema_contract` import block, but the current completed run proves that merely reversing the final two mixed-case/private names is insufficient. Consume the exact current Ruff formatter diff before another Backend mutation; do not guess a second ordering change.
- Integrator handoff: HOLD Backend v41/Research-dependent integration until an exact successor is Ruff green.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards remain authoritative and must not be weakened.
- Prior bounded orchestrator repair `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` replaced subclass `WalMaintenanceOrchestrator` doubles with canonical concrete instances while leaving production exact-type guards unchanged.
- Dependency-boundary candidate `3fbd8c238b8e926c5c175e37805c3033cb90e6b6` is harness-only in `tests/unit/test_wal_scheduler_dependency_boundary.py`: expected `TypeError` regex aligns with the existing production diagnostic; no production WAL code changed.
- Backend handoff for `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` states the three predecessor WAL failures are addressed by current exact-class scheduler/guard-text harness commits, but exact Quality `34299682340` remains globally pytest red. No WAL subcluster is marked FIXED without assertion-level/focused PASS evidence.
- Remaining known scope includes fake-`DurableJobScheduler` cases in `test_wal_job_hook.py`; do not weaken production exact-type guards.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2. Status: `IN_PROGRESS`.
- Exact evidence family: stale fresh/current assertions expect schema v40 / migration `0040_grounded_response_receipts`; reconstructed v30-v40 fixtures can retain the v41-only `research_delta_boundaries` table/index, causing the strict real v40→v41 migration to raise `table research_delta_boundaries already exists`.
- Backend handoff on `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` confirms this independent v41 harness/fixture cluster remains in exact pytest diagnostics.
- Required fix remains harness-only: truthful v41 expectations and legacy fixture construction; production migration remains additive, transactional and fail-closed.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2. Status: `IN_PROGRESS`.
- Original exact red: Quality `34245022980` failed `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` with missing `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Current Backend tree visibly re-exports both Research Delta contract constants, but no independent focused/current canonical passing assertion has been consumed; no FIXED claim.

## Cleared historical state relevant to integration

- `ERR-0023` FIXED: exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- `ERR-0025` STALE after that exact-green Develop descendant.
- `ERR-0004` remains FIXED; current Ruff red is Backend schema `ERR-0026`, not the historical UI startup/readiness defect.
- `ERR-0014` remains STALE absent exact-current Qt SIGSEGV reproduction.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
