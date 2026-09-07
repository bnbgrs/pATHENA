# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@d40dc421585193db7bda039d113d7d81ccfb9c03`.
- Error worker: `postmerge/errors` only.
- History-preserving NON-FORCE baseline synchronization: `68a72d5c70ed8d95e05679dc4769d140ee4839f4`.
- Current Spec/Core head reviewed: `80915e1e8c7dff42fc998e9035df41273bdb08ca`.
- Current Backend head reviewed: `aae2b6ef705db49eddcee501e872dd179889709e`.
- Current UI head reviewed: `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0020`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0020 closure

ERR-0020 is now `FIXED` on real canonical evidence. The root cause remained harness-only: final source-analysis artifacts are reduce/final synthesis artifacts, while the fixture had preserved the `resume-source-*` identity only in MAP output and collapsed reduce/final output to one generic Finding. The corrected fixture preserves real schema phase dispatch, finds `resume-source-\d+` anywhere in the request text and carries that source identity through synthesis without changing production code or weakening assertions.

Error fix commit `ae44d44aef0ed6a8885a78738f8c316f35ac5fb9` produces test blob `ada5c2d762f9603e48e37790b0fbdcb73885e935`. Current Spec/Core head `80915e1e8c7dff42fc998e9035df41273bdb08ca` contains that exact same blob and canonical ATHENA Quality Gate `34166094972` completed `success`. Its jobs show Local install smoke PASS, Windows path safety PASS, Linux storage regressions PASS, Validator PASS, Ruff PASS, mypy PASS and full pytest PASS. This satisfies the required byte-identical owner-successor verification and clears the ERR-0020 hold.

## Current worker evidence

- Spec/Core `80915e1e8c7dff42fc998e9035df41273bdb08ca`: exact canonical Quality `34166094972 = success`.
- Backend `aae2b6ef705db49eddcee501e872dd179889709e`: Quality `34167555208` currently `in_progress`; no new confirmed primary failure yet.
- UI `04b4a77b144fb1da1edfa0b0c155f8fe8b583d6c`: Quality `34167675010` currently `pending`; no new confirmed primary failure yet.
- Current Develop `d40dc421585193db7bda039d113d7d81ccfb9c03` has no error-worker promotion-ready claim; require exact completed canonical evidence on the actual candidate before promotion.

## Integrator handoff

- CLEAR the ERR-0020 error-ledger hold for the byte-identical verified fixture repair represented by Spec/Core head `80915e1e8c7dff42fc998e9035df41273bdb08ca` and Quality `34166094972 = success`.
- This clearance is limited to ERR-0020. It is not a blanket green claim for current Develop or unrelated worker mutations.
- Consume Backend `34167555208` and UI `34167675010` when complete. If either yields an exact primary failure, deduplicate cascades and allocate/reopen only against concrete evidence.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

## Next scan

1. Consume Backend Quality `34167555208` and UI Quality `34167675010` completions.
2. Inspect the next exact current Develop/canonical or runtime failure signal; do not manufacture errors.
3. Reopen only a known crash class that reproduces on an exact current SHA; otherwise retain it solely as release-regression knowledge.
