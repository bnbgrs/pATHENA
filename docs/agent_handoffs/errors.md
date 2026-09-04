# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `c91e76804e74595f92c8eb624ce7c5d83b66bad2`
- Worker branch: `postmerge/errors`
- Synchronization: history-preserving NON-FORCE merge `964e71b98d6a417f87920fdb44a5630b87069424`, parents prior Error head `94e703f99f3363b10e96a4be32a92eda3f829ca3` and exact Develop `c91e76804e74595f92c8eb624ce7c5d83b66bad2`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0009`.
- FIXED: `ERR-0001` through `ERR-0008`.
- BLOCKED: none.

## Fresh evidence

- Historical `ERR-0004` remains FIXED and did not recur.
- Backend advanced from the failing ERR-0009 lineage to `7688f49ea351749bf227a1683fd14aba719d9bb6`, but `tests/unit/test_lm_studio_response_limits.py` still contained the two stale constant-size expectations `[17, 17, 17]` and `[9, 9, 9]`.
- Backend handoff separately records product hardening `2981624e0f7eef8c2e94b6f0eb86a859132a2386` and fixture-only correction `d988c9faa171f4fe86aac4b5fa4d169e8ee34a41`; its exact canonical Quality `33900614960` was cancelled after a later branch update and therefore is not PASS evidence.
- The owner cycle completed without correcting the exact ERR-0009 expectations, and no newer conflicting Backend mutation of those assertions was present. Under the hard progress rule, Error took the minimal harness-only fix.
- Error fix `67f3f447621c4544a5fb2fe321e76b62347290e0` changes only:
  - `raw.readline_sizes == [17, 17, 17]` -> `[17, 9, 2]`;
  - `raw.readline_sizes == [9, 9, 9]` -> `[9, 5, 1]`.
- All response-byte limits, overflow behavior, secrecy assertions and product guards remain unchanged. No Skip/XFail or success mocking was introduced.
- No exact workflow run was associated with `67f3f447621c4544a5fb2fe321e76b62347290e0` at first verification check, so `ERR-0009` is `FIXED_PENDING_VERIFY`, not `FIXED`.
- Current Develop `c91e76804e74595f92c8eb624ce7c5d83b66bad2` has no exact-head global PASS claim in this handoff.

## ERR-0009 verification contract

Candidate fix SHA: `67f3f447621c4544a5fb2fe321e76b62347290e0`.

Required before closure:

1. `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_uses_bounded_readline_without_whole_body_read` PASS.
2. `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_rejects_many_small_lines_over_cumulative_limit` PASS.
3. Ruff PASS.
4. mypy PASS.
5. full pytest PASS.
6. canonical ATHENA Quality on an exact descendant containing the candidate unchanged = success.

Until those exist, do not mark `ERR-0009` FIXED and do not call the Error candidate globally green.

## Integrator handoff

- `ERR-0001` through `ERR-0008` remain cleared.
- Reject Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1` as globally green because canonical Quality `33900689788` fails full pytest.
- Do not use cancelled Backend Quality `33900614960` as verification evidence.
- Candidate `ERR-0009` correction is Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; it is harness-only and preserves product hardening, but remains NOT READY pending exact verification.
- Preserve prior verified ERR fixes and do not treat historical red, cancelled, pending or unverified exact-head SHAs as globally green.

## Next scan

1. Verify exact Error candidate `67f3f447621c4544a5fb2fe321e76b62347290e0` or an exact descendant with unchanged test blob using the two focused nodes, Ruff, mypy, full pytest and canonical Quality.
2. If the candidate fails, isolate the exact primary signature and correct only that root cause; no assertion/guard weakening.
3. Consume newest Backend/UI/Core/Integrator and current Develop exact-head evidence.
4. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop and local install/start scanning for real current-lineage failures.
