# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`.
- Baseline SHA observed this run: `859e1a68e8d9a207a5094462aefe189f6f276c9d`.
- Worker branch: `postmerge/errors`.
- Error branch pre-run head: `118f3b2c182de43d1876c7c369a00282800018fa`.
- Current Backend head observed: `3d61f4ed646ceda00785928320bfefa12b6fb257`.
- Required `spec-core.md`, `backend.md`, `ui.md` and `integrator.md` handoffs were reviewed before disposition.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0015`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## Fresh evidence — ERR-0015

Backend bounded local-response read-size type stability has a concrete reproducible canonical failure.

- First canonical signal: Quality `34004101347@e4ddf651db85c1abe1c42e8b3f65a7b77fd08eba` failed only full pytest at `tests/unit/test_local_http_read_size_validation.py::test_bounded_local_response_still_accepts_negative_integer_read_size`.
- Backend then history-preserving NON-FORCE resynced to Develop at `aed7296fd0ca173daaca41da1f2f64e575b8c5b4`.
- Exact resync Quality `34006604490@aed7296fd0ca173daaca41da1f2f64e575b8c5b4` reproduced the identical sole failure: `1 failed, 4666 passed, 3 skipped`.
- In `34006604490`, Windows path safety, Linux storage regressions, local install smoke, specification Validator, Ruff and mypy all PASS. Only canonical full pytest fails.
- Exact exception: `LocalResponseTooLargeError: Local model response exceeded the configured byte limit.` from `src/athena/model/adapters/local_http.py:137` while the test expects `bounded.read(-1) == b"xxxx"` with `max_bytes=4`.

## Root cause — finalized

This is a harness defect, not a product byte-budget defect.

The bounded response intentionally maps `read(None)` or `read(negative_integer)` to an underlying request of `remaining + 1`. This one-extra-byte probe is what detects a response larger than the configured limit. With `max_bytes=4`, the wrapper therefore asks the delegate for five bytes.

The test's `_TrackingResponse.read(amt)` behaves as an unbounded byte generator: when asked for five bytes it fabricates five bytes. That contradicts the test's intended finite four-byte response premise. The wrapper then correctly counts five bytes and raises `LocalResponseTooLargeError`.

The product guard must not be changed. The minimal correction is in `tests/unit/test_local_http_read_size_validation.py`: make the fake response finite/remaining-aware so its four-byte body returns at most the bytes actually present even when probed with `remaining + 1`. Preserve the assertion that true negative integers are accepted and preserve explicit oversized-body rejection coverage.

## Ownership / collision rule

Backend currently owns `tests/unit/test_local_http_read_size_validation.py`. Current Backend head `3d61f4ed646ceda00785928320bfefa12b6fb257` is a documentation descendant and exact canonical Quality `34006623230` is still in progress. Error therefore does not create a competing mutation in this cycle.

Required Backend correction signature:

1. finite/remaining-aware `_TrackingResponse` or equivalent finite-body harness;
2. no change to `src/athena/model/adapters/local_http.py` `remaining + 1` overflow probe;
3. no weaker assertions or changed exception contract for truly oversized bodies;
4. focused `tests/unit/test_local_http_read_size_validation.py` green;
5. relevant local HTTP response-limit regressions green;
6. Ruff green;
7. exact new Backend SHA canonical Quality green, including full pytest.

If Backend completes one further worker cycle without this correction and no active colliding code mutation remains, Error may take the minimal harness-only fix under the hard progress rule.

## Historical state retained

- Historical `ERR-0004` remains `FIXED`; exact B010/I001 evidence and exact-head green verification remain recorded in the ledger. No current startup/readiness Ruff recurrence exists.
- `ERR-0014` remains `STALE`, not `FIXED`: two historical exact SIGSEGV recurrences were followed by repeated exact canonical clean runs on unchanged affected controller/test lineage. Reopen the same ID only on exact exit-139/controller-refresh recurrence.
- No mocks, Skip/XFail, dummy success path, weaker off-UI-thread assertions, Ruff/mypy relaxation, or Security/Storage/Recovery/Windows guard weakening is permitted.

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

- `ERR-0015` is the sole active error.
- Reject Backend bounded-read type-stability candidate `e4ddf651...` and resync `aed7296f...` as READY because both have the exact same full-pytest failure.
- Do not classify the product `remaining + 1` probe as defective; it is the safety mechanism exposing the fake-response defect.
- Current Backend `3d61f4ed...` remains unverified while Quality `34006623230` is in progress.
- Current Develop `859e1a68e8d9a207a5094462aefe189f6f276c9d` does not receive a repository-wide green claim from this run.
- Preserve all provider transport byte-budget, deadline, loopback-only/proxy-free, Storage, Security, Recovery, Qt, Windows path, Validator, Ruff and mypy guards.

## Next scan

1. Consume Backend Quality `34006623230@3d61f4ed646ceda00785928320bfefa12b6fb257`.
2. Verify whether Backend supplies the exact minimal `ERR-0015` harness correction on a new SHA; do not accept a documentation-only handoff as a fix.
3. Set `ERR-0015` to `FIXED` only after focused and exact canonical verification are actually green.
4. If one full further Backend cycle leaves the same error unfixed and no active collision remains, apply the minimal harness-only correction on `postmerge/errors` and verify it without weakening product safeguards.
5. After `ERR-0015`, immediately consume the next concrete canonical/runtime signal; do not manufacture failures.
