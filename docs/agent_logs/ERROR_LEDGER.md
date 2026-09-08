# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@ee940a135e0859b3d880d44d873260f0617b17f4`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `1c15db07e5342b5322fee374461dcfe7f2b4a0e7`, parents prior Error head `d15f50e3e4197e247e1111e86aa33cd80d0e5309` and current Develop `ee940a135e0859b3d880d44d873260f0617b17f4`.
- Spec/Core exact-green repair head reviewed: `772c2bfdc8767b7c0d032dbb8709120de635f6c0`; current Spec/Core documentation descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`.
- Backend failing head reviewed: `ea601b96d681580c2e8f1f1af40c7d97c347511e`.
- UI current head reviewed: `de3ae27e58e41e478648a368d37d1bba160bfc7a`.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- IN_PROGRESS: `ERR-0025`.
- OPEN/BLOCKED: none.

## ERR-0025 — Backend canonical full-pytest failure on WAL adapter boundary lineage

- Severity: P2.
- Status: `IN_PROGRESS`.
- Exact evidence: canonical Backend Quality `34195601115` on `postmerge/backend@ea601b96d681580c2e8f1f1af40c7d97c347511e` completed `failure`.
- Gate split: Local install smoke PASS; Windows path safety PASS; Linux storage regressions PASS; specification validator PASS; Ruff PASS; mypy PASS; only `Quality — pytest` FAIL; canonical diagnostics upload PASS.
- Deduplication proof: this exact Backend SHA does not contain `tests/unit/test_exhaustive_research_unavailable_nas.py` (GitHub contents lookup returns 404), therefore the failure cannot be the §72 acceptance failure tracked as `ERR-0024`.
- Backend handoff identifies the bounded product lineage as `WalJobSchedulerHook` exact-type hardening / `tests/unit/test_wal_scheduler_adapter_boundary.py`, but no failure may be attributed to that product slice without the exact pytest assertion.
- Root cause: not yet finalized. The available GitHub connector exposes the failing pytest step and successful diagnostics upload but not the traceback payload; no speculative product-vs-harness mutation is permitted.
- Repro: run full canonical pytest on exact `ea601b96d681580c2e8f1f1af40c7d97c347511e`; failure is reproducible in canonical run `34195601115`.
- Affected files: unknown until exact assertion/traceback is obtained; do not pre-assign to WAL product code.
- Fix SHA: none.
- Verification: none; no PASS claimed.
- Risks: a distinct shared-suite or Backend-lineage failure remains unresolved; Develop is not globally promotion-ready on the basis of worker greens alone.
- Integrator handoff: hold the failing Backend lineage until the exact pytest assertion is root-caused or a concrete exact-green successor proves the failure cleared; deduplicate before allocating any further ERR.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `FIXED`.
- Initial exact evidence: canonical Quality `34186455107` on `postmerge/spec-core@5fbe0dc8b3d7674a18c562e96c118ddf4e476985`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest FAIL only.
- Root cause: harness identity/lifecycle acceptance drift. The original acceptance bound state to work-list order rather than exact source identity; after exact source-ID repair a remaining teardown/lifecycle defect persisted. The corrected acceptance lineage culminated at `772c2bfdc8767b7c0d032dbb8709120de635f6c0`.
- Fix lineage: initial source-identity repair `124bdd9d789230d33452cfbc2452b307d410316c`; final exact-green corrective successor `772c2bfdc8767b7c0d032dbb8709120de635f6c0`.
- Real verification: canonical Quality `34198674038` on exact `772c2bfdc8767b7c0d032dbb8709120de635f6c0` completed `success`. Windows path safety PASS, Local install smoke PASS, Linux storage PASS, specification validator PASS, Ruff PASS, mypy PASS, full pytest PASS, diagnostics upload PASS and canonical result enforcement PASS.
- Integrator evidence: exact verified §72 acceptance was integrated to Develop by `7d39c25faf93068f3363b68e9bac7d4c4e93ac89`; current Develop descends from it.
- Affected file: `tests/unit/test_exhaustive_research_unavailable_nas.py`; no product-code weakening.
- Risks: none for this signature absent exact recurrence. Historical red descendants before `772c2bfd...` remain superseded evidence, not current failures.
- Integrator handoff: clear the `ERR-0024` hold; preserve exact source identity, UNAVAILABLE-not-IRRELEVANT semantics, processed=3, failed=0, coverage=2/3 and durable-state assertions.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: canonical Backend Quality `34177086068` on exact `076a0d1209fe1cb30c6cfe7f6735a39158036c28`; full pytest only failed at `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because visible copy was `no lifecycle action is available`.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()` exposed implementation-oriented wording; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop `ee940a135e0859b3d880d44d873260f0617b17f4` retains the corrected product blob `src/athena/desktop/jobs_lifecycle.py@a661beaa6cbcc4fe35178e24d1f56de8db7d9ff9`.
- Exact verification remains pending because no completed canonical Quality run on a current Develop descendant has yet been consumed as exact verification of the integrated Error wording. Current UI Quality `34200490506` on `de3ae27e58e41e478648a368d37d1bba160bfc7a` is still in progress and is not counted as PASS.

## Current worker evidence — 2026-09-08

- Spec/Core `772c2bfdc8767b7c0d032dbb8709120de635f6c0`: Quality `34198674038 = success`; `ERR-0024` closed. Documentation-only/current successor `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` has Quality `34198712540` still in progress; no additional defect inferred.
- Backend `ea601b96d681580c2e8f1f1af40c7d97c347511e`: Quality `34195601115 = failure`, pytest-only with all other canonical gates green; tracked as distinct `ERR-0025` because the §72 test does not exist on that SHA.
- UI `de3ae27e58e41e478648a368d37d1bba160bfc7a`: Quality `34200490506` is in progress; no conclusion inferred.
- Develop `ee940a135e0859b3d880d44d873260f0617b17f4` has no exact completed canonical Quality success establishing global promotion readiness.
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
