# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed and NON-FORCE synchronized: `develop/pathena-next@3421bee8f1ed00f1473a930b759cb7f272345d7e`.
- Error branch mutation lineage: `postmerge/errors` only; history-preserving two-parent synchronization commit `755f9ff9dcdebaf41297e471672cec207cfa287a` carries current Develop plus the canonical Error Ledger/Handoff.
- Exact Develop green anchor remains `270f97c36bd114036658e322f68d8011983ff150`, canonical Quality `34248696450 = SUCCESS`; current Develop `3421bee8f1ed00f1473a930b759cb7f272345d7e` has no PR-triggered canonical Quality run returned.
- Backend current: `postmerge/backend@4495cab0492f0c70e6d0b5cbda1136c1d960ab86`; canonical Quality `34281292370` is IN_PROGRESS. Its Ruff step is already completed FAILURE while Validator and mypy passed; Local install smoke, Linux storage regressions and Windows path safety also passed.
- The preceding product commit `95b077af9e8e648f67863d36b5ddbbc2ec19051c` attempted the `ERR-0026` import-only fix. Its Quality `34281237072` was cancelled because the Backend worker immediately pushed docs commit `4495cab0492f0c70e6d0b5cbda1136c1d960ab86`.
- Exact compare `95b077af...4495cab` contains only `docs/agent_handoffs/backend.md`; therefore the current Ruff failure is exact evidence against the product tree containing the attempted import reorder.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- STALE: `ERR-0014`, `ERR-0025`.
- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY: none.

## ERR-0029 — WAL test collaborators incompatible with canonical exact-type runtime guards

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend canonical Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` failed a bounded WAL cluster while platform/install/static gates otherwise passed apart from independent Ruff `ERR-0026`.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards must not be weakened.
- Worker candidate: `c8b12bb2bd0362540c8a9474aecb27a6e168c6d1` repairs one exact dependency-boundary cluster only in `tests/unit/test_wal_scheduler_dependency_boundary.py`: it expects the current canonical `DurableJobScheduler` diagnostic and uses a real canonical scheduler with inert typed dependencies before testing the invalid WAL-hook boundary. Production `type(...) is ...` guards remain unchanged.
- Verification: Backend handoff reports predecessor `34276050284@8fd7fd305d027f7367de01e53e95e255801a99f7` completed FAILURE with pytest improved to `49 failed, 4799 passed, 3 skipped`, proving the dependency-boundary repair removed two failures but did not close the wider WAL/schema harness set. Current exact successor `34281292370@4495cab0492f0c70e6d0b5cbda1136c1d960ab86` remains IN_PROGRESS.
- Remaining scope: other WAL harness collaborators/diagnostic expectations may still require conversion to canonical concrete `DurableJobScheduler` / `WalMaintenanceOrchestrator` collaborators or explicit fail-before-side-effect assertions.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` completed with `51 failed, 4793 passed, 3 skipped`; later Backend handoff reports `34276050284` improved to `49 failed, 4799 passed, 3 skipped` after an independent WAL harness repair.
- Root cause: stale fresh/current assertions still expect schema v40 / migration `0040_grounded_response_receipts`; multiple legacy v30-v40 fixture builders already include v41-only `research_delta_boundaries`, causing the real v40→v41 migration to correctly raise `sqlite3.OperationalError: table research_delta_boundaries already exists`.
- Required fix: repair only stale harness expectations and legacy fixture construction; keep the additive/transactional production migration strict.
- Current verification: exact Backend descendant Quality `34281292370@4495cab0492f0c70e6d0b5cbda1136c1d960ab86` is IN_PROGRESS; no status change before assertion-level evidence.
- Fix SHA: none verified.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact red evidence: `34245022980` failed `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` with missing `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Root cause: `src/athena/storage/schema.py` wired v41 migration but omitted the established schema-facade re-export.
- Candidate fix lineage: `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` plus descendants; current Backend tree visibly re-exports both `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Verification: candidate-fixed only. Exact descendant Quality `34281292370` remains IN_PROGRESS; require focused schema-contract evidence or completed canonical pytest evidence before FIXED.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2.
- Status: `IN_PROGRESS`.
- Original exact diagnostic: Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` reported one fixable `I001` in `src/athena/storage/schema.py`.
- Root cause class: canonical import ordering in the consolidated `from athena.storage.schema_contract import (...)` block. Product semantics are not implicated.
- Disproven correction: commit `95b077af9e8e648f67863d36b5ddbbc2ec19051c` moved `DatabaseCompatibilityError` from the uppercase `CONSOLIDATED_*` / `DELETION_*` region to immediately after `_user_tables`. That tree is preserved unchanged in successor `4495cab0492f0c70e6d0b5cbda1136c1d960ab86`; exact compare shows the only successor change is `docs/agent_handoffs/backend.md`.
- New exact evidence: canonical Quality `34281292370@4495cab0492f0c70e6d0b5cbda1136c1d960ab86` has completed Ruff = FAILURE while Validator = PASS and mypy = PASS; pytest is still running. Therefore the previous handoff's specific claim that the `_user_tables` move was the formatter-proven final correction is false and is retired.
- Required next step: consume the diagnostics artifact from `34281292370` after the run completes and use its exact current Ruff diff/rule before any further mutation. Do not guess a second ordering change. If the diagnostic remains the same `schema.py` I001, apply only the exact formatter output in Backend-owned scope and verify Ruff before broader tests.
- CI-discipline note: Quality `34281237072` on the product commit was cancelled by the immediate docs push; current run `34281292370` is the authoritative exact verification point and must not be disturbed by further Backend pushes until completion.

## ERR-0025 — older shared-baseline canonical full-pytest failure family

- Severity: P2.
- Status: `STALE`.
- Clearing evidence: exact Develop descendant `270f97c36bd114036658e322f68d8011983ff150` completed canonical Quality `34248696450 = SUCCESS`. Later v41 failures are separately tracked as `ERR-0027` through `ERR-0029`.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2. Status: `FIXED`. Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`.

## ERR-0023 — Terminal Jobs action reason lifecycle wording

- Severity: P2. Status: `FIXED`.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`; Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9`.
- Exact verification: Develop `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.

## Historical verified entries

- `ERR-0004` P2 FIXED — UI startup/readiness harness Ruff B010/I001; no current recurrence. Backend schema Ruff is distinct `ERR-0026`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping.
- `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0018` remain FIXED per prior exact verification records.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.