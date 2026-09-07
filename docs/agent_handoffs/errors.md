# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@87aa3cebb13abb7b65bfc9aa64edf77cf257dd01`.
- Error branch mutation lineage: `postmerge/errors` only. No force-push, rebase, history rewrite, or main mutation.
- Current worker heads reviewed: Spec/Core `ad0647e5659572737831456a28312a530150720f`; Backend `3a5cdd8c95007a0fba909910d9505871b1631fcf`; UI `0a257caf023b5babc0394d77264e5173fc417bc1`; Integrator/Develop `87aa3cebb13abb7b65bfc9aa64edf77cf257dd01`.
- `spec-core.md`, `backend.md`, `ui.md`, and `integrator.md` were reviewed before this scan.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## Canonical evidence consumed this run

- Current Spec/Core `34075688329@ad0647e5659572737831456a28312a530150720f = success`; no primary Error-ledger signal.
- Current Backend `34076469382@3a5cdd8c95007a0fba909910d9505871b1631fcf = success`; no primary Error-ledger signal.
- Current UI `34077293629@0a257caf023b5babc0394d77264e5173fc417bc1 = in_progress`; no confirmed primary failure. Prior integrated UI `34073855547@23c03d06b333ec2156665bfaa65b0de5219f5ccd = success` remains valid source evidence.
- Current Develop `87aa3cebb13abb7b65bfc9aa64edf77cf257dd01` has no exact completed canonical Quality observed; no promotion-ready claim.
- No current Quality/Runtime evidence reproduces any retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signature, so none is reopened.

## Integrator handoff

- Error ledger has no OPEN/BLOCKED defect.
- `ERR-0004` and `ERR-0018` remain closed; do not reopen without new exact contradictory evidence.
- Spec/Core `ad0647e5659572737831456a28312a530150720f` and Backend `3a5cdd8c95007a0fba909910d9505871b1631fcf` are exact canonical green.
- Do not treat UI `0a257caf023b5babc0394d77264e5173fc417bc1` as exact green until `34077293629` completes successfully.
- Develop `87aa3cebb13abb7b65bfc9aa64edf77cf257dd01` still requires its own exact completed canonical evidence before any promotion-ready claim.
- Preserve Provider/Transport byte-budget/deadline/poisoning, Personal-Memory provenance/review, Windows path safety, Storage, Security and Recovery guards.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume completion of UI `34077293629@0a257caf023b5babc0394d77264e5173fc417bc1` and allocate/reopen only if a concrete deduplicated primary failure appears.
2. Consume the next exact current Develop/Runtime signal for `87aa3cebb13abb7b65bfc9aa64edf77cf257dd01` or its successor.
3. Keep known Windows/runtime crash classes in the Beta/release regression matrix without reopening absent exact-current reproduction.
