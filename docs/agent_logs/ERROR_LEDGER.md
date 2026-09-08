# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization commit: `da6727cd60f56e6b88fbc7632712b04783637c84`, preserving prior Error head and exact Develop as two parents.
- Backend current: `255e73eae28651c20ae1baa660c4087f4a62f128`; Quality `34234185972 = in_progress` at review time. Functional predecessor `e81957a388763d3b5931df694a06908a0ba29f75` / `34233916176` was cancelled by successor, not clearing evidence.
- UI current reviewed: `932face973987d84a44c5d37fc61509285466279`.
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
- Initial exact evidence: Backend Quality `34195601115` on `ea601b96d681580c2e8f1f1af40c7d97c347511e`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; only full pytest FAIL; diagnostics upload PASS.
- Prior narrowing remains valid: Backend sync `8b04e8d5816fc908399d3e80a4407edd5fe50473` failed before WAL exact-type product commit `b90b96578146856f726208dcc1d562a26f6059b2`, excluding that mutation as primary cause.
- Backend descendants `8929474b6bdc4885c51e51de327816d5cf42137c` / `34206163937`, `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e` / `34211221630`, `aa9cb18188bf070ac4b9f0e2763e2b31c643a54f` / `34221259239`, and now `55a6e95486c8b7501f27ed07748dc922803025ea` / `34226856389` reproduce the pytest-only pattern.
- Exact new Backend evidence this run: Quality `34226856389` completed FAILURE on `55a6e95486c8b7501f27ed07748dc922803025ea`. Windows path safety PASS, Local install smoke PASS, Linux storage PASS, specification validator PASS, Ruff PASS, mypy PASS; only `Quality — pytest` failed; diagnostics upload PASS.
- Independent UI descendants `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723` / `34211448894`, `b9936b6e404c224c47230ced5919f475760c013a` / `34221783638`, and now `93367bc74dab77f8ffab65e7de538ee79fb5a72a` / `34227608407` reproduce the same canonical failure conclusion, strengthening cross-lineage deduplication rather than creating a new ERR.
- Root-cause boundary: persistent shared-suite/shared-baseline pytest defect until exact assertion evidence proves otherwise. WAL exact-type hardening is excluded as primary cause. Historical `ERR-0004` Ruff is excluded because current red lineages have Ruff PASS.
- Exact assertion/traceback remains unavailable through the readable connector surface. No speculative product-vs-harness mutation is permitted.
- Current Backend successor `255e73eae28651c20ae1baa660c4087f4a62f128` is under Quality `34234185972`; consume it next. If it turns green, diff the first clearing delta against nearest exact red. If red, obtain exact assertion evidence before mutation.
- Affected files: unknown until exact assertion or concrete clearing delta identifies them.
- Fix SHA: none.
- Verification: none; no PASS claimed.
- Remaining risks: global pytest instability blocks promotion confidence until exact root cause is identified or a concrete exact-green clearing successor is established.
- Integrator handoff: hold global promotion for `ERR-0025`; deduplicate new pytest-only worker reds under this ID unless exact evidence proves a distinct root cause.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `FIXED`.
- Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` passed `34198712540`; later `f4abb89d7538a11efa50d94a847b6f69139c602b` passed `34220174847`.
- Root cause: harness identity/lifecycle acceptance drift; source-order repair plus final teardown/lifecycle repair. No product-code weakening.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: Backend Quality `34177086068` on `076a0d1209fe1cb30c6cfe7f6735a39158036c28` failed `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because terminal visible copy exposed `lifecycle action` wording.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()`; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop retains the corrected product content.
- Exact verification remains pending because current Develop `9fb4f005ebb34f835f5a6c362965ad35cd2f3efb` has no completed exact canonical Quality success established in this run; worker pytest-only reds cannot be used as positive verification.
- Affected files: `src/athena/desktop/jobs_lifecycle.py`, `tests/unit/test_pathena_jobs_lifecycle.py`.
- Fix SHA: `d0207d43dabd66406df630a2cdff89e6f56b259b`.
- Integrator handoff: keep pending until an exact Develop descendant carrying the corrected wording is canonical green.

## Historical verified entries

- `ERR-0004` P2 FIXED — startup/readiness harness Ruff B010/I001; exact-green evidence retained; current worker Ruff PASS evidence confirms no recurrence.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss; verified green successor.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak; exact red-to-green successor.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping; exact canonical green.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.