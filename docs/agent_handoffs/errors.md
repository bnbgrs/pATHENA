# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@591da5b99d2d8a7d24ba2c2cf866151bf362f4fb`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `de488e7f956f817de9fe17c8edcb58378d4ccfce`.
- History-preserving NON-FORCE synchronization merge: `72a9f67fe85ad8f1792e0cc4bd90487573fa83f4`.
- Current worker heads reviewed: Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48`; Backend `69b5a7792f5b2087f857fe00c0828a209abff438`; UI `b4297ae1e54e2bbf8b2f8d673018077590b029c8`; Integrator/Develop `591da5b99d2d8a7d24ba2c2cf866151bf362f4fb`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Canonical evidence consumed this run

- Backend exact `42a3397916a0b75091f2577bd02bf89b0082b4aa`: ATHENA Quality Gate `34128772157 = success`; no new Error-Ledger item.
- UI exact `e4123e2085b9c7c20f5dffdc8faba19d14296c57`: ATHENA Quality Gate `34129349248 = success`; no new Error-Ledger item. Integrator already consumed this exact-green slice for UI-GAP-0063.
- Spec/Core current documentation head `c6b4fdba485a1de249a93e99883fca4085b9fc48`: Quality `34127196867 = success`; no current failure signal.
- Backend current exact `69b5a7792f5b2087f857fe00c0828a209abff438`: Quality `34133863835 = in_progress`; local install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy PASS; full pytest still running. No confirmed primary failure.
- UI current exact `b4297ae1e54e2bbf8b2f8d673018077590b029c8`: Quality `34134425435 = in_progress`; local install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy PASS; full pytest still running. No confirmed primary failure.
- Develop exact `591da5b99d2d8a7d24ba2c2cf866151bf362f4fb`: no exact completed pull-request-triggered canonical Quality evidence observed. No promotion-ready claim.
- No current exact-SHA Quality/runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.

## Integrator handoff

- No Error-Ledger hold exists for exact-green Backend `42a3397916a0b75091f2577bd02bf89b0082b4aa`, UI `e4123e2085b9c7c20f5dffdc8faba19d14296c57`, or Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48` based on the cited canonical evidence.
- Do not treat current Backend `69b5a7792f5b2087f857fe00c0828a209abff438` or UI `b4297ae1e54e2bbf8b2f8d673018077590b029c8` as exact-green until `34133863835` and `34134425435` complete successfully.
- Do not promote Develop `591da5b99d2d8a7d24ba2c2cf866151bf362f4fb` without its own exact completed canonical evidence or an explicitly accepted product-identical successor.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- `ERR-0004` and `ERR-0019` remain FIXED; reopen only on exact-current recurrence.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before any Beta/release promotion, execute these known crash classes explicitly on the exact candidate SHA. A reproducible known signature blocks promotion.

## Next scan

1. Consume completion of Backend `34133863835` and UI `34134425435`; allocate/reopen only on concrete deduplicated primary failure evidence.
2. Consume the next exact current Develop/runtime signal for `591da5b99d2d8a7d24ba2c2cf866151bf362f4fb` or successor.
3. If a run turns red, isolate the exact diagnostic, separate cascade from primary root cause, then finalize root cause, make the minimal Error-owned fix, or concretely verify the owning worker mutation in the same run.
4. If no real failure exists, keep the ledger clean rather than manufacturing work.
