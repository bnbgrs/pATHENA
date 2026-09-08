# pATHENA Error Handoff

## Baseline

- Current Develop reviewed: `develop/pathena-next@e6ed6eba803e4084b5e5aeaa2ad576dccdaf9961`.
- Error worker: `postmerge/errors` only.
- Exact Develop verification anchor consumed this run: `270f97c36bd114036658e322f68d8011983ff150`, Quality `34248696450 = SUCCESS`.
- Current Backend: `postmerge/backend@75e45f99ce60b87e0b56ea024d3bed931ec461d4`; active Quality `34251875708` already reports Validator PASS, Ruff FAIL, mypy PASS, Linux storage PASS, Local install PASS and Windows path safety PASS; pytest remains in progress at time of handoff.
- Backend candidate v41 product repair: `69e2a4707bba544af5d2d2ae53daffc1dbf786a3`; its first run `34251782009` was cancelled and is not verification evidence.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- IN_PROGRESS: `ERR-0026`, `ERR-0027`, `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN/BLOCKED/FIXED_PENDING_VERIFY: none.

## Hard progress this run

### ERR-0023 closed on exact Develop evidence

Develop SHA `270f97c36bd114036658e322f68d8011983ff150` contains `src/athena/desktop/jobs_lifecycle.py` blob `a661beaa6cbcc4fe35178e24d1f56de8db7d9ff9` with the corrected terminal text `This job is {state}; no actions are available.`. Canonical Quality `34248696450` on that exact SHA completed `SUCCESS`. `ERR-0023` is therefore `FIXED`; the prior exact-Develop verification hold is cleared.

### ERR-0025 cleared as stale historical signature

The older cross-lineage pytest-only family now has the required exact green descendant: Develop `270f97c36bd114036658e322f68d8011983ff150` / Quality `34248696450 = SUCCESS`. Because intervening accepted changes prevent unique attribution of one primary fix, the historical family is marked `STALE` rather than inventing a root cause. The later v41 failures remain separately owned by `ERR-0027` through `ERR-0029`.

### ERR-0026 corrective attempt is still Ruff-red

Backend commit `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` attempted the bounded schema import-order repair and v41 facade re-export. The first run `34251782009` was cancelled. Its documentation-only successor `75e45f99ce60b87e0b56ea024d3bed931ec461d4` is under canonical Quality `34251875708`; Ruff has already completed `FAIL` while Validator and mypy pass. Therefore `ERR-0026` stays `IN_PROGRESS`. Do not assume the successor Ruff diagnostic is the same I001 until diagnostics are available; consume the exact rule/file before another mutation.

### ERR-0027 candidate exists but is not yet verified

The same candidate product commit `69e2a4707bba544af5d2d2ae53daffc1dbf786a3` re-exports the real `RESEARCH_DELTA_BOUNDARY_MIGRATION_ID` and `RESEARCH_DELTA_BOUNDARY_SCHEMA_VERSION`. Keep `ERR-0027` `IN_PROGRESS` until the focused schema-contract assertion/full pytest on the exact successor completes; cancelled run `34251782009` does not count.

## ERR-0028 / ERR-0029 remain actionable

- `ERR-0028`: repair stale v40 current-version expectations and legacy v30-v40 fixtures that incorrectly contain v41-only `research_delta_boundaries`; do not weaken production migration behavior.
- `ERR-0029`: adapt WAL harness collaborators to canonical `DurableJobScheduler` / `WalMaintenanceOrchestrator` and current dependency wording; do not relax exact-type fail-closed guards.

## Integrator handoff

- CLEAR the old global hold for `ERR-0023`; exact Develop canonical verification is green.
- CLEAR the older `ERR-0025` promotion hold as an active defect; it is now historical `STALE` after exact green Develop descendant evidence. Reopen only on new exact-current reproduction.
- HOLD Backend v41 integration for `ERR-0026` through `ERR-0029`.
- For `ERR-0026`, consume diagnostics from `34251875708` before any further import-order mutation because the purported corrective successor is still Ruff-red.
- For `ERR-0027`, require exact focused/full verification of the facade re-export; do not infer PASS from the code diff alone.
- Preserve strict v40→v41 migration semantics, WAL exact-type guards, Windows path safety, Linux storage, local install, Security, Provider/Transport, Recovery, Ruff, mypy and Validator.
- No global promotion-ready claim while Backend v41 remains red/incomplete.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume completion/diagnostics of Backend Quality `34251875708` on `75e45f99ce60b87e0b56ea024d3bed931ec461d4`.
2. If Ruff remains red, identify the exact successor rule/file and require a minimal correction; do not repeat the old I001 hypothesis without evidence.
3. Independently verify whether `ERR-0027` schema-facade assertion is green on that exact successor.
4. Decompose remaining pytest failures only into `ERR-0028` / `ERR-0029` or new stable IDs when exact distinct signatures require it.
5. Continue scanning current canonical Develop/Runtime for the next real signal after Backend v41 closure.
