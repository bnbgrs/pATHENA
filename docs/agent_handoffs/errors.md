# pATHENA Error Handoff

## Baseline

- Current baseline reviewed: `develop/pathena-next@51bd144aafc0fb1f50c00515c366442038a2c251`.
- Error worker: `postmerge/errors` only.
- Previous Error head: `4c2295f9dd20550d3b2cead4769a9802b69cbb18`.
- Current worker heads reviewed: Spec/Core `6ad95079a114ea1d89517f7c299153caef66d3b5`; Backend `b01598b0d8980a2983f912917556b3bdf9af94ff`; UI `535b2848643d8244d726e968c9ab9ed3e7620db4`; Integrator/Develop `51bd144aafc0fb1f50c00515c366442038a2c251`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0020`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0019`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## New exact evidence

`ERR-0020` is allocated from canonical Quality `34155243750` on exact Spec/Core SHA `6ad95079a114ea1d89517f7c299153caef66d3b5`.

- Local install smoke: PASS.
- Linux storage regressions: PASS.
- Windows path safety: PASS.
- Validator: PASS.
- Ruff: PASS.
- mypy: PASS.
- full pytest: FAIL.
- Exact parent `c6b4fdba485a1de249a93e99883fca4085b9fc48` was previously canonical green.
- The failing SHA's only new delta is `tests/unit/test_exhaustive_research_resume.py`, added by commit message `test(research): cover restart after 60 percent`.
- The GitHub diagnostics artifact exists (`canonical-quality-diagnostics-6ad95079...`) but its archived traceback payload is not exposed by the current connector. Root cause therefore remains deliberately unclassified between product and harness; no speculative fix was made.

## Other current workers

- Backend `b01598b0d8980a2983f912917556b3bdf9af94ff`: Quality `34156185828` remains in progress with Local install, Linux storage, Windows path safety, Validator, Ruff and mypy green; pytest still running.
- UI `535b2848643d8244d726e968c9ab9ed3e7620db4`: Quality `34156844241` remains in progress with Local install, Linux storage, Windows path safety, Validator, Ruff and mypy green; pytest still running.
- Develop `51bd144aafc0fb1f50c00515c366442038a2c251` has no exact-current promotion-ready evidence established.

## Integrator handoff

- HOLD Spec/Core `6ad95079a114ea1d89517f7c299153caef66d3b5`; Quality `34155243750` is exact red via full pytest.
- Do not label `ERR-0020` product or harness until the exact failing assertion/traceback is available or a focused exact reproduction identifies it.
- Next Error run must consume the traceback/owner successor and either finalize root cause plus minimal fix, or verify the owning worker correction; repeating the same unknown hypothesis is not acceptable.
- Do not treat Backend `b01598b0d8980a2983f912917556b3bdf9af94ff` or UI `535b2848643d8244d726e968c9ab9ed3e7620db4` as exact-green until their current Quality runs complete successfully.
- Preserve Windows path safety, Storage, Security, Provider/Transport, Recovery, Ruff, mypy, Validator and all release crash-regression guards.

## Persistent Beta/release regression matrix

Retain without reopening absent exact-current reproduction: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before any Beta/release promotion, execute these known crash classes explicitly on the exact candidate SHA. A reproducible known signature blocks promotion.

## Next scan

1. Resolve `ERR-0020` from exact traceback/reproduction or verify an owner corrective successor.
2. Consume Backend `34156185828` and UI `34156844241` completions and allocate only concrete deduplicated primary failures.
3. Consume the next exact current Develop/runtime signal.
