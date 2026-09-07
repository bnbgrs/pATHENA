# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@f4c7ecfdca3313f0418895e6e495459e091586fe`.
- Error branch mutation lineage: `postmerge/errors` only. No force-push, rebase, history rewrite, or main mutation.
- Current Develop synchronization for this scan is history-preserving, two-parent and NON-FORCE.
- Current worker heads reviewed: Spec/Core `8bb8822a3423ac4fa1ab2873ecf052d16c390199`; Backend `8ddd3f12dbf3eb34332b8b54ef06eccc3e0d35b8`; UI `2f98ef242107421770ed4573bea06532e052727b`; Integrator/Develop `f4c7ecfdca3313f0418895e6e495459e091586fe`.
- `spec-core.md`, `backend.md`, `ui.md`, and `integrator.md` were reviewed before this scan; worker heads and current canonical workflow states were independently rechecked.

## Current state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`, `ERR-0016`, `ERR-0017`, `ERR-0018`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## Canonical evidence consumed this run

- Spec/Core `34090530294@8bb8822a3423ac4fa1ab2873ecf052d16c390199 = success`; exact canonical green, no Error-ledger objection.
- Backend `34091580477@8ddd3f12dbf3eb34332b8b54ef06eccc3e0d35b8 = in_progress`; Validator/Ruff/mypy/Windows/Linux/local-install PASS, full pytest still running; no concrete primary Error-ledger signal.
- UI `34092357862@2f98ef242107421770ed4573bea06532e052727b = in_progress`; Validator/Ruff/mypy/Windows/Linux/local-install PASS, full pytest still running; no concrete primary Error-ledger signal.
- Current Develop `f4c7ecfdca3313f0418895e6e495459e091586fe` has no exact pull-request-triggered canonical Quality run associated with the SHA in this scan; no promotion-ready claim.
- No current Quality/Runtime evidence reproduces any retained Windows packaging/process-tree/chat-context/lane-lock/storage-bootstrap crash signature, so none is reopened.

## Integrator handoff

- Error ledger has no OPEN/BLOCKED defect.
- `ERR-0004` and `ERR-0018` remain closed; do not reopen without new exact contradictory evidence.
- Spec/Core `8bb8822a3423ac4fa1ab2873ecf052d16c390199` is exact canonical green via `34090530294`.
- Do not treat Backend `8ddd3f12dbf3eb34332b8b54ef06eccc3e0d35b8` or UI `2f98ef242107421770ed4573bea06532e052727b` as exact green until their current Quality runs complete successfully.
- Develop `f4c7ecfdca3313f0418895e6e495459e091586fe` still requires its own exact completed canonical evidence before any promotion-ready claim.
- Preserve Provider/Transport byte-budget/deadline/poisoning, Personal-Memory provenance/review, Windows path safety, Storage, Security and Recovery guards.

## Persistent Beta/release regression knowledge

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume completion of Backend `34091580477` and UI `34092357862`; allocate/reopen only if a concrete deduplicated primary failure appears.
2. Consume the next exact current Develop/Runtime signal for `f4c7ecfdca3313f0418895e6e495459e091586fe` or its successor.
3. Keep known Windows/runtime crash classes in the Beta/release regression matrix without reopening absent exact-current reproduction.
