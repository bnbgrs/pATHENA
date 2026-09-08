# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE synchronization this run: `b560dfcfbae9313e06105829d1de027200a0f30d`.
- Current Spec/Core: `af1f9da019fbee21984cf62fb77a2e8bbacaed5b`, Quality `34198712540 = success`.
- Current Backend: `8929474b6bdc4885c51e51de327816d5cf42137c`, Quality `34206163937 = in_progress`.
- Current UI: `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812`, Quality `34205607335 = failure` at full pytest only.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0025`.
- FIXED_PENDING_VERIFY: `ERR-0023`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`, `ERR-0024`.
- STALE: `ERR-0014`.
- OPEN/BLOCKED: none.

## ERR-0025 — shared canonical pytest failure — IN_PROGRESS

Initial Backend Quality `34195601115` on `ea601b96d681580c2e8f1f1af40c7d97c347511e` is pytest-only red with Local install, Windows path safety, Linux storage, Validator, Ruff and mypy green.

This run materially narrows root-cause ownership. Backend sync head `8b04e8d5816fc908399d3e80a4407edd5fe50473` also failed Quality `34205822004` before the WAL exact-type product mutation `b90b96578146856f726208dcc1d562a26f6059b2`; therefore that WAL mutation cannot be the primary cause of the already-existing failure. Independently, UI sync head `6cd161d98a54ebfa0c356fe0a3c21660fc1a9812` fails Quality `34205607335` only at full pytest while all non-pytest canonical gates pass and without the Backend WAL product mutation.

Deduplication result: treat these worker reds as one shared-suite/shared-baseline `ERR-0025` unless an exact distinct assertion proves otherwise. Do not allocate a separate UI error from `34205607335` yet. The uploaded diagnostics exist, but the exact traceback payload is not exposed by the available connector surface; no speculative product or harness mutation is allowed.

Current Backend head `8929474b6bdc4885c51e51de327816d5cf42137c` is under canonical run `34206163937`; consume that result next. A green result would provide a concrete clearing lineage to diff; a red result must be deduplicated and its exact assertion obtained before mutation.

## ERR-0023 — terminal Jobs copy — FIXED_PENDING_VERIFY

Error fix `d0207d43dabd66406df630a2cdff89e6f56b259b` changed terminal wording to `This job is {state}; no actions are available.`. Develop integration `568d57a63bb2253d97ca63e92b52e1df66505ac9` is retained by current Develop, whose exact product blob is `src/athena/desktop/jobs_lifecycle.py@a661beaa6cbcc4fe35178e24d1f56de8db7d9ff9`.

Do not mark FIXED yet: current Develop `cbc66ecbe8b6080e7e955471a5d7131e2ec84bf9` has no completed exact canonical Quality run, and current UI is pytest-only red rather than a verification surface.

## ERR-0024 — §72 unavailable-NAS acceptance — FIXED

Exact corrected Spec/Core head `772c2bfdc8767b7c0d032dbb8709120de635f6c0` passed Quality `34198674038`. Current documentation descendant `af1f9da019fbee21984cf62fb77a2e8bbacaed5b` independently completed Quality `34198712540 = success`. Keep the hold cleared and preserve exact source identity, UNAVAILABLE-not-IRRELEVANT semantics and durability assertions.

## Integrator handoff

- HOLD global promotion for `ERR-0025`, but do not pin blame on the WAL exact-type product slice: the canonical red predates it and independently recurs on UI synchronization lineage.
- KEEP `ERR-0023` at `FIXED_PENDING_VERIFY` until focused Jobs lifecycle + Ruff + canonical Quality succeed on an exact Develop descendant carrying `a661beaa6cbcc4fe35178e24d1f56de8db7d9ff9` or byte-identical corrected content.
- CLEAR `ERR-0024`; current Spec/Core is exact green via `34198712540`.
- Consume Backend `34206163937` when complete and use its result to localize `ERR-0025`; deduplicate before allocating any new ERR.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and known release crash-regression guards.
- No global Develop promotion-ready claim.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34206163937` on exact `8929474b6bdc4885c51e51de327816d5cf42137c`.
2. If red, obtain the exact pytest assertion or identify a concrete first green descendant and diff only the clearing delta; do not repeat WAL-blame analysis.
3. Verify `ERR-0023` on an exact Develop descendant with completed canonical Quality.
4. Before Beta/release promotion, execute the known-crash matrix on the exact candidate SHA.
