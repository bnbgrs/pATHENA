# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@df05e76c998148e2445401de04115a7c5dccd708`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE sync this run: `e0c77705ad30102c612a1e8706e769f77f5d8951`.
- Current Spec/Core head: `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00`.
- Current Backend head: `5fb145df421059314b4d90f53b9fc69b1c4333ab`.
- Current UI head: `4c656c2c5dfb55e6d3f0078719183cbbad73a555`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0024`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0024 — §72 unavailable-NAS acceptance

Initial exact failure: Spec/Core `5fbe0dc8b3d7674a18c562e96c118ddf4e476985`, Quality `34186455107`; only full pytest failed.

Concrete owner-side root cause identified and repaired: the acceptance selected work items by list order, not exact source identity, so it did not prove that the item marked UNAVAILABLE belonged to the NAS source. Repair `124bdd9d789230d33452cfbc2452b307d410316c` maps persisted work items through candidate -> `source_id`, selects the actual NAS work item, and retains all unavailable-vs-irrelevant, 2/3 coverage and durability assertions.

Verification materially advanced but remains red: exact Quality `34190083267` on `124bdd9d789230d33452cfbc2452b307d410316c` passed Local install, Windows path safety, Linux storage, Validator, Ruff and mypy, but full pytest still failed. The ordering/source-identity harness defect is therefore real and fixed, but does not explain the entire remaining full-suite failure. Current handoff descendant `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` has Quality `34190114472` still in progress.

Integrator: HOLD §72. Next Error run must consume the exact remaining assertion/traceback or a concrete green/corrective successor; do not repeat the already-fixed list-order hypothesis.

## ERR-0023 — terminal Jobs copy

Root cause remains product copy in `src/athena/desktop/jobs_lifecycle.py`; Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.`. Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` is still present on current Develop.

Status remains `FIXED_PENDING_VERIFY`: no completed canonical Quality on a Develop descendant specifically establishes exact verification of the integrated Error wording. Do not substitute equivalent UI wording for exact verification.

## Current worker evidence

- Spec/Core: `124bdd9d789230d33452cfbc2452b307d410316c` -> Quality `34190083267 = failure`, pytest-only; `ac8dad2af4d5bb8b38c2fdcb6f4ea61b3deb5b00` -> `34190114472 = in_progress`.
- Backend: `5df50d524d4177a2fe157cf18cb952ff15df65a4` -> Quality `34187200684 = failure`, pytest-only with all non-pytest gates green. No new ERR allocated without exact assertion; this may deduplicate to an existing shared/full-suite defect. Current Backend `5fb145df421059314b4d90f53b9fc69b1c4333ab` -> `34190743330 = in_progress`.
- UI: current `4c656c2c5dfb55e6d3f0078719183cbbad73a555` -> Quality `34191944523 = pending`.
- Develop `df05e76c998148e2445401de04115a7c5dccd708`: no exact completed canonical Quality success establishing global promotion readiness.
- No exact-current reproduction of historical Windows/runtime crash signatures.

## Integrator handoff

- HOLD `ERR-0024` / Spec-Core §72 until the remaining full-pytest failure is exactly root-caused and a corrected exact successor is canonical green.
- Keep `ERR-0023` at `FIXED_PENDING_VERIFY` until focused Jobs lifecycle + Ruff + canonical Quality succeed on a Develop descendant carrying the exact Error-owned wording.
- Do not allocate a separate Backend error from `34187200684` until its exact pytest assertion is known and deduplicated.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume `34190114472` and exact remaining §72 pytest evidence; finalize `ERR-0024` or verify a concrete owner correction.
2. Consume Backend `34190743330` and UI `34191944523`; deduplicate any red signal before opening a new ERR.
3. Verify integrated `ERR-0023` on an exact Develop descendant.
4. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.
