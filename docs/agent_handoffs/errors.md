# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@7c784b77af3bc0ec0c2579cc89b6947aadaf701c`.
- Error branch mutation lineage: `postmerge/errors` only. No force-push, rebase, history rewrite, or main mutation.
- Current worker heads reviewed: Spec/Core `57aa31ec49ddec2d68147e91ea6b3c311d33881a`; Backend `552209e005b82d31577d9f8a466af4dd97b99866`; UI `cf808b725fcd7ac6c302cf8a3f59c20e385f8f2c`; Integrator/Develop `7c784b77af3bc0ec0c2579cc89b6947aadaf701c`.
- `spec-core.md`, `backend.md`, `ui.md`, and `integrator.md` were reviewed before this scan.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## Canonical evidence consumed this run

- Previously pending Backend `34067080370@35883180205c83cabc1d20ef2fad39d8ee691699` is now exact `success`; no error-ledger objection.
- Previously pending UI `34067696492@335d4b2ce2787677bd2d930efd7c12c325759f1f` is now exact `success`; no error-ledger objection.
- Current Spec/Core `57aa31ec49ddec2d68147e91ea6b3c311d33881a` completed canonical Quality `34069391378 = success`; no primary error signal.
- Current Backend `552209e005b82d31577d9f8a466af4dd97b99866` has canonical Quality `34069825099` still `in_progress`; no confirmed primary failure at this scan.
- Current UI `cf808b725fcd7ac6c302cf8a3f59c20e385f8f2c` has canonical Quality `34070554735` still `in_progress`; no confirmed primary failure at this scan.
- Current Develop `7c784b77af3bc0ec0c2579cc89b6947aadaf701c` has no exact completed canonical Quality observed; no promotion-ready claim.

## Integrator handoff

- `ERR-0018` remains closed with fix `61194be6eddf6fa7fe37c9c62690244a29414acd`; do not re-edit Personal Memory import layout without new exact contradictory evidence.
- Backend `35883180205c83cabc1d20ef2fad39d8ee691699` and UI `335d4b2ce2787677bd2d930efd7c12c325759f1f` are now exact canonical green.
- Spec/Core `57aa31ec49ddec2d68147e91ea6b3c311d33881a` is exact canonical green via `34069391378`.
- Do not treat current Backend `552209e005b82d31577d9f8a466af4dd97b99866` or current UI `cf808b725fcd7ac6c302cf8a3f59c20e385f8f2c` as exact green until their current workflows complete successfully.
- Preserve Provider/Transport byte-budget/deadline/poisoning, Personal-Memory provenance/review, Windows path safety, Storage, Security and Recovery guards.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume completion of Backend `34069825099` and UI `34070554735` on their exact heads.
2. Consume the next exact current Develop/Runtime signal and allocate/reopen only for concrete deduplicated primary evidence.
3. Keep known Windows/runtime crash classes in the Beta/release regression matrix without reopening absent exact-current reproduction.
