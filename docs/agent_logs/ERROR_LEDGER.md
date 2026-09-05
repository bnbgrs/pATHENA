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
- Baseline SHA observed this run: `de2f5a64e7a0fbc282df81db6beee3431297f2de`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization this run: `70eb579a1e1581f8164db91c5e2a0903e509b416`, merging Error lineage with current Develop without force, rebase or history rewrite.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0011`.
- BLOCKED: none.

## Current scan

- `ERR-0004` remains `FIXED`; its startup/readiness Ruff signatures did not recur.
- `ERR-0009` remains `FIXED` on canonical Backend Quality `33911612711 = success`.
- `ERR-0010` remains `FIXED` on exact descendant canonical Backend Quality `33921338439 = success`.
- `ERR-0011` is now `FIXED`: canonical UI Quality `33926653411` on exact owner fix SHA `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` completed with conclusion `success`.
- The ERR-0011 fix remains UI-local and fail-closed: provider/detail metadata reports `unavailable` when provider is absent; Provider/Transport, network, security, storage, recovery and actual runtime freshness behavior were not changed.
- Backend Quality `33925587762` on `d507de617f27976b174c1beadb22d8432fef63d6` also completed `success`; no new error is allocated from that previously pending signal.
- Newer exact worker-head Quality remains pending: UI `33930318851` on `37a097b9e97314184c36780b38b39b217418be12` and Backend `33929643363` on `235a13086985341edc02ee61e742e63a863974ab` are in progress and are neither PASS nor failure evidence.
- Current Develop exact head `de2f5a64e7a0fbc282df81db6beee3431297f2de` has no exact-head global PASS claim from this scan.

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
- status: `FIXED`
- checked_sha: failing Backend `f459035a701d6dad90d7be130e7a0644ae78201c`; correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`; verified descendant `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`.
- evidence: failing canonical Quality `33916312429`; exact descendant canonical Quality `33921338439 = success`.
- repro: `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline`.
- root_cause: the prior monotonic iterator modeled the old iterator-only deadline sequence; direct `readline()` added pre/post deadline checks and consumed additional timestamps.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`.
- verification: exact canonical Backend Quality `33921338439` completed `success` on `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`.
- risk: low; no production timeout, byte cap, routing or security guard was weakened.
- integrator_handoff: direct total-deadline slice is cleared by exact canonical success; retain fail-closed product behavior.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- first_seen: 2026-09-04
- severity: P2
- area: UI / Settings / provider detail accessibility state
- status: `FIXED`
- checked_sha: failing UI `3d74d43279d9a80bf891bb6bc31001b1e43490e2`; owner correction `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- evidence: failing canonical UI Quality `33922277491`: Windows path safety PASS, Linux storage PASS, local-install smoke PASS, validator PASS, Ruff PASS, mypy PASS, full pytest FAIL; primary assertion at `tests/unit/test_pathena_settings_provider_detail_state.py:77` was `assert 'fresh' == 'unavailable'`. Exact fix-head canonical UI Quality `33926653411` completed `success`.
- repro: `tests/unit/test_pathena_settings_provider_detail_state.py::test_unavailable_provider_detail_fails_closed_as_error` on failing SHA `3d74d43279d9a80bf891bb6bc31001b1e43490e2`.
- root_cause: `SettingsRuntimePanel.apply_snapshot()` used `resolved_model_freshness` directly for provider/detail metadata even when `provider is None`; semantic state was unavailable/error but metadata could remain `fresh`.
- files: `src/athena/desktop/pathena_settings_runtime.py`, `tests/unit/test_pathena_settings_provider_detail_state.py`.
- fix_sha: UI owner `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- fix: derive provider-specific freshness as `unavailable` whenever provider is absent and apply it only to provider/detail presentation metadata; no backend/provider/network/security behavior changed.
- verification: canonical UI Quality `33926653411` completed with conclusion `success` on exact fix SHA `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- risk: low and UI-local; freshness presentation remains fail-closed without changing actual provider transport state.
- integrator_handoff: UI-GAP-0018 correction is cleared by exact canonical success; preserve the UI-local fail-closed provider/detail metadata behavior.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
