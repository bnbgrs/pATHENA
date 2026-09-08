# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA evidenced failures are opened; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, weakened assertion, Ruff/mypy/Validator relaxation, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Baseline reviewed: `develop/pathena-next@df05e76c998148e2445401de04115a7c5dccd708`.
- Error branch mutation lineage: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `e0c77705ad30102c612a1e8706e769f77f5d8951`, parents prior Error head `bfefb4fcd9f87e4587984e96689009366be77361` and current Develop `df05e76c998148e2445401de04115a7c5dccd708`.
- Current Spec/Core head reviewed: `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00`.
- Current Backend head reviewed: `5fb145df421059314b4d90f53b9fc69b1c4333ab`.
- Current UI head reviewed: `4c656c2c5dfb55e6d3f0078719183cbbad73a555`.
- `main` and `bnbgrs/ATHENA` remained read-only and untouched.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- IN_PROGRESS: `ERR-0024`.
- OPEN/BLOCKED: none.

## ERR-0024 — Spec/Core §72 unavailable-NAS acceptance full-pytest failure

- Severity: P2.
- Status: `IN_PROGRESS`.
- Initial exact evidence: canonical Quality `34186455107` on `postmerge/spec-core@5fbe0dc8b3d7674a18c562e96c118ddf4e476985`; Local install, Windows path safety, Linux storage, Validator, Ruff and mypy PASS; full pytest FAIL only.
- Concrete root-cause progress: inspection proved the original acceptance bound SUCCESSFUL/IRRELEVANT/UNAVAILABLE to `work[0..2]` ordering and therefore did not prove the UNAVAILABLE work item belonged to the NAS source. Work-item list order is not source identity.
- Owner repair: `124bdd9d789230d33452cfbc2452b307d410316c` changes only `tests/unit/test_exhaustive_research_unavailable_nas.py`, resolving each work item through candidate -> exact `source_id`, selecting the actual NAS work item, preserving all coverage/durability assertions.
- Verification of repair: canonical Quality `34190083267` on exact `124bdd9d789230d33452cfbc2452b307d410316c` again failed only full pytest; Validator/Ruff/mypy/Windows path/Linux storage/local install all PASS. Therefore the demonstrated ordering defect is fixed but is not sufficient to close the canonical failure.
- Current unchanged handoff descendant `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` has Quality `34190114472` still in progress; no PASS inferred.
- Exact remaining pytest assertion/traceback is still not exposed through the available diagnostics interface. No product-vs-second-harness classification is invented.
- Integrator handoff: HOLD §72 until an exact repaired successor completes canonical green; do not weaken exact source identity, unavailable-vs-irrelevant, 2/3 coverage or persistence assertions.

## ERR-0023 — Terminal Jobs action reason leaks implementation-oriented lifecycle wording

- Severity: P2.
- Status: `FIXED_PENDING_VERIFY`.
- Failing evidence: canonical Backend Quality `34177086068` on exact `076a0d1209fe1cb30c6cfe7f6735a39158036c28`; full pytest only failed at `tests/unit/test_pathena_jobs_lifecycle.py::test_action_availability_matches_durable_service_states[completed-enabled5]` because visible copy was `no lifecycle action is available`.
- Root cause: product copy in `src/athena/desktop/jobs_lifecycle.py::JobActionAvailability.reason()` exposed implementation-oriented wording; harness assertion valid.
- Minimal Error-owned fix: `d0207d43dabd66406df630a2cdff89e6f56b259b`, terminal copy -> `This job is {state}; no actions are available.`.
- Develop integration: `568d57a63bb2253d97ca63e92b52e1df66505ac9`; current Develop `df05e76c998148e2445401de04115a7c5dccd708` still contains exact corrected line/blob.
- Exact verification remains pending because no completed canonical Quality run is associated with a Develop descendant specifically verifying this integrated wording. Independent UI lineage previously cleared the same defect class but is not substituted for exact Error wording verification.

## Current worker evidence — 2026-09-08

- Spec/Core repair SHA `124bdd9d789230d33452cfbc2452b307d410316c`: Quality `34190083267 = failure`, pytest-only; current handoff SHA `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00`: Quality `34190114472 = in_progress`.
- Backend `5df50d524d4177a2fe157cf18cb952ff15df65a4`: Quality `34187200684 = failure`, pytest-only; all non-pytest canonical gates PASS. This is not allocated as a new ERR without exact assertion and may still deduplicate to an existing shared/full-suite defect. Current Backend `5fb145df421059314b4d90f53b9fc69b1c4333ab`: Quality `34190743330 = in_progress`.
- UI current `4c656c2c5dfb55e6d3f0078719183cbbad73a555`: Quality `34191944523 = pending`; no conclusion inferred.
- Develop `df05e76c998148e2445401de04115a7c5dccd708` has no exact completed canonical Quality success establishing global promotion readiness.
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
