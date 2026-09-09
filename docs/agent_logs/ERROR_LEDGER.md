# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@82aaef0caaa90599f530acc84d728b602dee6739`.
- Error worker before this ledger update: `postmerge/errors@c5a71183986c2bfe356f7737b853269edfc8045d`.
- Current workers reviewed: Backend `5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a`; Spec/Core `5dd790f9102bed6377b1d7e495ec5e831f64d9ae`; UI `3cbb2aee7fb3e3bc48b7d6a9fefe86ea3132cb9e`.
- Latest exact Backend canonical Quality: `34311050843@5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a = FAILURE`; Windows path safety PASS, Linux storage PASS, Local install smoke PASS, specification validator PASS, mypy PASS, Ruff FAIL, full pytest FAIL.
- Current UI canonical Quality `34312166038@3cbb2aee7fb3e3bc48b7d6a9fefe86ea3132cb9e` is still `IN_PROGRESS`; no competing run was started.
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
- New exact successor evidence: canonical Quality `34311050843@5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a` completed `FAILURE`; Ruff remains red while validator, mypy and all three platform/install jobs are green.
- Root-cause localization advanced this run: compare `102aecd2c61415b0a428f6e69bba61bd3fb54f0b...5fb8d5b7b5ee29af09bd70ccde8824633f0e0c8a` changes only `docs/agent_handoffs/integrator.md`, `src/athena/chat/direct.py` and `tests/unit/test_direct_chat_context_budget.py`. `src/athena/storage/schema.py` is byte-unchanged across that successor, yet Ruff remains red. Therefore the current I001 is independent of the DirectChat/develop synchronization and remains localized to the existing schema import block rather than a new cross-worker regression.
- Current import block is already in the latest previously attempted `DatabaseCompatibilityError` / `_user_tables` arrangement; another manual ordering guess is prohibited. The next mutation must be driven by the exact Ruff 0.15.22 formatter/diagnostic diff or an exact Backend successor that applies it.
- Integrator handoff: HOLD Backend v41/Research-dependent integration until an exact successor is Ruff green.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards remain authoritative and must not be weakened.
- Prior bounded orchestrator repair `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` replaced subclass `WalMaintenanceOrchestrator` doubles with canonical concrete instances while leaving production exact-type guards unchanged.
- Dependency-boundary candidate `3fbd8c238b8e926c5c175e37805c3033cb90e6b6` is harness-only in `tests/unit/test_wal_scheduler_dependency_boundary.py` and aligns the expected diagnostic with unchanged production behavior.
- Backend predecessor diagnostics recorded the prior three WAL exact-type harness failures as absent, but no focused/assertion-level current PASS has been consumed; keep `IN_PROGRESS`.
- Remaining known scope includes fake-`DurableJobScheduler` cases in `test_wal_job_hook.py`; do not weaken production exact-type guards.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: stale harness expectations treat v40 / `0040_grounded_response_receipts` as current, while reconstructed predecessor fixtures can retain the v41-only `research_delta_boundaries` table and collide with the strict real v40→v41 migration.
- Bounded grounded-response-receipt repair: Backend `102aecd2c61415b0a428f6e69bba61bd3fb54f0b` changes only `tests/unit/test_grounded_response_receipt.py`: latest-schema assertions use `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION` / `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID`, and v39 reconstruction drops the v41-only `research_delta_boundaries` table before replaying unchanged production migrations.
- Exact verification consumed from canonical Quality `34303936995@102aecd2c61415b0a428f6e69bba61bd3fb54f0b`: full pytest explicitly reports `tests/unit/test_grounded_response_receipt.py ...... [24%]`. All six tests in that focused file passed on the exact candidate SHA. The bounded grounded-response-receipt subcluster is CLOSED by real assertion-level evidence.
- `ERR-0028` as a whole remains `IN_PROGRESS` because other independent v41 fixture/current-version failures remain. Do not conflate those failures with the closed grounded-response-receipt subcluster.
- Production v40→v41 migration remains strict, additive, transactional and fail-closed; no production migration/schema/recovery code was changed for that closure.

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

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance, one-token and zero-margin boundaries; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
