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
- Baseline SHA: `6a9b933dcec80d4d104ac7d3be68351c46554864`
- Worker branch: `postmerge/errors`
- Synchronization: history-preserving NON-FORCE merge `88725f431fe46e30e49d03d487f8ef9a8935260e` of exact current Develop into Error lineage.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0010`.
- FIXED: `ERR-0001` through `ERR-0009`.
- BLOCKED: none.

## Current scan

- `ERR-0004` remains `FIXED`; its startup/readiness Ruff signatures did not recur.
- `ERR-0009` remains `FIXED` on canonical Backend Quality `33911612711 = success`.
- New concrete signal: canonical Backend Quality `33916312429` on `f459035a701d6dad90d7be130e7a0644ae78201c` passed Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy, but full pytest failed.
- Backend owner root-caused the failure to stale harness timing in `test_stream_iteration_enforces_monotonic_total_deadline` after product `2270477ccf7631471379774430745f1a81f24d36` added direct `read()`/`readline()` total-deadline checks.
- Harness-only correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81` preserves fail-closed deadline behavior and supplies timestamps through the full first-line check chain.
- Exact descendant canonical Quality `33921338439` on Backend head `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` currently has Windows path safety PASS, Linux storage PASS, local-install smoke PASS, validator PASS, Ruff PASS and mypy PASS; full pytest remains in progress. Therefore `ERR-0010` is not `FIXED` yet.
- Current UI canonical Quality `33922277491` on `3d74d43279d9a80bf891bb6bc31001b1e43490e2` remains in progress and is neither PASS nor failure evidence yet.
- Current Develop exact head `6a9b933dcec80d4d104ac7d3be68351c46554864` has no exact-head canonical global PASS evidence yet.

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
- severity: P2
- status: `FIXED`
- evidence: `33845743958`, `33849890354`; final exact fix Quality `33854660676 = success`.
- root_cause: stale Settings harness expectations after truthful loopback-only runtime/accessibility contract.
- files: `tests/unit/test_pathena_settings_runtime.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.

### ERR-0009 — Local HTTP remaining-budget hardening leaves stale readline-size harness expectations
- severity: P2
- status: `FIXED`
- evidence: failing Quality `33900689788`; diagnostics expected `[17,17,17]` vs actual `[17,9,2]` and expected `[9,9,9]` vs actual `[9,5,1]`; exact Backend Quality `33911612711 = success`.
- root_cause: correct product `remaining + 1` readline hardening left two old constant-size harness expectations.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; equivalent Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.

### ERR-0010 — Direct total-deadline hardening invalidates stream timing harness
- first_seen: 2026-09-04
- severity: P2
- area: Backend / Provider-Transport / local HTTP test harness
- status: `FIXED_PENDING_VERIFY`
- checked_sha: failing Backend `f459035a701d6dad90d7be130e7a0644ae78201c`; candidate Backend correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`; verification head `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`.
- evidence: canonical Quality `33916312429` passed Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy; only full pytest failed. Backend handoff identifies `test_stream_iteration_enforces_monotonic_total_deadline` as the failing harness after direct `readline()` gained its own pre/post deadline checks.
- repro: `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline` on lineage containing product `2270477ccf7631471379774430745f1a81f24d36` and focused tests `93e83640e69df9016fc4a10ac790e803fecf5d57`.
- root_cause: the previous four-value monotonic iterator modeled the old iterator-only deadline-check sequence; direct `readline()` now consumes additional pre/post timestamps and reaches the deadline during the first yielded line.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`.
- fix: harness-only timestamp sequence updated to cover `__iter__` pre, `readline` pre/post and `__iter__` post before reaching the deadline ahead of the second underlying read.
- verification: pending exact descendant canonical Quality `33921338439`; Windows/Linux-storage/local-install/validator/Ruff/mypy already PASS, full pytest still running.
- risk: low if canonical run completes green; no production timeout, byte cap, routing or security guard was weakened.
- integrator_handoff: do not integrate/declare this slice ready until `33921338439` completes success; if red, isolate the exact remaining primary signature before any further mutation.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
