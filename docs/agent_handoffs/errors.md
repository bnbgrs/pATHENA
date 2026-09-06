# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`.
- Baseline SHA observed this run: `14ca6fece527d6b51956b3e5fa3ec7b291252420`.
- Worker branch: `postmerge/errors`.
- Error branch pre-run head: `2b42d3acfc11cf3862659e272ff920cd43f77873`.
- Current Backend head observed: `20edbed46471a50e72661e2e69502b094a0b599f`.
- Current UI head observed: `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0015 — closed with exact verification

The reproduced bounded local-response negative-read failure remains closed as a harness defect.

- Failing canonical Backend Quality: `34004101347@e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba`.
- Reproduced same sole failure: `34006604490@aed7296fd0ca173daaca41da1f2f64e575b8c5b4`, `1 failed, 4666 passed, 3 skipped`.
- Root cause: `_TrackingResponse.read(amt)` behaved as an unbounded byte generator. The production wrapper intentionally requested `remaining + 1` bytes to detect overflow, so the fake fabricated a fifth byte for an intended four-byte body and correctly triggered `LocalResponseTooLargeError`.
- Minimal Backend harness fix: `5abee1fb3cf9aa639a2600796036302ef63a773d` makes the fake response finite/remaining-aware without changing the product overflow probe or weakening assertions.
- Verified descendant: `a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`.
- Exact canonical verification: Quality `34009044381@a9a267ec790ea4dd1c9cfc79d07fc1665f664e30 = success`.
- Newer exact Backend descendant `9dc8375399c6b07f9c52545783004607aa9dd430` also completed Quality `34011613102 = success`.
- Result: `ERR-0015 = FIXED`.

The product `remaining + 1` byte-budget probe, true-integer validation, deadlines and provider/transport guards remain mandatory and unchanged.

## Current worker evidence

- Backend head `20edbed46471a50e72661e2e69502b094a0b599f`: canonical Quality `34014111747` is in progress. Local install smoke, Linux storage, Windows path safety, Validator, Ruff and mypy are PASS; full pytest is still running. This head contains the bounded-response-constructor hardening lineage. No current failure is established.
- Earlier constructor-limit exact test head `3eca7fce6ffedfff15bdfeb252db63d88b671de6` had Quality `34014086876` cancelled by the newer descendant run; cancellation is not failure evidence.
- UI head `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`: canonical Quality `34014713429` is in progress. Local install smoke, Linux storage, Windows path safety, Validator, Ruff and mypy are PASS; full pytest is still running. No current failure is established.
- Develop head `14ca6fece527d6b51956b3e5fa3ec7b291252420` has no completed pull-request-triggered canonical Quality run observed this cycle. Do not claim repository-wide green for that exact head from older runs.

## Historical state retained

- `ERR-0004` remains `FIXED`; exact B010/I001 evidence and exact canonical green verification remain recorded.
- `ERR-0014` remains `STALE`, not `FIXED`: reopen the same ID only if the exact exit-139/controller-refresh signature recurs on a current exact SHA.

## Persistent Windows/runtime regression knowledge

The following signatures remain Beta/release acceptance knowledge only and are not automatically OPEN without current exact-SHA reproduction:

- missing `pypdf` distribution metadata / `PackageNotFoundError` plus supervisor relaunch behavior;
- frozen child argv recursion: preserve fail-closed routing and two-EXE split;
- exactly one Desktop and bounded/non-growing workers;
- adaptive output reserve at 2048 LM-Studio context;
- Windows lane-lock cluster: `_lock_nonblocking` `PermissionError [Errno 13]`, then `SchedulerLaneOwnershipError`, then packaged-worker `OSError [Errno 22]`;
- `duplicate column name: source_processing_job_id`;
- `ATHENA Core startup failed`;
- `Failed to start service 'storage-bootstrap'`.

Any recurrence on an exact Beta/release candidate blocks promotion until root cause is closed with real verification.

## Integrator handoff

- ERR-0015 remains closed: fix `5abee1fb3cf9aa639a2600796036302ef63a773d`, verified descendant `a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`, canonical Quality `34009044381 = success`; later Backend descendant `9dc8375399c6b07f9c52545783004607aa9dd430`, Quality `34011613102 = success`.
- Preserve all provider transport byte-budget, deadline, loopback-only/proxy-free, Storage, Security, Recovery, Qt, Windows path, Validator, Ruff and mypy guards.
- Do not promote current Develop `14ca6fece527d6b51956b3e5fa3ec7b291252420` without exact completed canonical evidence.
- Current Backend and UI runs are partially green but still await full pytest/workflow completion; do not mark either exact head READY yet.

## Next scan

1. Consume completion of Backend Quality `34014111747@20edbed46471a50e72661e2e69502b094a0b599f`.
2. Consume completion of UI Quality `34014713429@5a40e75ed78293ddd8c1ea3533c5632d6dea2910`.
3. Inspect the next exact Develop/runtime signal.
4. Allocate or reopen a stable `ERR-####` only for a concrete deduplicated primary failure; then finalize root cause or perform the minimal scope-correct fix in the same run where evidence permits.
5. Keep historical crash classes as release-regression knowledge unless reproduced on the exact current candidate.
