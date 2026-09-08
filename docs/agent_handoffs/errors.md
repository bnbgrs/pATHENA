# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@9fb4f005ebb34f835f5a6c362965ad35cd2f3efb`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization commit: `da6727cd60f56e6b88fbc7632712b04783637c84`, preserving prior Error head and exact Develop as parents.
- Current Backend: `255e73eae28651c20ae1baa660c4087f4a62f128`; Quality `34234185972 = in_progress` at review time.
- Current UI reviewed: `932face973987d84a44c5d37fc61509285466279`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0025 — shared canonical pytest failure — IN_PROGRESS

Backend exact SHA `55a6e95486c8b7501f27ed07748dc922803025ea` completed Quality `34226856389 = failure`. Windows path safety, Local install smoke, Linux storage regressions, specification validator, Ruff and mypy all passed; only `Quality — pytest` failed and diagnostics upload passed.

UI exact SHA `93367bc74dab77f8ffab65e7de538ee79fb5a72a` also completed Quality `34227608407 = failure`. This remains deduplicated under `ERR-0025`; no exact distinct assertion has been exposed that would justify a new error ID.

Prior root-cause elimination remains binding: Backend sync `8b04e8d5816fc908399d3e80a4407edd5fe50473` failed before WAL exact-type product mutation `b90b96578146856f726208dcc1d562a26f6059b2`, so do not blame that product slice. Ruff is green on the Backend red lineage, so this is not historical `ERR-0004`.

The exact pytest traceback remains unavailable through the readable GitHub connector surface. No speculative product or harness mutation is authorized.

Current Backend successor `255e73eae28651c20ae1baa660c4087f4a62f128` is under Quality `34234185972`; functional predecessor `e81957a388763d3b5931df694a06908a0ba29f75` / `34233916176` was cancelled by the newer worker commit and is not clearing evidence. Consume `34234185972` next. If green, isolate the first clearing delta against nearest exact red; if red, seek exact assertion/traceback before mutation.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.` and Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` remains present. Do not mark FIXED yet: exact canonical success on current Develop `9fb4f005ebb34f835f5a6c362965ad35cd2f3efb` was not established in this run.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; later Spec/Core `f4abb89d7538a11efa50d94a847b6f69139c602b` also passed Quality `34220174847`, confirming no recurrence on that verified Core lineage.

## Integrator handoff

- HOLD global promotion for `ERR-0025`.
- DEDUPLICATE Backend `34226856389` and UI `34227608407` under the shared pytest-only failure unless exact distinct assertion evidence appears.
- DO NOT assign primary blame to WAL exact-type hardening and DO NOT reopen `ERR-0004` from pytest-only red lineages with Ruff PASS.
- KEEP `ERR-0023` at `FIXED_PENDING_VERIFY` until canonical Quality succeeds on an exact Develop descendant carrying the corrected Jobs lifecycle wording.
- CONSUME Backend `34234185972` on `255e73eae28651c20ae1baa660c4087f4a62f128` next.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and known release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34234185972` on exact `255e73eae28651c20ae1baa660c4087f4a62f128`.
2. If green, identify the first clearing delta from nearest exact red; if red, obtain exact pytest assertion/traceback before mutation.
3. Keep new pytest-only worker reds deduplicated under `ERR-0025` unless distinct exact evidence appears.
4. Check for exact Develop Quality to verify `ERR-0023`.
5. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.