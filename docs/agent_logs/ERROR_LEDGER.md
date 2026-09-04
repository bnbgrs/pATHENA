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
- Baseline SHA: `c91e76804e74595f92c8eb624ce7c5d83b66bad2`
- Worker branch: `postmerge/errors`
- Synchronization: history-preserving NON-FORCE merge `964e71b98d6a417f87920fdb44a5630b87069424` of current Develop into Error lineage.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0009`.
- FIXED: `ERR-0001` through `ERR-0008`.
- BLOCKED: none.

## Current scan

- `ERR-0004` remains `FIXED`; its historical startup/readiness Ruff signatures did not recur.
- Backend advanced to `7688f49ea351749bf227a1683fd14aba719d9bb6` after the ERR-0009 handoff but still retained the two stale readline-size expectations. Its separate exact fix-head Quality `33900614960` on `d988c9faa171f4fe86aac4b5fa4d169e8ee34a41` was cancelled after a later branch update, so it is not verification evidence for ERR-0009.
- Under the hard progress rule, Error took the now non-colliding harness-only correction on `postmerge/errors`: `67f3f447621c4544a5fb2fe321e76b62347290e0` updates only the two request-size expectations to the already-observed remaining-budget sequences. Product code, byte caps, overflow assertions and security guards are unchanged.
- No exact canonical Quality run is yet associated with Error fix SHA `67f3f447621c4544a5fb2fe321e76b62347290e0`; therefore `ERR-0009` is `FIXED_PENDING_VERIFY`, not `FIXED`.
- Current Develop is `c91e76804e74595f92c8eb624ce7c5d83b66bad2`; no exact-head global PASS is claimed.

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
- status: `FIXED_PENDING_VERIFY`
- checked_sha: failing Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1`; Error fix `67f3f447621c4544a5fb2fe321e76b62347290e0`.
- evidence: canonical ATHENA Quality Gate `33900689788`; Windows path safety PASS, Linux storage PASS, local-install smoke PASS, specification validator PASS, Ruff PASS, mypy PASS, full pytest FAIL. Diagnostics artifact `9948717940` reports exactly:
  - `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_uses_bounded_readline_without_whole_body_read`: expected `[17, 17, 17]`, actual `[17, 9, 2]`.
  - `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_rejects_many_small_lines_over_cumulative_limit`: expected `[9, 9, 9]`, actual `[9, 5, 1]`.
- repro: run the two focused pytest nodes above on lineage containing product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386`.
- root_cause: product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386` intentionally changed `_BoundedLocalResponse.readline()` from constant `max_bytes + 1` reads to `remaining + 1` reads, but two pre-existing harness assertions still encoded the old constant request-size behavior. The actual sequences are the direct arithmetic consequence of cumulative remaining-budget enforcement. Product behavior is fail-closed and matches the hardening intent; this is a harness contract lag.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- owner: Error assumed the minimal harness-only fix after Backend completed an additional non-colliding cycle without correcting these two expectations.
- fix_sha: `67f3f447621c4544a5fb2fe321e76b62347290e0`.
- fix: changed only `raw.readline_sizes` expectations from `[17, 17, 17]` to `[17, 9, 2]` and `[9, 9, 9]` to `[9, 5, 1]`; all overflow, secrecy and byte-cap assertions remain intact; product code unchanged.
- verification: pending exact Error-fix SHA focused tests, Ruff, mypy, full pytest and canonical Quality. No workflow run was associated with the exact fix SHA at first check.
- risk: low; harness-only correction. Security/runtime risk would increase if product hardening were reverted, which remains prohibited.
- integrator_handoff: do not consume failing Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1` as green. Candidate correction is Error `67f3f447621c4544a5fb2fe321e76b62347290e0`, but it is not integration-ready until exact verification is green.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
