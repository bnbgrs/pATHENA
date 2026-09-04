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
- Baseline SHA: `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`
- Worker branch: `postmerge/errors`
- Synchronization: history-preserving NON-FORCE merge `09bc08b6945e4097c07998768738e0ad1f1760be` of exact current Develop into Error lineage.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0009`.
- FIXED: `ERR-0001` through `ERR-0008`.
- BLOCKED: none.

## Current scan

- `ERR-0004` remains `FIXED`; its historical startup/readiness Ruff signatures did not recur.
- Error candidate `67f3f447621c4544a5fb2fe321e76b62347290e0` corrects only the two stale readline-size expectations; product code, byte caps, overflow behavior and secrecy/security assertions are unchanged.
- Backend independently converged on the same harness correction at `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`; current Backend handoff head is `225db6c031551a2b79edf0d74b331a33e359ad26`.
- Exact canonical Quality `33911612711` on Backend head `225db6c031551a2b79edf0d74b331a33e359ad26` is still in progress. Windows path safety, Linux storage regressions and local-install smoke have passed; specification validator, Ruff and mypy have passed; full pytest is still running.
- Pending full pytest is neither PASS nor failure evidence, so `ERR-0009` remains `FIXED_PENDING_VERIFY`, not `FIXED`.
- Error is now synchronized non-force to Develop `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358` while preserving its candidate correction.

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
- checked_sha: failing Backend `2d9375d8afbeb05eea8d0b9149ffd3f352e4a9c1`; Error fix `67f3f447621c4544a5fb2fe321e76b62347290e0`; equivalent Backend owner correction `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`; current Backend verification head `225db6c031551a2b79edf0d74b331a33e359ad26`.
- evidence: canonical ATHENA Quality Gate `33900689788` failed only full pytest after Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy passed. Diagnostics artifact `9948717940` reported exactly:
  - `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_uses_bounded_readline_without_whole_body_read`: expected `[17, 17, 17]`, actual `[17, 9, 2]`.
  - `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_rejects_many_small_lines_over_cumulative_limit`: expected `[9, 9, 9]`, actual `[9, 5, 1]`.
- repro: run the two focused pytest nodes above on lineage containing product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386`.
- root_cause: product commit `2981624e0f7eef8c2e94b6f0eb86a859132a2386` intentionally changed `_BoundedLocalResponse.readline()` from constant `max_bytes + 1` reads to `remaining + 1` reads, but two pre-existing harness assertions still encoded the old constant request-size behavior. Product behavior is fail-closed and matches the hardening intent; this is a harness contract lag.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- owner: Error applied the minimal harness-only fix after the non-colliding owner-cycle threshold; Backend then independently applied an equivalent owner correction.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; equivalent Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.
- fix: changed only `raw.readline_sizes` expectations from `[17, 17, 17]` to `[17, 9, 2]` and `[9, 9, 9]` to `[9, 5, 1]`; all overflow, secrecy and byte-cap assertions remain intact; product code unchanged.
- verification: canonical Backend Quality `33911612711` on exact head `225db6c031551a2b79edf0d74b331a33e359ad26` currently has Windows path safety PASS, Linux storage PASS, local-install smoke PASS, validator PASS, Ruff PASS and mypy PASS; full pytest remains in progress. No final PASS/FIXED claim yet.
- risk: low; harness-only correction. Security/runtime risk would increase if product hardening were reverted, which remains prohibited.
- integrator_handoff: prefer the owner-equivalent correction lineage once `33911612711` completes green; until then do not consume the current Backend head as globally green and do not revert remaining-budget hardening.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
