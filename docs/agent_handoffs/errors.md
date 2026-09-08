# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@ee940a135e0859b3d880d44d873260f0617b17f4`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE sync this run: `1c15db07e5342b5322fee374461dcfe7f2b4a0e7`.
- Exact-green Spec/Core repair head: `772c2bfdc8767b7c0d032dbb8709120de635f6c0`; current handoff descendant: `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`.
- Current Backend failing head: `ea601b96d681580c2e8f1f1af40c7d97c347511e`.
- Current UI head: `de3ae27e58e41e478648a368d37d1bba160bfc7a`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Initial exact failure: Spec/Core `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`, Quality `34186455107`; only full pytest failed.

The source-identity defect was repaired by `124bdd9d789230d33452cfbc2452b307d410316c`; a second teardown/lifecycle acceptance defect remained on intermediate descendants. The final corrected lineage reached `772c2bfdc8767b7c0d032dbb8709120de635f6c0`.

Real verification is now complete: Quality `34198674038` on exact `772c2bfdc8767b7c0d032dbb8709120de635f6c0` completed `success`. Windows path safety, Local install smoke, Linux storage, specification validator, Ruff, mypy and full pytest all passed; diagnostics upload and canonical result enforcement also passed.

Integrator imported the exact verified acceptance into Develop via `7d39c25faf93068f3363b68e9bac7d4c4e93ac89`. Clear the prior `ERR-0024` hold. Preserve candidate -> exact source identity, exact NAS UNAVAILABLE-not-IRRELEVANT state, processed=3, failed=0, unavailable=1, irrelevant=1, coverage=2/3 and durable-state assertions.

## ERR-0025 — Backend pytest-only failure — IN_PROGRESS

Canonical Backend Quality `34195601115` on exact `ea601b96d681580c2e8f1f1af40c7d97c347511e` completed `failure`.

Evidence split: Local install PASS; Windows path safety PASS; Linux storage PASS; specification validator PASS; Ruff PASS; mypy PASS; only full pytest FAIL; diagnostics upload PASS.

This is demonstrably distinct from `ERR-0024`: `tests/unit/test_exhaustive_research_unavailable_nas.py` does not exist on exact Backend SHA `ea601b96d...`, so the §72 acceptance cannot be the failing test in `34195601115`.

Backend handoff associates the candidate lineage with exact-type hardening around `WalJobSchedulerHook` / `tests/unit/test_wal_scheduler_adapter_boundary.py`, but Error does not attribute the failing pytest to that product slice without the exact assertion. The connector exposes the failing pytest step but not the uploaded traceback payload. No speculative patch is permitted.

Next admissible progress: consume the exact pytest assertion/traceback or a concrete corrected Backend successor. Then finalize product-vs-harness root cause and either apply the minimal Error-owned fix or verify the owner mutation. Do not merely repeat the generic pytest-only description.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Root cause remains product copy in `src/athena/desktop/jobs_lifecycle.py`; Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.`. Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` is an ancestor of current Develop `ee940a135e0859b3d880d44d873260f0617b17f4`, which retains product blob `a661beaa6cbcc4fe35178e24d1f56de8db7d9ff9`.

Status remains `FIXED_PENDING_VERIFY`: no completed exact-current Develop canonical Quality has yet been consumed to establish the integrated Error wording. Current UI Quality `34200490506` on `de3ae27e58e41e478648a368d37d1bba160bfc7a` remains in progress and is not treated as PASS.

## Current worker evidence

- Spec/Core `772c2bfdc8767b7c0d032dbb8709120de635f6c0` -> Quality `34198674038 = success`; `ERR-0024` closed. Current documentation descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` -> Quality `34198712540 = in_progress`.
- Backend `ea601b96d681580c2e8f1f1af40c7d97c347511e` -> Quality `34195601115 = failure`, pytest-only; distinct `ERR-0025`.
- UI `de3ae27e58e41e478648a368d37d1bba160bfc7a` -> Quality `34200490506 = in_progress`.
- Develop `ee940a135e0859b3d880d44d873260f0617b17f4`: no exact completed canonical Quality success establishing global promotion readiness.
- No exact-current reproduction of historical Windows/runtime crash signatures.

## Integrator handoff

- CLEAR `ERR-0024` / Spec-Core §72 hold from exact Quality `34198674038 = success`.
- HOLD Backend lineage `ea601b96d...` for `ERR-0025` until the exact pytest assertion is root-caused or a concrete exact-green successor clears it.
- Keep `ERR-0023` at `FIXED_PENDING_VERIFY` until focused Jobs lifecycle + Ruff + canonical Quality succeed on an exact Develop descendant carrying the Error-owned wording.
- Consume UI `34200490506` and Spec/Core `34198712540` when complete; deduplicate any red signal before allocating another ERR.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume exact `ERR-0025` pytest traceback or a concrete corrected Backend successor; finalize root cause or verify the minimal owner fix.
2. Consume UI `34200490506` and Spec/Core `34198712540`; deduplicate before opening any new ERR.
3. Verify integrated `ERR-0023` on an exact Develop descendant.
4. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.
