# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@1e6b3b17117c938f5aee26c9797432959a4544c9`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization with current Develop is performed with a two-parent merge commit; no rebase/force update.
- Current Spec/Core: `25d3cf0a674086b3e8050bb730359674909288cc`.
- Current Backend: `55a6e95486c8b7501f27ed07748dc922803025ea`, Quality `34226856389 = in_progress` at review time.
- Current UI: `93367bc74dab77f8ffab65e7de538ee79fb5a72a`, Quality `34227608407 = in_progress` at review time.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0025 — shared canonical pytest failure — IN_PROGRESS

Backend exact SHA `aa9cb18188bf070ac4b9f0e2763e2b31c643a54f` completed Quality `34221259239 = failure`. Windows path safety, Local install smoke, Linux storage regressions, specification validator, Ruff and mypy all passed; only `Quality — pytest` failed and diagnostics upload passed.

This is another exact Backend persistence point for the shared pytest-only failure already independently reproduced by UI. Prior root-cause elimination remains binding: Backend sync `8b04e8d5816fc908399d3e80a4407edd5fe50473` failed before WAL exact-type product mutation `b90b96578146856f726208dcc1d562a26f6059b2`, so do not blame that product slice. Ruff is green on these current red lineages, so this is not historical `ERR-0004`.

The exact pytest traceback remains unavailable through the readable GitHub connector surface. Job metadata exposes the failing pytest step and all green sibling gates but not the traceback payload. Therefore no speculative product or harness mutation is authorized and no new ERR is allocated without a distinct exact assertion.

Current Backend successor `55a6e95486c8b7501f27ed07748dc922803025ea` is under Quality `34226856389`; current UI successor `93367bc74dab77f8ffab65e7de538ee79fb5a72a` is under Quality `34227608407`. Consume them next. If either is green, isolate the first clearing delta against its nearest exact red. If red, obtain exact assertion evidence before any mutation.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.` and Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` remains present. Do not mark FIXED yet: current Develop `1e6b3b17117c938f5aee26c9797432959a4544c9` has no completed exact canonical Quality run returned by the connector.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; later Spec/Core `f4abb89d7538a11efa50d94a847b6f69139c602b` also passed Quality `34220174847`, confirming no recurrence on that verified Core lineage.

## Integrator handoff

- HOLD global promotion for `ERR-0025`.
- DO NOT assign primary blame to WAL exact-type hardening; the canonical failure predates it and independently persists on UI lineage.
- DEDUPLICATE new worker pytest-only reds under `ERR-0025` unless an exact distinct assertion proves a separate root cause.
- KEEP `ERR-0023` at `FIXED_PENDING_VERIFY` until canonical Quality succeeds on an exact Develop descendant carrying the corrected Jobs lifecycle wording.
- CLEAR `ERR-0024`.
- CONSUME Backend `34226856389` and UI `34227608407` next; if either is green, isolate only the clearing delta against the nearest exact red; if red, seek exact pytest assertion/traceback rather than repeating eliminated hypotheses.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and known release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34226856389` on exact `55a6e95486c8b7501f27ed07748dc922803025ea` and UI Quality `34227608407` on exact `93367bc74dab77f8ffab65e7de538ee79fb5a72a`.
2. If either turns green, identify the first clearing delta from its nearest exact red; if red, obtain exact pytest assertion/traceback before mutation.
3. Keep worker pytest-only reds deduplicated under `ERR-0025` unless distinct exact evidence appears.
4. Check for an exact Develop Quality run to verify `ERR-0023`.
5. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.