# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@249c83ae7dc4a33ceb8491029af4bad09b452e92`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `93c5aaaf4a250b17e83007d510923e0d94a5abed`.
- Current Spec/Core: `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`, Quality `34198712540 = success`.
- Current Backend: `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e`, Quality `34211221630 = in_progress`.
- Current UI: `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723`, Quality `34211448894 = failure` at full pytest only.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0025 — shared canonical pytest failure — IN_PROGRESS

The shared failure is now confirmed persistent across additional exact descendants. Backend `8929474b6bdc4885c51e51de327816d5cf42137c` completed Quality `34206163937 = failure` with Local install, Windows path safety, Linux storage, Validator, Ruff and mypy green and only full pytest red. This extends the earlier Backend evidence and confirms the signal did not disappear on the next descendant.

Independent UI synchronization descendant `0bc6947afecd0def64c2cbc0f6bdc1c5b97fc723` likewise completed Quality `34211448894 = failure` with every non-pytest canonical gate green and only full pytest red. It follows the earlier UI red `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812`, so the failure is not a single-run flake on either worker lineage.

Prior root-cause elimination remains binding: Backend sync `8b04e8d5816fc908399d3e80a4407edd5fe50473` failed before WAL exact-type product mutation `b90b96578146856f726208dcc1d562a26f6059b2`; do not blame that product slice. Deduplicate current Backend/UI pytest-only reds under `ERR-0025` unless an exact distinct assertion proves otherwise.

The exact pytest traceback is still not exposed by the available GitHub connector surface. Job metadata proves `Quality — pytest` is the sole failing canonical quality step and diagnostics upload succeeds, but the uploaded payload itself is unavailable as readable evidence. Therefore no speculative product or harness mutation is authorized.

Current Backend `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e` is running Quality `34211221630`; consume it first next run. A green result becomes the first concrete clearing descendant and must be diffed narrowly. A red result further localizes persistence but still requires exact assertion evidence before mutation.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.` and Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` remains present. Do not mark FIXED yet: current Develop `249c83ae7dc4a33ceb8491029af4bad09b452e92` has no completed exact canonical Quality run.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`; current Spec/Core descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` passed `34198712540`.

## Integrator handoff

- HOLD global promotion for `ERR-0025`.
- DO NOT assign primary blame to WAL exact-type hardening; the canonical failure predates it and independently persists on UI lineage.
- DEDUPLICATE new worker pytest-only reds under `ERR-0025` unless an exact distinct assertion proves a separate root cause.
- KEEP `ERR-0023` at `FIXED_PENDING_VERIFY` until canonical Quality succeeds on an exact Develop descendant carrying the corrected Jobs lifecycle wording.
- CLEAR `ERR-0024`; Spec/Core remains exact green.
- Consume Backend `34211221630` next; if green, diff only the clearing delta against the nearest red ancestor. If red, continue seeking the exact pytest assertion rather than repeating already-eliminated hypotheses.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and known release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34211221630` on exact `e4370a46bd42785aaea0f5c1806d8d79ced3eb7e`.
2. If green, identify the first clearing delta from the nearest exact red; if red, obtain exact pytest assertion/traceback before mutation.
3. Check for an exact Develop Quality run to verify `ERR-0023`.
4. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.
