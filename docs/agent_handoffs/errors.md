# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@15f4a439d15d4bb1414e7b54afee7a25ced36e61`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE sync: `e0796ebb84c65b0b24a767848f049222649b9662`, parents Error `9d761fa1e1c70a0c44f3158924fd358e6167a55d` and Develop `15f4a439d15d4bb1414e7b54afee7a25ced36e61`.
- Current worker heads reviewed: Spec/Core `6b164470eae5352e6d5c0a84ac32a8f80ac002bc`; Backend `936843b32b42b25d818eda39d128180844b9e14a`; UI `8454d633810283e47d0b9bb9b93321536440cb45`; Integrator/Develop `15f4a439d15d4bb1414e7b54afee7a25ced36e61`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Canonical evidence consumed this run

- Spec/Core exact `6b164470eae5352e6d5c0a84ac32a8f80ac002bc`: ATHENA Quality Gate `34116431458 = success`. This is a current exact-green successor after the verified ERR-0019 closure lineage; no error is allocated.
- Backend exact `936843b32b42b25d818eda39d128180844b9e14a`: Quality `34116835252 = in_progress`. Local install smoke, Windows path safety and Linux storage are complete PASS. In Python quality, Validator, Ruff and mypy are PASS; full pytest is still in progress. No confirmed primary failure exists.
- UI exact `8454d633810283e47d0b9bb9b93321536440cb45`: Quality `34118404763 = in_progress`. Local install smoke, Windows path safety and Linux storage are complete PASS. In Python quality, Validator, Ruff and mypy are PASS; full pytest is still in progress. No confirmed primary failure exists.
- Develop exact `15f4a439d15d4bb1414e7b54afee7a25ced36e61`: no exact pull-request-triggered canonical Quality run observed. No promotion-ready claim.
- No current exact-SHA Quality/runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.

## Integrator handoff

- No Error-Ledger hold exists for Spec/Core `6b164470eae5352e6d5c0a84ac32a8f80ac002bc`; exact canonical Quality `34116431458` is green. Integrator still owns normal collision/current-Develop review.
- Do not treat Backend `936843b32b42b25d818eda39d128180844b9e14a` or UI `8454d633810283e47d0b9bb9b93321536440cb45` as exact-green until their current Quality runs complete successfully.
- Do not promote Develop `15f4a439d15d4bb1414e7b54afee7a25ced36e61` without its own exact completed canonical evidence or an explicitly accepted product-identical successor.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- `ERR-0004` and `ERR-0019` remain FIXED; reopen only on exact-current recurrence.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before any Beta/release promotion, execute these known crash classes explicitly on the exact candidate SHA. A reproducible known signature blocks promotion.

## Next scan

1. Consume completion of Backend `34116835252` and UI `34118404763`; allocate/reopen only on concrete deduplicated primary failure evidence.
2. Consume the next exact current Develop/runtime signal for `15f4a439d15d4bb1414e7b54afee7a25ced36e61` or successor.
3. If a run turns red, isolate the exact diagnostic, separate cascade from primary root cause, then either finalize root cause, make the minimal Error-owned fix, or concretely verify the owning worker mutation in the same run.
4. If no real failure exists, keep the ledger clean rather than manufacturing work.
