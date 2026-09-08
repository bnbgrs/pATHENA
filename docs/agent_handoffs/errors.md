# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE baseline synchronization: `76d095bb747aa9f006174e66fa88423e9e7d309b`.
- Current Spec/Core head reviewed: `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`.
- Current Backend head reviewed: `076a0d1209fe1cb30c6cfe7f6735a39158036c28`.
- Current UI head reviewed: `dd7384f8f39cb9b61c0fa1a8d205492b584dd3de`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0022`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0022 closed — Spec/Core Ruff import grouping

Spec/Core `0d0fe488fcf52e7bc89ec6e5feeb373aec93f823` failed canonical Quality `34173373152` only on Ruff while full pytest and all other canonical gates passed. The owner applied the minimal harness correction in `tests/unit/test_exhaustive_research_large_archive.py` at `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5` (`fix(core): satisfy Ruff import grouping for large archive acceptance`). Exact fix SHA passed canonical Quality `34176070442 = success`.

Classification remains harness-only. ERR-0022 is `FIXED`; its Spec/Core hold is cleared for that exact SHA.

## ERR-0021 closed — Jobs helper refresh suppression leaked beyond construction

The shared full-pytest-only signal is now isolated by a direct red-to-green UI sequence. UI parent `dd052e7d3fcbbec80653d472b7870ef019a96502` failed canonical Quality `34174017940` specifically at full pytest while Validator, Ruff, mypy, Local install, Windows path safety and Linux storage passed.

Its direct child `352b4c72c39d5cafe866c604a050a1b93df71940` changed only `tests/unit/test_pathena_jobs_status_copy.py`: `_workspace()` now saves the real `JobsWorkspace.refresh`, suppresses refresh only during `JobsWorkspace()` construction, then immediately restores the real method. Exact child passed canonical Quality `34174030199 = success`.

Root cause: the harness monkeypatch intended only to suppress constructor refresh remained active for the rest of each test, changing post-construction refresh behavior and contaminating full-suite semantics. This explains the same full-pytest-only split previously seen on Develop and Backend/UI descendants without requiring a product defect. Current Develop contains the corrected helper blob `a1ba67fdf864f49945a7dd5c6e3bfe9b981d09bd`.

ERR-0021 is `FIXED`. The specific error hold is cleared. Current Develop is still not globally promotion-ready until its own exact completed canonical Quality succeeds.

## Current worker evidence

- Spec/Core `d97ffca766868e3eb3ad1e9197fc1478a0e8e7a5`: Quality `34176070442 = success`; ERR-0022 closed.
- UI fix verifier `352b4c72c39d5cafe866c604a050a1b93df71940`: Quality `34174030199 = success`; direct parent `dd052e7d3fcbbec80653d472b7870ef019a96502` Quality `34174017940 = failure`, full-pytest-only; ERR-0021 closed.
- Backend previous `c964506791611da78dd3959aa64c12b2614e253b`: Quality `34173582002 = failure`, full-pytest-only; now treated as ERR-0021 shared-harness reproduction, not a separate Backend defect.
- Current Backend `076a0d1209fe1cb30c6cfe7f6735a39158036c28`: Quality `34177086068` in progress; do not allocate a new error until a concrete completed primary failure exists.
- Current UI `dd7384f8f39cb9b61c0fa1a8d205492b584dd3de`: no new exact primary failure established in this scan.
- Current Develop `eeaf49fa22f1b9b3f9dfae46c7cd2c2d1146d9ff`: corrected Jobs helper present; no associated exact completed pull-request-triggered canonical Quality run observed.

## Integrator handoff

- Clear ERR-0021 and ERR-0022 holds on their exact verified fixes.
- Do not convert those closures into a global Develop promotion-ready claim; `develop/pathena-next@eeaf49fa...` still requires its own exact completed canonical success.
- Consume Backend `34177086068` when complete and inspect current UI/Develop/runtime evidence for the next concrete primary failure.
- Do not reopen historical Windows/runtime crash classes without matching exact-current signatures.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume current Backend canonical completion and current UI exact Quality state.
2. Inspect exact current Develop/runtime evidence; allocate only a concrete deduplicated primary failure.
3. If no failure exists, retain zero-open ledger state rather than manufacturing work.
4. Before Beta/release promotion, run the known-crash matrix on the exact candidate SHA.
