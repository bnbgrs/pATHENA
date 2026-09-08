# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@4f077e36248a49d261f13d3f3838d62a376f506f`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization commit: `53cf8bc4a6a40988a5bc40414c704d1cf2ea9694`, preserving prior Error head and exact Develop as parents.
- Backend current: `00b630e4915ec85abc08252d85e6403009b48858`; canonical Quality `34239827573` is in progress. Exact current job evidence already shows specification validator PASS, Ruff FAIL, mypy PASS, Local install PASS, Linux storage PASS, Windows path safety PASS; full pytest still running at review time.
- UI current: `b0c74459af0d6382f23106819f34778c86b6f18b`; Integrator already imported the bounded three-line Jobs status-copy skip removal onto Develop as `cbfe6d65e424f83b9c39d0d8ecf9af1aaffbf66a`, then documented it in current Develop head.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- IN_PROGRESS: `ERR-0025`, `ERR-0026`.
- OPEN/BLOCKED: none.

## ERR-0026 — Backend v41 schema module canonical Ruff I001

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact current evidence: canonical Backend Quality `34239827573` on `00b630e4915ec85abc08252d85e6403009b48858` has `Quality — Ruff = failure` while specification validator, mypy, Local install smoke, Linux storage regressions and Windows path safety are PASS. Full pytest remains in progress, so this entry is scoped only to the independently proven Ruff defect.
- Root cause finalized from the immediately preceding exact Backend diagnostic lineage: Quality `34234185972` on `255e73eae28651c20ae1baa660c4087f4a62f128` reported exactly one Ruff `I001` import-order failure in `src/athena/storage/schema.py`. Backend handoff for current head `00b630e4915ec85abc08252d85e6403009b48858` explicitly records that this Ruff defect remains to be repaired after the two mypy regressions were corrected.
- This is distinct from `ERR-0025`: current Ruff failure is an exact, file-identified lint defect, while `ERR-0025` tracks the cross-lineage full-pytest failure. It is also not recurrence of historical `ERR-0004`, whose file/scope was the UI startup/readiness harness.
- Affected file: `src/athena/storage/schema.py` on the Backend v41 lineage.
- Required minimal fix: import-order-only correction satisfying Ruff I001; no product semantics, schema invariants, tests or guards may be changed.
- Fix SHA: none yet.
- Verification required: exact corrected Backend SHA with Ruff PASS plus focused v40→v41/restart/schema checks and canonical Quality. Do not mark FIXED from a documentation-only descendant.
- Integrator handoff: do not integrate the v41 Backend slice while `ERR-0026` remains Ruff-red; consume the Backend worker's minimal import-order correction and exact verification first.

## ERR-0025 — Shared baseline canonical full-pytest failure / now partially decomposed

- Severity: P2.
- Status: `IN_PROGRESS`.
- Initial exact evidence: Backend Quality `34195601115` on `ea601b96d681580c2e8f1f1af40c7d97c347511e`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; only full pytest FAIL; diagnostics upload PASS.
- Cross-lineage persistence was reproduced by multiple Backend and UI descendants through Backend `55a6e95486c8b7501f27ed07748dc922803025ea` / `34226856389` and UI `93367bc74dab77f8ffab65e7de538ee79fb5a72a` / `34227608407`.
- New Backend diagnostics from exact predecessor `255e73eae28651c20ae1baa660c4087f4a62f128` / `34234185972` expose a larger v41-specific pytest set (`51 failed, 4793 passed, 3 skipped`) containing schema-expectation/legacy-fixture failures plus WAL exact-type compatibility failures. Those concrete failures are not to be blindly collapsed into the older shared-baseline hypothesis; primary causes must be separated as exact assertions become available.
- WAL exact-type product hardening remains excluded as the original shared failure's primary cause because a predecessor already failed before that mutation.
- Current Backend `34239827573` is still running pytest; consume its completed result before changing this entry further.
- Fix SHA: none.
- Integrator handoff: hold global promotion; deduplicate only genuinely identical pytest signatures, and split exact v41 schema/fixture or WAL compatibility failures when assertion-level evidence proves separate primary causes.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `FIXED`.
- Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; descendants `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` / `34198712540` and `f4abb89d7538a11efa50d94a847b6f69139c602b` / `34220174847` remained green.
- Root cause: harness identity/lifecycle acceptance drift; source-order repair plus final teardown/lifecycle repair. No product-code weakening.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: Backend Quality `34177086068` on `076a0d1209fe1cb30c6cfe7f6735a39158036c28` failed `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because terminal visible copy exposed `lifecycle action` wording.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()`; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop retains the corrected product content.
- Exact Develop canonical success remains pending; do not infer FIXED from worker-lineage evidence.
- Affected files: `src/athena/desktop/jobs_lifecycle.py`, `tests/unit/test_pathena_jobs_lifecycle.py`.
- Fix SHA: `d0207d43dabd66406df630a2cdff89e6f56b259b`.

## Historical verified entries

- `ERR-0004` P2 FIXED — UI startup/readiness harness Ruff B010/I001; exact-green evidence retained. Current Backend Ruff defect is `ERR-0026`, not recurrence.
- `ERR-0014` P1 STALE — Qt Desktop controller SIGSEGV; reopen only on exact recurrence.
- `ERR-0019` P2 FIXED — Personal Memory precedence harness drift.
- `ERR-0020` P2 FIXED — exhaustive-research resume harness identity loss; verified green successor.
- `ERR-0021` FIXED — Jobs status-copy constructor-refresh monkeypatch leak; exact red-to-green successor.
- `ERR-0022` FIXED — Spec/Core Ruff import grouping; exact canonical green.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, explicitly execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim is allowed while a known crash signature is reproducible on that candidate.
