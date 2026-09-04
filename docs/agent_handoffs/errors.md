# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `e51e805266b625c008812ae5ab79435655ff1ca5`
- Worker branch: `postmerge/errors`
- Synchronization: history-preserving NON-FORCE merge `61e81656276d3e2affef119cdbc0944178e58672`, parents prior Error head `28e75ca7391ce0f41165f6d481f1318a98f27fdb` and exact Develop `e51e805266b625c008812ae5ab79435655ff1ca5`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0009`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0008`.
- BLOCKED: none.

## Fresh evidence

- Historical `ERR-0004` remains FIXED and did not recur.
- Core exact head `921c6868c8813c92da200cdd68a0ba12df583e9c` passed canonical Quality `33900087353 = success`.
- UI exact head `be55343dcaab9eb2afe80fe869000c139e6e2de1` / Quality `33902213148`: Windows path safety PASS, Linux storage PASS, local-install smoke PASS, specification validator PASS, Ruff PASS, mypy PASS, full pytest still running. Pending is neither PASS nor failure evidence.
- Backend exact head `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1` / Quality `33900689788`: Windows path safety PASS, Linux storage PASS, local-install smoke PASS, specification validator PASS, Ruff PASS, mypy PASS, full pytest FAIL.
- Canonical diagnostics artifact `9948717940` isolates exactly two Backend-owned failures in `tests/unit/test_lm_studio_response_limits.py`:
  - `test_stream_iteration_uses_bounded_readline_without_whole_body_read`: actual `raw.readline_sizes == [17, 9, 2]`, stale expected `[17, 17, 17]`.
  - `test_stream_iteration_rejects_many_small_lines_over_cumulative_limit`: actual `raw.readline_sizes == [9, 5, 1]`, stale expected `[9, 9, 9]`.
- Product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386` intentionally changed bounded streaming reads from constant `max_bytes + 1` to `remaining + 1`; the failing sequences exactly reflect this hardened cumulative budget. The product guard is not the defect shown by this run; the two harness size expectations lag the new contract.
- Current Develop `e51e805266b625c008812ae5ab79435655ff1ca5` has no exact-head global PASS claim.

## ERR-0009 owner action

Backend still actively owns `tests/unit/test_lm_studio_response_limits.py` and `src/athena/model/adapters/local_http.py`, so Error does not race that mutation this cycle.

Required minimal correction: preserve all existing behavioral/overflow assertions and change only the stale readline request-size expectations to the remaining-budget sequences (`[17, 9, 2]` and `[9, 5, 1]`), or an equivalently strict assertion proving monotonically shrinking `remaining + 1` reads. Do not revert the product hardening, weaken `MAX_LOCAL_RESPONSE_BYTES`, remove overflow coverage, Skip/XFail, or add dummy success paths.

Verification required before `ERR-0009` can become FIXED: new exact Backend SHA; both focused failing nodes PASS; Ruff PASS; mypy PASS; full pytest PASS; canonical Quality success.

If Backend does not produce the correction after one full additional non-colliding worker cycle and no active conflicting commit remains, Error may apply the minimal harness-only fix on `postmerge/errors` under the hard progress rule.

## Integrator handoff

- `ERR-0001` through `ERR-0008` remain cleared.
- Reject Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1` as globally green because canonical Quality `33900689788` fails full pytest.
- Do not infer a product-security regression from `ERR-0009`; current evidence points specifically to stale test call-size expectations after the remaining-budget hardening.
- Core `921c6868c8813c92da200cdd68a0ba12df583e9c` is canonical-green via `33900087353`.
- Do not consume UI `be55343dcaab9eb2afe80fe869000c139e6e2de1` as globally green until `33902213148` completes successfully.
- Preserve prior verified ERR fixes and do not treat historical red, cancelled, pending or unverified exact-head SHAs as globally green.

## Next scan

1. Check Backend for a new owner correction to `ERR-0009`; verify the exact new SHA against the two failing nodes plus canonical Quality. If no correction exists after one full additional non-colliding Backend cycle, take the minimal harness-only fix on `postmerge/errors`.
2. Consume UI Quality `33902213148` completion; allocate another ERR only on a distinct concrete deduplicated primary failure.
3. Check newest Core/Integrator and current Develop exact-head evidence.
4. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop and local install/start scanning for real current-lineage failures.
