# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`.
- Baseline SHA observed this run: `fd15a75212acac7f88886117835b8d754577ea91`.
- Worker branch: `postmerge/errors`.
- Error branch pre-run head: `46fb660d7980d83e1b22c061187bae2b99832610`.
- Current Backend head observed: `9dc8375399c6b07f9c52545783004607aa9dd430`.
- Current UI head observed: `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0015 — closed with exact verification

The reproduced bounded local-response negative-read failure is confirmed as a harness defect and is now closed.

- Failing canonical Backend Quality: `34004101347@e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba`.
- Reproduced same sole failure: `34006604490@aed7296fd0ca173daaca41da1f2f64e575b8c5b4`, `1 failed, 4666 passed, 3 skipped`.
- Root cause: `_TrackingResponse.read(amt)` behaved as an unbounded byte generator. The production wrapper intentionally requested `remaining + 1` bytes to detect overflow, so the fake fabricated a fifth byte for an intended four-byte body and correctly triggered `LocalResponseTooLargeError`.
- Minimal Backend harness fix: `5abee1fb3cf9aa639a2600796036302ef63a773d` makes the fake response finite/remaining-aware without changing the product overflow probe or weakening assertions.
- Verified descendant: `a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`.
- Exact canonical verification: Quality `34009044381@a9a267ec790ea4dd1c9cfc79d07fc1665f664e30 = success`.
- Result: `ERR-0015 = FIXED`.

The product `remaining + 1` byte-budget probe, true-integer validation, deadlines and provider/transport guards remain mandatory and unchanged.

## Current worker evidence

- Backend head `9dc8375399c6b07f9c52545783004607aa9dd430` has canonical Quality `34011613102` in progress. It is newer than the exact verified ERR-0015 descendant; consume it only for new Backend readiness/failure evidence, not to reopen ERR-0015 without an exact recurrence.
- UI head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea` is a separate current candidate and is not evidence of an Error-owned failure by itself.
- Develop head `fd15a75212acac7f88886117835b8d754577ea91` has no completed pull-request-triggered canonical Quality run observed this cycle. Do not claim repository-wide green for that exact head from older runs.

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

- Accept the ERR-0015 correction lineage as closed evidence: fix `5abee1fb3cf9aa639a2600796036302ef63a773d`, exact verified descendant `a9a267ec790ea4dd1c9cfc79d07fc1665f664e30`, canonical Quality `34009044381 = success`.
- Preserve all provider transport byte-budget, deadline, loopback-only/proxy-free, Storage, Security, Recovery, Qt, Windows path, Validator, Ruff and mypy guards.
- Do not promote current Develop `fd15a75212acac7f88886117835b8d754577ea91` without exact completed canonical evidence.
- Consume Backend `34011613102`; only allocate a new error if it finishes with a concrete deduplicated primary failure.

## Next scan

1. Consume completion of Backend Quality `34011613102@9dc8375399c6b07f9c52545783004607aa9dd430`.
2. Inspect the next exact Develop/UI canonical or runtime signal.
3. Allocate a new stable `ERR-####` only for a real deduplicated primary failure.
4. Keep historical crash classes as release-regression knowledge unless reproduced on the exact current candidate.
