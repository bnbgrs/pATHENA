# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `develop/pathena-next@363d6ca497b12cf9f04d9c9392d945960eade3d3`.
- Error worker synchronized history-preservingly and NON-FORCE with exact current Develop via merge commit `9090e7e730ff519bad9146c6fcba5328e1d3a926`.
- Current workers reviewed: Backend `102aecd2c61415b0a428f6e69bba61bd3fb54f0b`; Spec/Core `9e0f1df1a0321c2568993f974a4b1dcf316e6b21`; UI `2cb2feb3685358f629095445554c9d04fd56efd1`.
- Current Backend exact canonical Quality: `34303936995@102aecd2c61415b0a428f6e69bba61bd3fb54f0b = FAILURE`.
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
- Latest exact Backend evidence: Quality `34303936995@102aecd2c61415b0a428f6e69bba61bd3fb54f0b` completed `FAILURE`; specification validator PASS, Ruff FAIL, mypy PASS, full pytest FAIL, Linux storage PASS, Windows path safety PASS and Local install smoke PASS.
- Previous isolated import-order candidates did not clear Ruff. Do not guess another ordering mutation without exact current formatter/diagnostic output.
- Integrator handoff: HOLD Backend v41/Research-dependent integration until an exact successor is Ruff green.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards remain authoritative and must not be weakened.
- Prior bounded orchestrator repair `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` replaced subclass `WalMaintenanceOrchestrator` doubles with canonical concrete instances while leaving production exact-type guards unchanged.
- Dependency-boundary candidate `3fbd8c238b8e926c5c175e37805c3033cb90e6b6` is harness-only in `tests/unit/test_wal_scheduler_dependency_boundary.py` and aligns the expected diagnostic with unchanged production behavior.
- Backend handoff for predecessor `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` records that the prior three WAL exact-type failures are absent from its diagnostics, but no focused/assertion-level current PASS has been consumed; keep `IN_PROGRESS`.
- Remaining known scope includes fake-`DurableJobScheduler` cases in `test_wal_job_hook.py`; do not weaken production exact-type guards.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: stale harness expectations treat v40 / `0040_grounded_response_receipts` as current, while reconstructed predecessor fixtures can retain the v41-only `research_delta_boundaries` table and collide with the strict real v40→v41 migration.
- New exact worker candidate: `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` is harness-only for the grounded-response-receipt subcluster. In `tests/unit/test_grounded_response_receipt.py` it changes latest-schema expectations to `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION` / `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and explicitly drops the v41-only `research_delta_boundaries` table when reconstructing the v39 predecessor; production migration/schema/recovery code is unchanged.
- New completed exact evidence: canonical Quality `34303936995@102aecd2c61415b0a428f6e69bba61bd3fb54f0b = FAILURE`. Windows path safety PASS; Local install smoke PASS; Linux storage regressions PASS; specification validator PASS; mypy PASS; Ruff FAIL; full pytest FAIL; diagnostics upload PASS.
- This verifies the bounded mutation landed on the exact tested SHA and preserved platform/storage/install/validator/type-check guards. It does NOT prove the two grounded-response-receipt assertions green because assertion-level diagnostics for the completed pytest failure are not readable through the available connector. Therefore no `FIXED_PENDING_VERIFY` or `FIXED` claim is made.
- Required next evidence: focused/assertion-level result for `tests/unit/test_grounded_response_receipt.py` on exact `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` or a direct successor. Keep remaining v41 fixture/current-version failures separate; production v40→v41 migration remains strict, additive, transactional and fail-closed.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2.
- Status: `IN_PROGRESS`.
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
