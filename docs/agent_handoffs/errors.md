# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@ed9dde599541dffe704a0810a9fa9debf1c8f74b`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `68ef04e969422829809c030c450cf321c5c74d50`.
- History-preserving NON-FORCE synchronization merge: `3d5568a268d4f4ee4c3cfec780b544543a3de60e`, parents `68ef04e969422829809c030c450cf321c5c74d50` and `ed9dde599541dffe704a0810a9fa9debf1c8f74b`.
- Current worker heads reviewed: Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48`; Backend `a3765f1e55420ebb193d37228919aa9032760cd0`; UI `81cf9ceffb1885943d82b80ab50f00eb3454eb9f`; Integrator/Develop `ed9dde599541dffe704a0810a9fa9debf1c8f74b`.
- Required `spec-core.md`, `backend.md`, `ui.md`, `integrator.md`, relevant worker heads and current canonical workflow state were reviewed before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Canonical evidence consumed this run

- Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48`: prior exact Quality `34127196867 = success`; no current failure signal.
- Backend `a3765f1e55420ebb193d37228919aa9032760cd0`: Quality `34152208000` is in progress. Local install smoke, Linux storage regressions and Windows path safety are completed PASS; specification validator, Ruff and mypy are completed PASS; full pytest is still running. No confirmed primary failure.
- UI `81cf9ceffb1885943d82b80ab50f00eb3454eb9f`: Quality `34152552680` is in progress. Local install smoke, Linux storage regressions and Windows path safety are completed PASS; specification validator, Ruff and mypy are completed PASS; full pytest is still running. No confirmed primary failure.
- UI-GAP-0067 exact worker `fd0780d23b081fddb8a236971c74f4cb3c565899` passed Quality `34148642145 = success` and was integrated to Develop in `109598a95ec63a23d9692257e784c69aa601ab79`.
- Develop exact `ed9dde599541dffe704a0810a9fa9debf1c8f74b`: no exact-current promotion-ready claim is made without matching completed canonical evidence.
- No current exact-SHA Quality/runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.
- `ERR-0004` remains FIXED; current Backend/UI Ruff evidence is green and no startup/readiness Ruff recurrence is present.

## Integrator handoff

- No Error-Ledger hold exists for integrated UI-GAP-0067 lineage `fd0780d23b081fddb8a236971c74f4cb3c565899` because exact canonical Quality `34148642145 = success`.
- Do not treat current Backend `a3765f1e55420ebb193d37228919aa9032760cd0` as exact-green until `34152208000` completes successfully; all completed canonical checks are green and only full pytest remains in progress.
- Do not treat current UI `81cf9ceffb1885943d82b80ab50f00eb3454eb9f` as exact-green until `34152552680` completes successfully; all completed canonical checks are green and only full pytest remains in progress.
- No Error-Ledger hold exists for Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48` based on prior exact canonical success.
- Do not promote Develop `ed9dde599541dffe704a0810a9fa9debf1c8f74b` without its own exact completed canonical evidence or an explicitly accepted product-identical successor.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- `ERR-0004` and `ERR-0019` remain FIXED; reopen only on exact-current recurrence.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before any Beta/release promotion, execute these known crash classes explicitly on the exact candidate SHA. A reproducible known signature blocks promotion.

## Next scan

1. Consume completion of Backend `34152208000` and UI `34152552680`; allocate/reopen only on concrete deduplicated primary failure evidence.
2. Consume the next exact current Develop/runtime signal for `ed9dde599541dffe704a0810a9fa9debf1c8f74b` or successor.
3. If a run turns red, isolate the exact diagnostic, separate cascade from primary root cause, then finalize root cause, make the minimal Error-owned fix, or concretely verify the owning worker mutation in the same run.
4. If no real failure exists, keep the ledger clean rather than manufacturing work.
