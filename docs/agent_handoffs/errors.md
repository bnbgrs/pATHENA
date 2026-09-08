# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@4f077e36248a49d261f13d3f3838d62a376f506f`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization commit: `53cf8bc4a6a40988a5bc40414c704d1cf2ea9694`.
- Current Backend: `00b630e4915ec85abc08252d85e6403009b48858`; canonical Quality `34239827573` in progress.
- Current UI: `b0c74459af0d6382f23106819f34778c86b6f18b`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`, `ERR-0026`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0026 — Backend v41 schema Ruff I001 — IN_PROGRESS

Current exact Backend Quality `34239827573` on `00b630e4915ec85abc08252d85e6403009b48858` already reports Ruff FAIL while specification validator, mypy, Local install, Linux storage and Windows path safety pass. Full pytest is still running.

The root cause is no longer speculative: exact predecessor Quality `34234185972` on `255e73eae28651c20ae1baa660c4087f4a62f128` identified one Ruff `I001` import-order defect in `src/athena/storage/schema.py`. The current Backend handoff explicitly states that the two mypy regressions were repaired but this Ruff import-order defect remains outstanding. Therefore this is a new distinct exact error, not `ERR-0025` and not historical UI-owned `ERR-0004`.

Required Backend action is bounded: import-order-only correction in `src/athena/storage/schema.py`, with no semantic/schema/test/guard changes; then exact Ruff PASS plus focused v40→v41/restart/schema verification and canonical Quality. Do not mark FIXED from a docs-only commit.

## ERR-0025 — shared/full-pytest family — IN_PROGRESS

The older cross-lineage pytest-only failure remains open. New Backend diagnostics on predecessor `255e73eae28651c20ae1baa660c4087f4a62f128` / `34234185972` expose a larger v41-specific failure set (`51 failed, 4793 passed, 3 skipped`) with schema-expectation/legacy-fixture and WAL exact-type compatibility failures. These concrete failures must be separated by exact assertion/root cause rather than blindly folded into the older shared-baseline hypothesis.

Current Backend `34239827573` is still executing pytest. Consume the completed result next. If the v41 schema/fixture failures persist, allocate/split only when assertion-level evidence proves independent primary causes. WAL exact-type product hardening remains excluded as the original shared failure's primary cause because an earlier baseline failed before that mutation.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.` and Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` remains present. Current Develop still lacks an exact completed canonical-green verification; do not mark FIXED yet.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; later exact Spec/Core descendants remained green.

## Integrator handoff

- HOLD Backend v41 integration for `ERR-0026` until the import-order-only correction is exact Ruff-green and the relevant v40→v41/restart/schema checks remain valid.
- HOLD global promotion for `ERR-0025` until current pytest failures are decomposed/cleared with real evidence.
- Do not reopen historical `ERR-0004`; current Ruff failure is Backend `src/athena/storage/schema.py`, not UI startup/readiness harness.
- Keep `ERR-0023` at `FIXED_PENDING_VERIFY` until canonical Quality succeeds on an exact Develop descendant carrying the corrected Jobs lifecycle wording.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.
- No global promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume completed Backend Quality `34239827573` on `00b630e4915ec85abc08252d85e6403009b48858`.
2. Verify the Backend worker's minimal `src/athena/storage/schema.py` I001 correction on its exact successor; if no successor exists yet, keep `ERR-0026` IN_PROGRESS without speculative mutation.
3. Decompose current v41 pytest failures from `ERR-0025` only with assertion-level evidence.
4. Consume UI Quality for `b0c74459af0d6382f23106819f34778c86b6f18b` and verify no Jobs status-copy regression after the Integrator's bounded no-skip import.
5. Check exact Develop Quality to close or retain `ERR-0023`.
