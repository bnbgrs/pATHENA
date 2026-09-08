# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@e6ed6eba803e4084b5e5aeaa2ad576dccdaf9961`.
- Error branch mutation lineage: `postmerge/errors` only.
- Exact Develop verification anchor: `270f97c36bd114036658e322f68d8011983ff150`, canonical Quality `34248696450 = SUCCESS`.
- Backend current: `postmerge/backend@75e45f99ce60b87e0b56ea024d3bed931ec461d4`; canonical Quality `34251875708` is in progress and already shows Validator PASS, Ruff FAIL, mypy PASS, Linux storage PASS, Local install PASS, Windows path safety PASS.
- Backend v41 candidate product fix: `69e2a4707bba544af5d2d2ae53daffc1dbf786a3`; its first Quality run `34251782009` was cancelled before verification.
- UI exact product head `b0c74459af0d6382f23106819f34778c86b6f18b` remains canonical green via `34240229731`.
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
- Repro signatures: `tests/unit/test_wal_job_hook.py`, `test_wal_maintenance_interval_runner.py`, `test_wal_schedule_overflow.py`, `test_wal_scheduler_dependency_boundary.py`; failures require canonical `DurableJobScheduler` / `WalMaintenanceOrchestrator` and include two stale dependency-error regex expectations.
- Root cause: harness collaborators/expectations drifted behind intentional exact-type fail-closed production contracts. Production guards must not be weakened.
- Fix SHA: none yet.
- Verification required: focused WAL suites plus Ruff/mypy and exact canonical Quality.

## ERR-0028 — v41 legacy schema fixtures/current-version assertions remain v40-shaped

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: Backend Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` completed with `51 failed, 4793 passed, 3 skipped`.
- Root cause: stale fresh/current assertions still expect schema v40 / migration `0040_grounded_response_receipts`; multiple legacy v30-v40 fixture builders already include v41-only `research_delta_boundaries`, causing the real v40→v41 migration to correctly raise `sqlite3.OperationalError: table research_delta_boundaries already exists`.
- Required fix: repair only stale harness expectations and legacy fixture construction; keep the additive/transactional production migration strict.
- Fix SHA: none yet.
- Verification required: representative fresh and v30/v35/v38/v39/v40→v41 migration/restart suites plus canonical Quality.

## ERR-0027 — v41 schema contract constant not re-exported by `athena.storage.schema`

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact red evidence: `34245022980` failed `tests/unit/test_schema_contract_boundary.py::test_schema_reexports_contract_constants` with missing `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`.
- Root cause: `src/athena/storage/schema.py` wired v41 migration but omitted the established schema-facade re-export.
- Candidate product fix: `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` re-exports the real v41 migration/schema constants. First exact run `34251782009` was cancelled; successor Quality `34251875708` on `75e45f99ce60b87e0b56ea024d3bed931ec461d4` is still running. Do not mark fixed until focused/full verification is available.
- Fix SHA: candidate `69e2a4707bba544af5d2d2ae53daffc1dbf786a3`.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2.
- Status: `IN_PROGRESS`.
- Original exact diagnostic: Quality `34245022980` on `4e61cba775a4b9b88cd40b33d9c0e33b4eb9fc66` reported one fixable `I001` in `src/athena/storage/schema.py`.
- Candidate correction `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` attempted canonical import consolidation/reordering.
- Hard verification result this run: successor canonical Quality `34251875708` on exact Backend head `75e45f99ce60b87e0b56ea024d3bed931ec461d4` has already completed Ruff with `FAIL`; Validator and mypy are PASS, while Linux storage, Local install and Windows path safety are also PASS. Therefore the attempted correction is not verified and `ERR-0026` remains active. Exact successor Ruff diagnostic must be consumed before another mutation; do not assume it is the same I001 without diagnostic evidence.
- Fix SHA: none verified.

## ERR-0025 — older shared-baseline canonical full-pytest failure family

- Severity: P2.
- Status: `STALE`.
- Initial exact evidence: Backend `34195601115` on `ea601b96d681580c2e8f1f1af40c7d97c347511e`, later reproduced across independent Backend/UI lineages as pytest-only red.
- The later v41 failures were decomposed separately into `ERR-0027` through `ERR-0029` and must not be folded back into this ID.
- Clearing evidence: exact Develop descendant `270f97c36bd114036658e322f68d8011983ff150` completed canonical Quality `34248696450 = SUCCESS`, providing the required exact green descendant. No current shared-baseline pytest-only signature remains reproduced on that verified Develop SHA.
- Root cause attribution remains non-unique because multiple accepted lineage changes occurred before the clearing run; this historical family is therefore `STALE`, not claimed as a uniquely root-caused product fix. Reopen only on a new exact-current reproduction.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `FIXED`.
- Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; later descendants remained green.
- Root cause: harness identity/lifecycle acceptance drift; source-order repair plus final teardown/lifecycle repair.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED`.
- Failing evidence: Backend Quality `34177086068` on `076a0d1209fe1cb30c6cfe7f6735a39158036c28` failed the Jobs lifecycle terminal-copy assertion.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()`.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`; Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9`.
- Exact verification: Develop SHA `270f97c36bd114036658e322f68d8011983ff150` contains blob `a661beaa6cbcc4fe35178e24d1f56de8db7d9ff9` with terminal text `This job is {state}; no actions are available.` and canonical Quality `34248696450` completed `SUCCESS`. This satisfies the exact-Develop verification requirement.
- Fix SHA: `d0207d43dabd66406df630a2cdff89e6f56b259b`.

## Historical verified entries

- `ERR-0004` P2 FIXED — UI startup/readiness harness Ruff B010/I001; no current recurrence. Backend schema Ruff remains distinct `ERR-0026`.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
