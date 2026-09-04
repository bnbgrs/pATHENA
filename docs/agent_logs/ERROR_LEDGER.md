# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened.
- Cascades are deduplicated under the primary root cause.
- `FIXED` requires observed verification; unverified corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `e51e805266b625c008812ae5ab79435655ff1ca5`
- Worker branch: `postmerge/errors`
- Synchronization: history-preserving NON-FORCE merge `61e81656276d3e2affef119cdbc0944178e58672` of current Develop into Error lineage.

## Current error state

- OPEN: none.
- IN_PROGRESS: `ERR-0009`.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0008`.
- BLOCKED: none.

## Current scan

- `ERR-0004` remains `FIXED`; its historical startup/readiness Ruff signatures did not recur.
- Core exact head `921c6868c8813c92da200cdd68a0ba12df583e9c` passed canonical Quality `33900087353 = success`.
- UI exact head `be55343dcaab9eb2afe80fe869000c139e6e2de1` has canonical Quality `33902213148` still in progress. Windows path safety, Linux storage, local-install smoke, specification validator, Ruff and mypy are green; full pytest is still running, so no PASS/failure claim is made.
- Backend exact head `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1` has canonical Quality `33900689788` with a Python-quality pytest failure. Windows path safety, Linux storage, local-install smoke, specification validator, Ruff and mypy passed. Canonical diagnostics artifact `9948717940` exposes exactly two failures in `tests/unit/test_lm_studio_response_limits.py`; these are tracked as `ERR-0009`.
- Current Develop is `e51e805266b625c008812ae5ab79435655ff1ca5`; no exact-head global PASS is claimed.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- root_cause: bool-safe/runtime validation missing before SQL mutation/cursor boundaries.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78` plus harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.

### ERR-0003 — Stale permanent-inspector harness contract
- severity: P1
- status: `FIXED`
- evidence: Backend `33755878184`; canonical UI `33745885426` passed byte-identical relevant product/harness blobs.
- root_cause: test contract lagged contextual `Evidence & Activity` inspector behavior.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- severity: P2
- status: `FIXED`
- evidence: `33785726577` B010; `33792012599` I001; exact-head `33804193396` SUCCESS.
- root_cause: bounded startup/readiness test-harness lint defects.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2
- status: `FIXED`
- evidence: UI `33822842314` mypy failure; corrected `33822861477` SUCCESS.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- severity: P2
- status: `FIXED`
- evidence: Backend `33833499697`; repaired-lineage `33838658964` SUCCESS.
- root_cause: static `Sequence[uuid.UUID]` annotation was trusted at runtime without explicit container validation.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- severity: P1
- status: `FIXED`
- evidence: post-integration `33838377083`; repaired-lineage `33838658964` SUCCESS.
- root_cause: Core integration carried `acceptance_service.py` without required `contradiction_review_gate.py`.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- first_seen: 2026-09-04
- severity: P2
- area: Qt/Desktop / Settings / test harness
- status: `FIXED`
- checked_sha: failing UI `5a77a4841dfdda120afaefccb698319d31a7d9e9`; intermediate `f7da16e05aa50da9ca17e5069a8880a84e34432e`; repeated failing `e6cb967c354f55a1cbb4ca1a4bbd2ff26b863b90`; final fix `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- evidence: `33845743958` and `33849890354` isolated the stale Settings runtime assertion after platform/static gates passed. Exact final fix Quality `33854660676` completed `success`.
- root_cause: first owner correction exposed a second stale harness expectation. Product runtime and accessibility state were consistent; the harness lagged the truthful loopback-only contract.
- files: `tests/unit/test_pathena_settings_runtime.py`; product reference `src/athena/desktop/pathena_settings_comprehension_5100.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- verification: canonical ATHENA Quality Gate `33854660676 = success` on exact fix SHA.
- risk: low; the fix retains substantive accessibility/network non-inference coverage via loopback-specific wording plus `pathenaInternetStateInferred is False`.
- integrator_handoff: no remaining ERR-0008 blocker; reject earlier red SHAs as globally green and preserve the verified final blobs.

### ERR-0009 — Local HTTP remaining-budget hardening leaves stale readline-size harness expectations
- first_seen: 2026-09-04
- severity: P2
- area: Backend / Provider-Transport / local HTTP test harness
- status: `IN_PROGRESS`
- checked_sha: Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1`.
- evidence: canonical ATHENA Quality Gate `33900689788`; Windows path safety PASS, Linux storage PASS, local-install smoke PASS, specification validator PASS, Ruff PASS, mypy PASS, full pytest FAIL. Diagnostics artifact `9948717940` reports exactly:
  - `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_uses_bounded_readline_without_whole_body_read`: expected `[17, 17, 17]`, actual `[17, 9, 2]`.
  - `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_rejects_many_small_lines_over_cumulative_limit`: expected `[9, 9, 9]`, actual `[9, 5, 1]`.
- repro: run the two focused pytest nodes above on Backend lineage containing product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386`.
- root_cause: product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386` intentionally changed `_BoundedLocalResponse.readline()` from constant `max_bytes + 1` reads to `remaining + 1` reads, but two pre-existing harness assertions still encode the old constant request-size behavior. The new actual sequences are the direct arithmetic consequence of cumulative remaining-budget enforcement. Product behavior is fail-closed and matches the hardening intent; this is a harness contract lag, not evidence for reverting the product guard.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- owner: Backend currently owns and is actively mutating this exact test/product lineage; Error must not race it this cycle.
- required_minimal_fix: retain all semantic response-size/overflow assertions and update only the stale request-size expectations to the remaining-budget sequences (`[17, 9, 2]` and `[9, 5, 1]`), or an equivalently strict assertion of decreasing `remaining + 1` requests. Do not weaken the byte cap, remove overflow assertions, skip/xfail, or revert `remaining + 1` product hardening.
- fix_sha: pending Backend owner correction.
- verification: pending exact new Backend SHA with both focused tests PASS, Ruff PASS, mypy PASS, full pytest PASS and canonical Quality success.
- risk: low if harness-only; security/runtime risk would increase if product hardening were reverted, which is prohibited.
- integrator_handoff: reject Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1` as globally green. Wait for a new exact Backend SHA that corrects the two stale expectations and passes canonical Quality. If no owner fix exists after one full additional non-colliding Backend cycle, Error may take the minimal harness-only fix on `postmerge/errors` under the hard progress rule.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
