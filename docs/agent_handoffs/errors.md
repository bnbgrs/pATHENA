# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@b6c5c6181a5327d4ee436be518f4eebfacaf82bb`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `2b7aa1940d4807df5e4347fd030eae8d9c03da38`.
- History-preserving NON-FORCE synchronization merge: `fc519540563d79d499e68e7def23cc722ae68bf6`.
- Current worker heads reviewed: Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48`; Backend `05549d4cfc8a8cdd01f3f4cbbe83685d200c9795`; UI `89cea7ecfaeb75a694a0682ff39feb5172ffbcfa`; Integrator/Develop `b6c5c6181a5327d4ee436be518f4eebfacaf82bb`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Canonical evidence consumed this run

- Spec/Core current head `c6b4fdba485a1de249a93e99883fca4085b9fc48`: prior exact Quality `34127196867 = success`; no current failure signal.
- Backend current exact `05549d4cfc8a8cdd01f3f4cbbe83685d200c9795`: Quality `34138525799 = in_progress`; local install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy PASS; full pytest still running. No confirmed primary failure.
- UI current exact `89cea7ecfaeb75a694a0682ff39feb5172ffbcfa`: Quality `34139713588 = in_progress`; local install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy PASS; full pytest still running. No confirmed primary failure.
- Develop exact `b6c5c6181a5327d4ee436be518f4eebfacaf82bb`: integrator documentation records verified WAL runtime integration, but no exact completed pull-request-triggered canonical Quality evidence was established for this Develop SHA in this scan. No promotion-ready claim.
- No current exact-SHA Quality/runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.
- `ERR-0004` remains FIXED; current Ruff evidence is green on both active Backend/UI exact SHAs.

## Integrator handoff

- No Error-Ledger hold exists for Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48` based on prior exact canonical success.
- Do not treat Backend `05549d4cfc8a8cdd01f3f4cbbe83685d200c9795` or UI `89cea7ecfaeb75a694a0682ff39feb5172ffbcfa` as exact-green until `34138525799` and `34139713588` complete successfully.
- Do not promote Develop `b6c5c6181a5327d4ee436be518f4eebfacaf82bb` without its own exact completed canonical evidence or an explicitly accepted product-identical successor.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- `ERR-0004` and `ERR-0019` remain FIXED; reopen only on exact-current recurrence.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before any Beta/release promotion, execute these known crash classes explicitly on the exact candidate SHA. A reproducible known signature blocks promotion.

## Next scan

1. Consume completion of Backend `34138525799` and UI `34139713588`; allocate/reopen only on concrete deduplicated primary failure evidence.
2. Consume the next exact current Develop/runtime signal for `b6c5c6181a5327d4ee436be518f4eebfacaf82bb` or successor.
3. If a run turns red, isolate the exact diagnostic, separate cascade from primary root cause, then finalize root cause, make the minimal Error-owned fix, or concretely verify the owning worker mutation in the same run.
4. If no real failure exists, keep the ledger clean rather than manufacturing work.
