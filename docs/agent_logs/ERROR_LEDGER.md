# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@249c83ae7dc4a33ceb8491029af4bad09b452e92`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `93c5aaaf4a250b17e83007d510923e0d94a5abed`, parents prior Error head `92893883bb34aff3aea2478c177ce67ce87877da` and current Develop `249c83ae7dc4a33ceb8491029af4bad09b452e92`.
- Current Spec/Core head reviewed: `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`; Quality `34198712540 = success`.
- Current Backend head reviewed: `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e`; Quality `34211221630 = in_progress`.
- Current UI head reviewed: `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723`; Quality `34211448894 = failure`, pytest-only.
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
- Prior narrowing remains valid: Backend sync `8b04e8d5816fc908399d3e80a4407edd5fe50473` failed `34205822004` before WAL exact-type product commit `b90b96578146856f726208dcc1d562a26f6059b2`, excluding that product mutation as primary cause.
- Hard progress this run: Backend descendant `8929474b6bdc4885c51e51de327816d5cf42137c` completed Quality `34206163937 = failure`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy all PASS and only full pytest FAIL. The failure therefore persists through a later Backend descendant rather than being a transient single-run artifact.
- Independent persistence: UI synchronization descendant `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723` completed Quality `34211448894 = failure`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS and only full pytest FAIL. This is a later independent UI reproduction after the earlier `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812` red.
- Deduplication remains mandatory: no separate Backend/UI ERR is allocated absent an exact distinct assertion. The repeated worker-lineage pattern strengthens classification as a shared-suite/shared-baseline failure.
- Exact assertion/traceback is still unavailable through the connector surface; job metadata exposes the failing `Quality — pytest` step and successful diagnostics upload, but not the UTF-8 traceback payload. No speculative product-vs-harness mutation is permitted.
- Current Backend `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e` is under canonical run `34211221630`; consume it next. If green, diff the first clearing delta; if red, use it as another exact persistence point and continue seeking the exact assertion.
- Affected files: unknown until exact assertion or a concrete clearing delta identifies them.
- Fix SHA: none.
- Verification: none; no PASS claimed.
- Integrator handoff: hold global promotion for `ERR-0025`; do not blame WAL exact-type hardening; deduplicate new pytest-only worker reds under `ERR-0025` unless exact evidence proves a distinct root cause.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `FIXED`.
- Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` passed `34198712540`.
- Root cause: harness identity/lifecycle acceptance drift; source-order repair plus final teardown/lifecycle repair. No product-code weakening.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: Backend Quality `34177086068` on `076a0d1209fe1cb30c6cfe7f6735a39158036c28` failed `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because terminal visible copy exposed `lifecycle action` wording.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()`; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop retains the corrected product content.
- Exact verification remains pending because current Develop `249c83ae7dc4a33ceb8491029af4bad09b452e92` has no completed exact canonical Quality run; worker pytest-only reds cannot be used as positive verification.

## Current worker evidence — 2026-09-08

- Spec/Core `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`: Quality `34198712540 = success`.
- Backend `8929474b6bdc4885c51e51de327816d5cf42137c`: Quality `34206163937 = failure`, pytest-only.
- Backend current `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e`: Quality `34211221630 = in_progress`.
- UI current `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723`: Quality `34211448894 = failure`, pytest-only; all non-pytest canonical gates PASS.
- Develop `249c83ae7dc4a33ceb8491029af4bad09b452e92`: no exact completed canonical Quality run.
- No exact-current evidence reproduced retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none reopened.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact-green evidence retained.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss; verified green successor.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak; exact red-to-green successor.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping; exact canonical green.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
