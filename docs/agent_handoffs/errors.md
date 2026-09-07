# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@92eddff0bfdbdeeb7c8756240a1ed174265e2f65`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `b3818ff60b5f98906afd70a6a5ae7a4d437650e8`.
- History-preserving NON-FORCE synchronization merge: `e32a4f2450b8fcf7b45bb99c41282c9086eb3739`.
- Current worker heads reviewed: Spec/Core `c6b4fdba485a1de249a93e99883fca4085b9fc48`; Backend `42a3397916a0b75091f2577bd02bf89b0082b4aa`; UI `e4123e2085b9c7c20f5dffdc8faba19d14296c57`; Integrator/Develop `92eddff0bfdbdeeb7c8756240a1ed174265e2f65`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`, `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Canonical evidence consumed this run

- Previously pending Backend exact `c41a49cf0efa8f5b2f47bbfcb89f5e1bf133f7ed`: ATHENA Quality Gate `34122783316 = success`; no new Error-Ledger item.
- Previously pending UI exact `8bd74b266028ccfac5b06d286f84d805261ac9e6`: ATHENA Quality Gate `34124133923 = success`; no new Error-Ledger item. Integrator already used this exact-green slice for UI-GAP-0062.
- Current Backend exact `42a3397916a0b75091f2577bd02bf89b0082b4aa`: Quality `34128772157 = in_progress`. Local install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy are PASS; full pytest remains in progress. No confirmed primary failure exists.
- Current UI exact `e4123e2085b9c7c20f5dffdc8faba19d14296c57`: Quality `34129349248 = in_progress`. Local install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy are PASS; full pytest remains in progress. No confirmed primary failure exists.
- Current Spec/Core documentation head `c6b4fdba485a1de249a93e99883fca4085b9fc48` descends from exact-green `57e133507ab4b8edc78d4af8467f2320dce0e906` via Quality `34121540987 = success`; handoff records a cross-component Protected Lock dependency, not an error signal.
- Develop exact `92eddff0bfdbdeeb7c8756240a1ed174265e2f65`: no exact completed canonical Quality evidence observed in this scan. No promotion-ready claim.
- No current exact-SHA Quality/runtime evidence reproduces retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signatures; none is reopened.

## Integrator handoff

- No Error-Ledger hold exists for the previously verified Backend `c41a49cf0efa8f5b2f47bbfcb89f5e1bf133f7ed` or UI `8bd74b266028ccfac5b06d286f84d805261ac9e6`; their canonical runs are exact-green.
- Do not treat current Backend `42a3397916a0b75091f2577bd02bf89b0082b4aa` or UI `e4123e2085b9c7c20f5dffdc8faba19d14296c57` as exact-green until `34128772157` and `34129349248` complete successfully.
- Do not promote Develop `92eddff0bfdbdeeb7c8756240a1ed174265e2f65` without its own exact completed canonical evidence or an explicitly accepted product-identical successor.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- `ERR-0004` and `ERR-0019` remain FIXED; reopen only on exact-current recurrence.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before any Beta/release promotion, execute these known crash classes explicitly on the exact candidate SHA. A reproducible known signature blocks promotion.

## Next scan

1. Consume completion of Backend `34128772157` and UI `34129349248`; allocate/reopen only on concrete deduplicated primary failure evidence.
2. Consume the next exact current Develop/runtime signal for `92eddff0bfdbdeeb7c8756240a1ed174265e2f65` or successor.
3. If a run turns red, isolate the exact diagnostic, separate cascade from primary root cause, then either finalize root cause, make the minimal Error-owned fix, or concretely verify the owning worker mutation in the same run.
4. If no real failure exists, keep the ledger clean rather than manufacturing work.
