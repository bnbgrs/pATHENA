# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `develop/pathena-next@b04b0107f55d8af8b0398e48066481a84d27775f`.
- Error branch synchronized NON-FORCE/history-preserving to that Develop via merge commit `46f3f7c35e2623c499d5c24735bf70219ac81443`; own mutations remain on `postmerge/errors` only.
- Current workers reviewed: Backend `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837`; Spec/Core `06b121edfcc80d0a9e50ffa4173baaea8060d3f9`; UI `2b54226815b0bb3b49832f1d64f1ac5b46716d41`.
- Integrator handoff on current Develop reports Spec/Core Quality `34285298078 = SUCCESS`, Backend Quality `34286119711 = FAILURE`, and UI Quality `34287102867` pending at that review point.
- Current direct check confirms UI Quality `34287102867@2b54226815b0bb3b49832f1d64f1ac5b46716d41` remains `IN_PROGRESS`.
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
- Earlier exact evidence: Backend Quality `34276050284@8fd7fd305d027f7367de01e53e95e255801a99f7` improved to `49 failed, 4799 passed, 3 skipped` after the dependency-boundary harness repair, proving that subcluster removed two failures without closing the wider WAL/schema set.
- Current bounded Backend candidate: `e3c96cbdb2b04b90179bcc743ccaf20c6f26b837`. Relative to predecessor `4495cab0492f0c70e6d0b5cbda1136c1d960ab86`, its Backend-owned WAL repair changes `tests/unit/test_wal_maintenance_interval_runner.py` and `tests/unit/test_wal_schedule_overflow.py` to use canonical `WalMaintenanceOrchestrator` instances; production WAL code/type guards are unchanged. The same candidate also history-preservingly carries current Develop DirectChat files and its Backend handoff.
- New exact completed evidence: canonical Quality `34286119711@e3c96cbdb2b04b90179bcc743ccaf20c6f26b837 = FAILURE`. Windows path safety, Linux storage regressions and Local install smoke passed. Python quality: specification validator PASS, mypy PASS, Ruff FAIL, full pytest FAIL; diagnostics artifact `10080190842` uploaded successfully.
- Interpretation: the candidate is **not** globally verified and `ERR-0029` cannot be marked FIXED. This run records the completed exact result rather than the prior pending state. The available connector exposes the artifact metadata but not its binary diagnostic payload, so no assertion-level claim is made that the two orchestrator-focused tests themselves passed or failed.
- Remaining scope known from Backend handoff: fake-`DurableJobScheduler` cases in `test_wal_job_hook.py` remain separate pending work inside `ERR-0029`; continue only with exact diagnostics/focused evidence and canonical concrete collaborators or fail-before-side-effect assertions.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2. Status: `IN_PROGRESS`.
- Exact evidence family: stale fresh/current assertions expect schema v40 / migration `0040_grounded_response_receipts`; legacy v30-v40 fixtures already contain v41-only `research_delta_boundaries`, causing the strict real v40→v41 migration to raise `table research_delta_boundaries already exists`.
- Required fix remains harness-only: truthful v41 expectations and legacy fixture construction; production migration remains additive, transactional and fail-closed.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2. Status: `IN_PROGRESS`.
- Original exact red: Quality `34245022980` failed `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` with missing `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Current Backend tree visibly re-exports both Research Delta contract constants, but no independent focused/current canonical passing assertion is available in this run; no FIXED claim.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2. Status: `IN_PROGRESS`.
- Exact rule/file family: Ruff `I001` in `src/athena/storage/schema.py`.
- Candidate `95b077af9e8e648f67863d36b5ddbbc2ec19051c` was disproven by exact successor Quality `34281292370` with unchanged product tree and Ruff still red.
- Current Backend Quality `34286119711@e3c96cbdb2b04b90179bcc743ccaf20c6f26b837` again has Ruff FAILURE. Do not guess another ordering change without the exact current diagnostic/formatter diff.

## Cleared historical state relevant to integration

- `ERR-0023` FIXED: exact Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- `ERR-0025` STALE after that exact-green Develop descendant.
- `ERR-0004` remains FIXED; current Ruff red is Backend schema `ERR-0026`, not the historical UI startup/readiness defect.
- `ERR-0014` remains STALE absent exact-current Qt SIGSEGV reproduction.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including one-token boundary; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
