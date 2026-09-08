# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@d5b4d1479416edd1cd55f8bff6190029f42d9289`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `5618eb391721423724e2791f21cc2e1bb947c3a6`.
- Current Spec/Core: `f4abb89d7538a11efa50d94a847b6f69139c602b`, Quality `34220174847 = success`.
- Current Backend: `aa9cb18188bf070ac4b9f0e2763e2b31c643a54f`, Quality `34221259239 = in_progress` at review time.
- Current UI: `b9936b6e404c224c47230ced5919f475760c013a`, Quality `34221783638 = failure`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0025 — shared canonical pytest failure — IN_PROGRESS

Current UI exact SHA `b9936b6e404c224c47230ced5919f475760c013a` has completed Quality `34221783638 = failure`. Windows path safety, Local install smoke, Linux storage regressions, specification validator, Ruff and mypy all passed; only `Quality — pytest` failed and diagnostics upload passed. This extends the same exact gate pattern already observed on independent Backend and UI lineages.

Prior root-cause elimination remains binding: Backend sync `8b04e8d5816fc908399d3e80a4407edd5fe50473` failed before WAL exact-type product mutation `b90b96578146856f726208dcc1d562a26f6059b2`; do not blame that product slice. Current UI Ruff is green, so this is also not a recurrence of historical `ERR-0004`.

The exact pytest traceback remains unavailable through the readable GitHub connector surface. Job metadata exposes the failing pytest step and all green sibling gates but not the traceback payload. Therefore no speculative product or harness mutation is authorized and no new ERR is allocated without a distinct exact assertion.

Current Backend `aa9cb18188bf070ac4b9f0e2763e2b31c643a54f` is under Quality `34221259239`. Consume it first next run. If green, it becomes a concrete clearing descendant and must be narrowly diffed against the nearest exact red. If red, seek the exact assertion rather than repeating already-eliminated hypotheses.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.` and Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` remains present. Do not mark FIXED yet: current Develop `d5b4d1479416edd1cd55f8bff6190029f42d9289` has no completed exact canonical Quality run returned by the connector.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; current Spec/Core `f4abb89d7538a11efa50d94a847b6f69139c602b` also passed Quality `34220174847`, confirming no current Core recurrence.

## Integrator handoff

- HOLD global promotion for `ERR-0025`.
- DO NOT assign primary blame to WAL exact-type hardening; the canonical failure predates it and independently persists on UI lineage.
- DEDUPLICATE new worker pytest-only reds under `ERR-0025` unless an exact distinct assertion proves a separate root cause.
- KEEP `ERR-0023` at `FIXED_PENDING_VERIFY` until canonical Quality succeeds on an exact Develop descendant carrying the corrected Jobs lifecycle wording.
- CLEAR `ERR-0024`; current Spec/Core is exact green.
- CONSUME Backend `34221259239` next; if green, isolate only the clearing delta against the nearest exact red. If red, seek exact pytest assertion/traceback rather than repeating eliminated hypotheses.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and known release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34221259239` on exact `aa9cb18188bf070ac4b9f0e2763e2b31c643a54f`.
2. If green, identify the first clearing delta from the nearest exact red; if red, obtain exact pytest assertion/traceback before mutation.
3. Keep current UI `34221783638` deduplicated under `ERR-0025` unless a distinct assertion becomes available.
4. Check for an exact Develop Quality run to verify `ERR-0023`.
5. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.
