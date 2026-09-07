# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@aed6afdfa23f1ef3d90abe05cbecd790727ed016`.
- Error branch mutation lineage remains `postmerge/errors` only; no force-push, rebase, history rewrite or main mutation was performed.
- Current worker heads reviewed: Spec/Core `cce6f200059d972958c9c971db2d7ad9d73ce2de`; Backend `607319fa41abdea0e468523f2c653e1fd84cfc82`; UI `1de30b1df309954399a3a47cc485b7517ecf9ce1`; Integrator/Develop `aed6afdfa23f1ef3d90abe05cbecd790727ed016`.
- Required handoffs and exact canonical workflow states were rechecked.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- IN_PROGRESS: `ERR-0019`.
- OPEN: none.

## Canonical evidence consumed this run

- Spec/Core advanced `ERR-0019` with a second harness-only correction at `cce6f200059d972958c9c971db2d7ad9d73ce2de`: both invalid/noncanonical repository `get()` calls in `test_current_instruction_outranks_conflicting_global_detail_preference` were replaced with the real `load_current()` API. This changes only `tests/unit/test_personal_memory_context_priority.py`.
- This confirms root-cause layer 2 as harness contract drift, in addition to layer 1 (`revision_no` expected although canonical serializer emits `context_id`).
- Exact follow-up Quality `34105038031@cce6f200059d972958c9c971db2d7ad9d73ce2de = failure`; Linux storage, Local install smoke, Windows path safety, Validator, Ruff and mypy PASS; full pytest alone FAILS. Therefore `cce6f200...` is still not a complete fix and `ERR-0019` remains active.
- Diagnostics artifact `10012806334` exists for the exact run, but the current GitHub connector exposes only artifact metadata and rejects the job-log endpoint; the automation runtime also cannot clone GitHub directly. The remaining traceback/assertion is therefore still unavailable and no speculative third mutation was made.
- Backend `34106290925@607319fa41abdea0e468523f2c653e1fd84cfc82 = in_progress`; no concrete primary failure confirmed yet.
- UI `34107416188@1de30b1df309954399a3a47cc485b7517ecf9ce1 = in_progress`; no concrete primary failure confirmed yet.
- Develop `aed6afdfa23f1ef3d90abe05cbecd790727ed016` has no exact completed canonical success established in this scan; no promotion-ready claim.
- No current Quality/Runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures, so none is reopened.

## ERR-0019 integrator handoff

- HOLD Spec/Core `cce6f200059d972958c9c971db2d7ad9d73ce2de`; it remains canonical-red.
- Treat the following only as verified partial harness corrections: `a033f07472b7c32f932da37b4659b047d19e0482` fixes the serializer expectation (`revision_no` -> `context_id: MEM-001`); `cce6f200059d972958c9c971db2d7ad9d73ce2de` fixes repository state reads (`get()` -> `load_current()`).
- Recover the exact residual pytest diagnostic from Quality run `34105038031`, Python quality job `101687991088`, or diagnostics artifact `10012806334`, then finish this same `ERR-0019` rather than allocating a duplicate.
- If the residual traceback proves another expectation/API drift, change only the harness. If it proves actual precedence behavior violates the current-message-over-durable-preference contract, fix the smallest product scope.
- Do not touch Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff/mypy/Validator configuration, or use Skip/XFail/dummy success paths.
- `ERR-0004` remains closed.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Recover the exact residual pytest traceback/assertion for `34105038031@cce6f200059d972958c9c971db2d7ad9d73ce2de` and finalize `ERR-0019`; do not repeat layers 1 or 2.
2. Consume Backend `34106290925` and UI `34107416188` completion and allocate/reopen only on a concrete deduplicated primary failure.
3. Consume the next exact current Develop/Runtime signal for `aed6afdfa23f1ef3d90abe05cbecd790727ed016` or successor.
4. Keep known Windows/runtime crash classes in the Beta/release regression matrix without reopening absent exact-current reproduction.
