# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@78519f7c94df31b3c2374e5a1124fe799db28929`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `b63613d1bbd66a24f7e8c48af9fc8367b8ccb93f`.
- History-preserving NON-FORCE synchronization merge: `54489a07e5c8fd49a0b4342de887b8cfc86b3719`, parents `b63613d1bbd66a24f7e8c48af9fc8367b8ccb93f` and `78519f7c94df31b3c2374e5a1124fe799db28929`.
- Current worker heads reviewed: Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48`; Backend `8bbd0c0b1ff3bf48fde48ce3e1a8e235e0a83b2e`; UI `7fe5d44e4271dcbec6c0bfba92e0a01a0671b69f`; Integrator/Develop `78519f7c94df31b3c2374e5a1124fe799db28929`.
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

- Backend predecessor exact `05549d4cfc8a8cdd01f3f4cbbe83685d200c9795`: Quality `34138525799 = success`.
- UI predecessor exact `89cea7ecfaeb75a694a0682ff39feb5172ffbcfa`: Quality `34139713588 = success`.
- Spec/Core current head `c6b4fdba485a1de249a93e99883fca4085b9fc48`: prior exact Quality `34127196867 = success`; no current failure signal.
- Backend current exact `8bbd0c0b1ff3bf48fde48ce3e1a8e235e0a83b2e`: Quality `34143789976` is in progress; Linux storage, local install and Windows path safety are completed PASS, while Python 3.12 quality is still in progress. No confirmed primary failure.
- UI current exact `7fe5d44e4271dcbec6c0bfba92e0a01a0671b69f`: Quality `34144645412` is in progress; Linux storage, local install and Windows path safety are completed PASS, while Python 3.12 quality is still in progress. No confirmed primary failure.
- Develop exact `78519f7c94df31b3c2374e5a1124fe799db28929`: no pull-request-triggered workflow run is associated with this exact SHA in the current scan; no promotion-ready claim.
- No current exact-SHA Quality/runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.
- `ERR-0004` remains FIXED; no Ruff recurrence is present in current confirmed evidence.

## Integrator handoff

- No Error-Ledger hold exists for predecessor Backend `05549d4cfc8a8cdd01f3f4cbbe83685d200c9795` or predecessor UI `89cea7ecfaeb75a694a0682ff39feb5172ffbcfa` because their exact canonical runs completed successfully.
- No Error-Ledger hold exists for Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48` based on prior exact canonical success.
- Do not treat current Backend `8bbd0c0b1ff3bf48fde48ce3e1a8e235e0a83b2e` or UI `7fe5d44e4271dcbec6c0bfba92e0a01a0671b69f` as exact-green until `34143789976` and `34144645412` complete successfully.
- Do not promote Develop `78519f7c94df31b3c2374e5a1124fe799db28929` without its own exact completed canonical evidence or an explicitly accepted product-identical successor.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- `ERR-0004` and `ERR-0019` remain FIXED; reopen only on exact-current recurrence.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before any Beta/release promotion, execute these known crash classes explicitly on the exact candidate SHA. A reproducible known signature blocks promotion.

## Next scan

1. Consume completion of Backend `34143789976` and UI `34144645412`; allocate/reopen only on concrete deduplicated primary failure evidence.
2. Consume the next exact current Develop/runtime signal for `78519f7c94df31b3c2374e5a1124fe799db28929` or successor.
3. If a run turns red, isolate the exact diagnostic, separate cascade from primary root cause, then finalize root cause, make the minimal Error-owned fix, or concretely verify the owning worker mutation in the same run.
4. If no real failure exists, keep the ledger clean rather than manufacturing work.
