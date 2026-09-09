# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `develop/pathena-next@8b7d83ba170a121414a26055f0c5df9acf97914e`.
- Error branch synchronized NON-FORCE/history-preserving to that Develop via merge commit `566fa0a6c0e598a2353bafa0d51889fa0a3463a5`; own mutations remain on `postmerge/errors` only.
- Current workers reviewed: Backend `3fbd8c238b8e926c5c175e37805c3033cb90e6b6`; Spec/Core `f8c06909a03a981464bf022ed6a4e30271225b93`; UI `33dcfb65e386e5a230ca476f4d9be1f36b56853d`.
- Current Backend exact canonical Quality: `34290849093@3fbd8c238b8e926c5c175e37805c3033cb90e6b6 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY: none.

## ERR-0029 — WAL harness collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards remain authoritative and must not be weakened.
- Prior bounded orchestrator repair `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` replaced subclass `WalMaintenanceOrchestrator` doubles with canonical concrete instances while leaving production exact-type guards unchanged; its canonical Quality `34286119711` remained globally red.
- New bounded dependency-boundary candidate: `3fbd8c238b8e926c5c175e37805c3033cb90e6b6`. Its complete diff is harness-only in `tests/unit/test_wal_scheduler_dependency_boundary.py`: the expected `TypeError` regex changed from `requires the canonical WalJobSchedulerHook` to `requires canonical WalJobSchedulerHook`, exactly matching the existing production fail-closed diagnostic. Production `src/athena/storage/wal_job_hook.py` is unchanged by this candidate.
- New exact completed evidence: canonical Quality `34290849093@3fbd8c238b8e926c5c175e37805c3033cb90e6b6 = FAILURE`. Windows path safety PASS; Local install smoke PASS; Linux storage regressions PASS; specification validator PASS; mypy PASS; Ruff FAIL; full pytest FAIL; diagnostics upload PASS.
- Interpretation: this run proves the candidate itself is not globally green, but the available connector still does not expose assertion-level pytest diagnostics. Therefore the dependency-boundary subcluster is **not** marked FIXED from overall pytest-red evidence. Its harness expectation is now code-level aligned with the unchanged production contract; focused/assertion-level PASS remains required before closure.
- Remaining known scope includes fake-`DurableJobScheduler` cases in `test_wal_job_hook.py`; do not weaken production exact-type guards.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2. Status: `IN_PROGRESS`.
- Exact evidence family: stale fresh/current assertions expect schema v40 / migration `0040_grounded_response_receipts`; legacy v30-v40 fixtures already contain v41-only `research_delta_boundaries`, causing the strict real v40→v41 migration to raise `table research_delta_boundaries already exists`.
- Required fix remains harness-only: truthful v41 expectations and legacy fixture construction; production migration remains additive, transactional and fail-closed.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2. Status: `IN_PROGRESS`.
- Original exact red: Quality `34245022980` failed `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` with missing `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Current Backend tree visibly re-exports both Research Delta contract constants, but no independent focused/current canonical passing assertion has been consumed; no FIXED claim.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2. Status: `IN_PROGRESS`.
- Exact rule/file family: Ruff `I001` in `src/athena/storage/schema.py`.
- Candidate `95b077af9e8e648f67863d36b5ddbbc2ec19051c` was disproven by exact successor Quality `34281292370` with unchanged product tree and Ruff still red.
- Current Backend Quality `34290849093@3fbd8c238b8e926c5c175e37805c3033cb90e6b6` again has Ruff FAILURE. Do not guess another ordering change without the exact current diagnostic/formatter diff.

## Cleared historical state relevant to integration

- `ERR-0023` FIXED: exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- `ERR-0025` STALE after that exact-green Develop descendant.
- `ERR-0004` remains FIXED; current Ruff red is Backend schema `ERR-0026`, not the historical UI startup/readiness defect.
- `ERR-0014` remains STALE absent exact-current Qt SIGSEGV reproduction.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including one-token boundary; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
