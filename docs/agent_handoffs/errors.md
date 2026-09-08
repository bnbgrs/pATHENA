# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@20619f1310bef9d7d2aa706cff11a974144c47e5`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `eda1e559fceddd01ad006f474f987ae7460456bd`.
- Current Spec/Core: `a77c1a5c5ef95ebc852cecb80aa13ffec1ad4cb7`.
- Current Backend: `73726422889bec6a43ad6d1b06f201d720b477d0`, Quality `34215906072 = in_progress`.
- Current UI: `31ed3fcb4b13d1cc115c7eb1c7a19c451b3b29ff`, Quality `34216731239 = pending`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0025 — shared canonical pytest failure — IN_PROGRESS

Backend exact SHA `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e` has now completed Quality `34211221630 = failure`. Local install smoke, Windows path safety, Linux storage regressions, specification validator, Ruff and mypy all passed; only `Quality — pytest` failed, and diagnostics upload passed. This is another exact persistence point after Backend `8929474b6bdc4885c51e51de327816d5cf42137c` / `34206163937` and the independent UI lineage `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723` / `34211448894`.

Prior root-cause elimination remains binding: Backend sync `8b04e8d5816fc908399d3e80a4407edd5fe50473` failed before WAL exact-type product mutation `b90b96578146856f726208dcc1d562a26f6059b2`; do not blame that product slice. The repeated exact reds remain deduplicated under `ERR-0025` unless an exact distinct assertion proves otherwise.

The exact pytest traceback is still not exposed by the readable GitHub connector surface. The canonical diagnostics artifact for `34211221630` exists as artifact `10051235357`, but the archive payload is not exposed as UTF-8 through the available action. Therefore no speculative product or harness mutation is authorized.

Current Backend `73726422889bec6a43ad6d1b06f201d720b477d0` is now under Quality `34215906072`. Consume it first next run. A green result becomes the first concrete clearing descendant and must be diffed narrowly against the nearest red. A red result further proves persistence but still requires exact assertion evidence before mutation.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.` and Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` remains present. Do not mark FIXED yet: current Develop `20619f1310bef9d7d2aa706cff11a974144c47e5` has no completed exact canonical Quality run returned by the connector.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; verified descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` passed `34198712540`.

## Integrator handoff

- HOLD global promotion for `ERR-0025`.
- DO NOT assign primary blame to WAL exact-type hardening; the canonical failure predates it and independently persists on UI lineage.
- DEDUPLICATE new worker pytest-only reds under `ERR-0025` unless an exact distinct assertion proves a separate root cause.
- KEEP `ERR-0023` at `FIXED_PENDING_VERIFY` until canonical Quality succeeds on an exact Develop descendant carrying the corrected Jobs lifecycle wording.
- CLEAR `ERR-0024`.
- CONSUME Backend `34215906072` next; if green, isolate only the clearing delta against the nearest exact red. If red, seek the exact pytest assertion/traceback rather than repeating already-eliminated hypotheses.
- CONSUME current UI `34216731239` after Backend and deduplicate before allocating any new ERR.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and known release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34215906072` on exact `73726422889bec6a43ad6d1b06f201d720b477d0`.
2. If green, identify the first clearing delta from the nearest exact red; if red, obtain exact pytest assertion/traceback before mutation.
3. Consume UI Quality `34216731239` and deduplicate.
4. Check for an exact Develop Quality run to verify `ERR-0023`.
5. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.
