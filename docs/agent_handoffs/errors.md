# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next@8236500a5ae0ae58e7dce5bb3cf0771eb534670d`.
- Worker branch: `postmerge/errors`; pre-run head `90904477f4810d0580ca42f4be3b9290b703c1a4`.
- Current Backend head: `a5904fc2078a8dec5eece17dd352436d14453d8f`.
- Current UI head: `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only; no force update, rebase, history rewrite or merge to main was attempted.

## Current error state

- OPEN: `ERR-0016`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015`.
- STALE: `ERR-0014`.
- BLOCKED: none.

## ERR-0016 — Local HTTP overflow no longer poisons the bounded response

Exact canonical Backend Quality `34016515174@c991482a9f49dec50e69779f73e3a0939df5c73b` completed failure. Windows path safety, Linux storage, local install smoke, specification Validator, Ruff and mypy all passed; full pytest failed exactly two tests with `2 failed, 4690 passed, 3 skipped`:

- `tests/unit/test_local_http_response_boundaries.py::test_size_overflow_poisoning_blocks_followup_read_before_underlying_io`
- `tests/unit/test_local_http_response_boundaries.py::test_readline_overflow_poisoning_blocks_followup_io`

The first oversized `read()`/`readline()` correctly raises `LocalResponseTooLargeError`, but a subsequent body read reaches underlying I/O instead of failing immediately.

Root cause is a product regression in the oversize-before-accounting lineage beginning at `5e6862fe9544465e3aed66840601a204d4d2cae5`. The new implementation computes `next_bytes_read`, raises if it exceeds the cap, and only assigns `_bytes_read` after that check. This leaves `_bytes_read` within budget after rejection and removes the established poisoned-state marker consumed by `_assert_within_byte_budget()`. The new `tests/unit/test_local_http_oversize_accounting.py` expectation that `_bytes_read == 0` after rejection conflicts with the older fail-closed poisoning invariant when no separate poison state exists.

Previous synchronized Backend head `56a78635a8404ac4d7fb1aa2129d1ef2054040bb` passed canonical Quality `34016477844 = success`; the delta to failing `c991482a...` is bounded to Local HTTP oversize-accounting product/test changes plus handoff documentation. Current Backend `a5904fc2078a8dec5eece17dd352436d14453d8f` still contains the non-poisoning `next_bytes_read` implementation, so the root cause remains present in the active Backend lineage.

Required correction: preserve a distinct fail-closed poisoned state after any over-budget returned chunk, preferably via an explicit flag rather than treating rejected bytes as successfully consumed. `_assert_within_byte_budget()` or an equivalent pre-I/O guard must reject all subsequent bounded body access. Preserve `remaining + 1` overflow probing, cumulative byte limits, true-integer validation, total deadlines, bytes-only body validation, loopback-only/proxy-free/redirect-rejecting transport, Security, Storage and Recovery guards. The new oversize-accounting regression should assert that rejected bytes are not counted as successful consumption while also proving follow-up I/O is blocked.

No Error-branch product patch was made this run because the active defect is Backend-owned and the current Error branch does not contain that newer mutation. This run finalized and versioned the root cause instead of duplicating an active worker mutation.

## Current worker evidence

- Backend `34019237735@a5904fc2078a8dec5eece17dd352436d14453d8f`: in progress; Windows path safety PASS, Linux storage PASS, local install smoke PASS, Validator PASS, Ruff PASS, mypy PASS, full pytest running at observation time. It is not fix evidence because its code still contains the `ERR-0016` root cause.
- UI `34017125454@bf7fadf849140697dc63c92c6a5c6c69335e3278 = success`.
- Current UI `34019891561@089a0e4b0b8fc43e37f00f8288f64cd62014fbb4`: in progress; Windows path safety PASS, Linux storage PASS, local install smoke PASS, Validator PASS, Ruff PASS, mypy PASS, full pytest running at observation time.
- Current Develop `8236500a5ae0ae58e7dce5bb3cf0771eb534670d` has no exact completed canonical Quality observed this run; do not claim repository-wide green for that exact head from older evidence.

## Historical state retained

- `ERR-0004` remains `FIXED`; exact startup/readiness Ruff evidence and exact canonical green verification remain recorded in the ledger.
- `ERR-0014` remains `STALE`, not `FIXED`; reopen only on recurrence of the exact controller-refresh exit-139 signature on a current exact SHA.
- `ERR-0015` remains `FIXED`; its finite/remaining-aware harness correction is independently verified and must not be confused with the new product poisoning regression.

## Persistent Windows/runtime regression knowledge

The following remain Beta/release acceptance knowledge and are not automatically OPEN without current exact-SHA reproduction:

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

- Reject the Backend oversize-before-accounting lineage beginning at `5e6862fe9544465e3aed66840601a204d4d2cae5`, including current descendant `a5904fc2078a8dec5eece17dd352436d14453d8f`, as READY while `ERR-0016` remains open.
- Accept no fix claim until focused read/readline overflow-poisoning, exact-limit/EOF and `ERR-0015` negative-read regressions pass, Ruff and mypy remain green, and an exact canonical full Quality run succeeds.
- Preserve all provider transport byte-budget, deadline, bytes-only, loopback-only/proxy-free, Storage, Security, Recovery, Qt, Windows path, Validator, Ruff and mypy guards.
- `ERR-0001` through `ERR-0013` and `ERR-0015` remain fixed; `ERR-0014` remains stale.

## Next scan

1. Consume completion of Backend Quality `34019237735@a5904fc2078a8dec5eece17dd352436d14453d8f` and verify whether it reproduces `ERR-0016`.
2. Verify the first Backend correction on a new exact SHA against both poisoning and oversize-accounting semantics; do not accept a harness-only weakening.
3. Consume current UI Quality `34019891561@089a0e4b0b8fc43e37f00f8288f64cd62014fbb4` for any unrelated concrete primary failure.
4. After `ERR-0016` closure, immediately scan the next current canonical/runtime signal and allocate a new stable ID only for a concrete deduplicated primary failure.
