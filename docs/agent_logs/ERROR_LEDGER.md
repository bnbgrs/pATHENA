# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `b560dfcfbae9313e06105829d1de027200a0f30d`, parents prior Error head `54abf5b205473c29b1c757442b9e6db09ee68e2c` and current Develop `cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9`.
- Current Spec/Core head reviewed: `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`; Quality `34198712540 = success`.
- Current Backend head reviewed: `8929474b6bdc4885c51e51de327816d5cf42137c`; Quality `34206163937 = in_progress`.
- Current UI head reviewed: `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812`; Quality `34205607335 = failure`, pytest-only.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- IN_PROGRESS: `ERR-0025`.
- OPEN/BLOCKED: none.

## ERR-0025 — Shared baseline canonical full-pytest failure, exact assertion pending

- Severity: P2.
- Status: `IN_PROGRESS`.
- Initial exact evidence: Backend Quality `34195601115` on `postmerge/backend@ea601b96d681580c2e8f1f1af40c7d97c347511e`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; only full pytest FAIL; diagnostics upload PASS.
- Hard progress this run: the failure is no longer attributable to the later WAL-hook exact-type hardening. Backend synchronization head `8b04e8d5816fc908399d3e80a4407edd5fe50473` already failed canonical Quality `34205822004` before product commit `b90b96578146856f726208dcc1d562a26f6059b2`; the WAL product commit's run `34206067801` was cancelled and therefore provides no clearing evidence.
- Independent deduplication: UI synchronization head `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812`, which shares the same Develop lineage but does not contain the Backend WAL-hook product mutation, also fails canonical Quality `34205607335` only at full pytest while Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS.
- Therefore the primary defect is a shared-suite/shared-baseline pytest failure already present across independently synchronized worker lineages, not the WAL-hook exact-type product slice. No second UI ERR is allocated from `34205607335` without an exact distinct assertion.
- Exact assertion/traceback remains unavailable through the current connector surface; diagnostics artifacts exist but their payload is not exposed as UTF-8 content. No speculative product-vs-harness mutation is permitted.
- Repro evidence: `34195601115`, `34205822004`, and `34205607335` are exact canonical pytest-only reds on separate worker descendants. Current Backend `8929474b6bdc4885c51e51de327816d5cf42137c` is being checked by `34206163937` and must be consumed when complete.
- Affected files: unknown until exact assertion or a concrete clearing delta identifies them.
- Fix SHA: none.
- Verification: none; no PASS claimed.
- Integrator handoff: do not hold the WAL exact-type product slice as the presumed root cause solely because of `ERR-0025`; instead hold global promotion until the shared pytest failure is identified or an exact-green current descendant clears it. Deduplicate any new worker pytest-only red against this entry first.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `FIXED`.
- Initial exact evidence: Quality `34186455107` on `postmerge/spec-core@5fbe0dc8b3d7674a18c562e96c118ddf4e476985`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest FAIL only.
- Root cause: harness identity/lifecycle acceptance drift. Source-order binding was repaired by `124bdd9d789230d33452cfbc2452b307d410316c`; final teardown/lifecycle repair reached `772c2bfdc8767b7c0d032dbb8709120de635f6c0`.
- Real verification: Quality `34198674038` on exact `772c2bfdc8767b7c0d032dbb8709120de635f6c0 = success`; current Spec/Core documentation descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` also completed Quality `34198712540 = success`.
- Integrator evidence: exact verified acceptance integrated to Develop by `7d39c25faf93068f3363b68e9bac7d4c4e93ac89`.
- Affected file: `tests/unit/test_exhaustive_research_unavailable_nas.py`; no product-code weakening.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: Backend Quality `34177086068` on exact `076a0d1209fe1cb30c6cfe7f6735a39158036c28`; full pytest failed at `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because terminal visible copy exposed `lifecycle action` wording.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()`; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop `cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9` retains corrected product blob `src/athena/desktop/jobs_lifecycle.py@a661beaa6cbcc4fe35178e24d1f56de8db7d9ff9`.
- Exact verification remains pending: current Develop has no associated completed canonical Quality run, and the current UI lineage is pytest-only red rather than a valid verification surface.

## Current worker evidence — 2026-09-08

- Spec/Core `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`: Quality `34198712540 = success`; no new error signal.
- Backend `8b04e8d5816fc908399d3e80a4407edd5fe50473`: Quality `34205822004 = failure`; failure predates WAL exact-type product commit, narrowing `ERR-0025` away from that product slice.
- Backend current `8929474b6bdc4885c51e51de327816d5cf42137c`: Quality `34206163937 = in_progress`.
- UI `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812`: Quality `34205607335 = failure`; Local install, Linux storage, Windows path safety, Validator, Ruff and mypy PASS; only full pytest FAIL. Deduplicated under `ERR-0025` absent a distinct exact assertion.
- Develop `cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9`: no exact completed canonical Quality run; no global promotion-ready claim.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact-green evidence retained.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss; verified green successor.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak; exact red-to-green successor.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping; exact canonical green.
- All other prior FIXED entries retain their recorded evidence.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
