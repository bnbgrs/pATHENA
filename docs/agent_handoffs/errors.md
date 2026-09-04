# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`
- Worker branch: `postmerge/errors`
- Synchronization: history-preserving NON-FORCE merge `09bc08b6945e4097c07998768738e0ad1f1760be`, with parents prior Error head `f99d9b8f911874c45928a7911013b0774ce96068` and exact Develop `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0009`.
- FIXED: `ERR-0001` through `ERR-0008`.
- BLOCKED: none.

## Fresh evidence

- Historical `ERR-0004` remains `FIXED` and did not recur.
- Error candidate `67f3f447621c4544a5fb2fe321e76b62347290e0` changes only the two stale `raw.readline_sizes` expectations to `[17, 9, 2]` and `[9, 5, 1]`; product byte caps, overflow handling and secrecy/security assertions remain unchanged.
- Backend independently converged on the same harness-only correction at `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`; current Backend handoff head is `225db6c031551a2b79edf0d74b331a33e359ad26`.
- Exact canonical Quality `33911612711` on Backend head `225db6c031551a2b79edf0d74b331a33e359ad26` is still `in_progress`.
- In that exact run, Windows path safety, Linux storage regressions and local-install smoke are `success`; specification validator, Ruff and mypy are also `success`; full pytest remains in progress. Pending pytest is neither PASS nor failure evidence.
- Therefore `ERR-0009` remains `FIXED_PENDING_VERIFY`; no global-green claim is made yet.
- Current Develop is `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`; Error was synchronized non-force without dropping the candidate harness correction.

## ERR-0009 verification contract

Candidate fix lineage: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; equivalent Backend owner correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.

Required before closure:

1. `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_uses_bounded_readline_without_whole_body_read` PASS.
2. `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_rejects_many_small_lines_over_cumulative_limit` PASS.
3. Ruff PASS.
4. mypy PASS.
5. full pytest PASS.
6. canonical ATHENA Quality on an exact descendant containing the correction unchanged = `success`.

Until all required evidence exists, do not mark `ERR-0009` `FIXED`.

## Integrator handoff

- `ERR-0001` through `ERR-0008` remain cleared.
- Reject failing Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1` and cancelled Quality `33900614960` as global-green evidence.
- Prefer the Backend-owned equivalent correction lineage now that owner and Error agree on the same harness contract; do not duplicate or revert the product remaining-budget hardening.
- Do not consume Backend `225db6c031551a2b79edf0d74b331a33e359ad26` as globally green until Quality `33911612711` completes successfully, including full pytest and canonical enforcement.
- Preserve prior verified ERR fixes and do not treat red, cancelled, pending or unverified exact-head SHAs as globally green.

## Next scan

1. Consume completion of Backend Quality `33911612711`; if green, close `ERR-0009` with exact evidence, otherwise isolate the exact primary pytest signature and fix only that root cause.
2. Consume newest UI/Core/Integrator/current-Develop exact-head evidence and allocate `ERR-0010` only for a concrete deduplicated primary failure.
3. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security and local install/start scanning for real current-lineage failures.
