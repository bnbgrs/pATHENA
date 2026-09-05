# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened.
- Cascades are deduplicated under the primary root cause.
- `FIXED` requires observed verification; unverified or recurrent corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA observed this run: `f9938b0f3c3a016b1cc7837441caaec72974e1cf`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization: `5442abac714b0b7caf3a5c9c49fe151d4f7ccfb4`, parents prior Error head `a64daaba830b3cac1c67ec85c1bd2bafd1e3be39` and exact Develop head `f9938b0f3c3a016b1cc7837441caaec72974e1cf`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0011`.
- BLOCKED: none.

## Current scan

- Historical `ERR-0004` remains `FIXED`; no startup/readiness Ruff recurrence was observed.
- `ERR-0010` remains `FIXED`; the corrected six-timestamp stream-deadline fixture remains preserved in current Develop.
- Previously pending Backend Quality `33939326942` on `7d380631f69b8b9b9f580f01f4510760f11de577` completed `success` and was independently integrated as the bounded raw body-handle escape slice.
- Previously pending UI Quality `33939919740` on `550943bd4515514ea9e87b863d1b16f22b60445a` completed `success`.
- No `ERR-0012` is allocated. Current Backend head `cdc61439364028d29ecc56f3c39d34cd9a3dcc12` is under canonical Quality `33941852514`: Windows path safety PASS, Linux storage PASS, local install smoke PASS, Validator PASS, Ruff PASS, mypy PASS, full pytest still in progress at observation time.
- Current UI head `9ca1cb04031d618bd6d34d2df4a46d331d110a82` is under canonical Quality `33942660590`: Linux storage PASS, local install smoke PASS, Validator PASS, Ruff PASS, mypy PASS, Windows path-safety teardown still completing, full pytest still in progress at observation time.
- Pending runs are neither PASS nor failure evidence. No exact-current-Develop global-green claim is made.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- severity: P2
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- repro: malformed/bool-like runtime values crossing deletion-ledger mutation/cursor boundaries before SQL validation.
- root_cause: bool-safe runtime validation missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`, `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: focused deletion boundaries plus validator/Ruff/mypy/Windows/Linux-storage/local-install passed in canonical Backend evidence.
- risk: none absent recurrence.
- integrator_handoff: no action required.

### ERR-0002 — Deletion-boundary harness Ruff I001
- severity: P2
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- repro: canonical Ruff on deletion-boundary harness.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
- files: `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: canonical Ruff PASS `33749788522`.
- risk: none.
- integrator_handoff: no action required.

### ERR-0003 — Stale permanent-inspector harness contract
- severity: P1
- status: `FIXED`
- evidence: Backend `33755878184`; canonical UI `33745885426` passed byte-identical affected product/harness blobs.
- repro: shell tests asserted permanently visible inspector while product contract is contextual.
- root_cause: test contract lagged contextual `Evidence & Activity` inspector behavior.
- files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py`.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification: exact known-green UI lineage `33745885426 = success`.
- risk: do not reintroduce permanent-inspector contract.
- integrator_handoff: preserve contextual state-transition coverage.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- severity: P2
- status: `FIXED`
- evidence: `33785726577` exact B010 diagnostic; `33792012599` I001; exact-head `33804193396 = success`.
- repro: Ruff on startup/readiness harness.
- root_cause: bounded startup/readiness test-harness lint defects, not product startup failure.
- files: `tests/unit/test_pathena_startup_experience_2900.py` and related startup harness imports.
- fix_sha: `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`, `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification: canonical exact-head Quality `33804193396 = success`.
- risk: none absent exact recurrence.
- integrator_handoff: remain closed unless exact signature recurs.

### ERR-0005 — System-tray QApplication ownership typing
- severity: P2
- status: `FIXED`
- evidence: UI `33822842314` mypy failure; corrected `33822861477 = success`.
- repro: mypy on tray application ownership path.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- files: system-tray/UI application ownership implementation and focused tests.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.
- verification: canonical corrected UI Quality `33822861477 = success`.
- risk: none absent recurrence.
- integrator_handoff: no action required.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- severity: P2
- status: `FIXED`
- evidence: Backend `33833499697`; repaired-lineage `33838658964 = success`.
- repro: malformed runtime filter container accepted because static `Sequence[uuid.UUID]` annotation was trusted.
- root_cause: missing explicit runtime container/element validation.
- files: Research filter boundary implementation/tests.
- fix_sha: `462fba22637e0083c87df32f987134ce0fb3de00`; integrated equivalent `4b390b4fcc39affc1884f304f460901d07ea622a`.
- verification: canonical repaired lineage `33838658964 = success`.
- risk: none absent recurrence.
- integrator_handoff: preserve runtime-safe boundary checks.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- severity: P1
- status: `FIXED`
- evidence: post-integration `33838377083`; repaired-lineage `33838658964 = success`.
- repro: integrated `acceptance_service.py` imported missing contradiction-review gate.
- root_cause: Core integration omitted required dependency file.
- files: contradiction-review/acceptance Core module graph.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`.
- verification: canonical repaired lineage `33838658964 = success`.
- risk: preserve import graph completeness.
- integrator_handoff: no action required.

### ERR-0008 — Settings runtime/comprehension harness contract mismatch
- severity: P2
- status: `FIXED`
- evidence: `33845743958`, `33849890354`; final exact fix Quality `33854660676 = success`.
- repro: Settings harness expected stale runtime/comprehension copy/state after truthful loopback-only contract changes.
- root_cause: harness contract drift.
- files: `tests/unit/test_pathena_settings_runtime.py`.
- fix_sha: `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- verification: exact canonical Quality `33854660676 = success`.
- risk: do not weaken loopback-only/provider truthfulness.
- integrator_handoff: no action required.

### ERR-0009 — Local HTTP remaining-budget hardening leaves stale readline-size harness expectations
- severity: P2
- status: `FIXED`
- evidence: failing Quality `33900689788`; exact Backend Quality `33911612711 = success`.
- repro: tests expected constant readline request sizes instead of remaining-budget sizes.
- root_cause: correct product `remaining + 1` readline hardening left stale harness expectations.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; equivalent Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.
- verification: exact Backend Quality `33911612711 = success`.
- risk: never revert remaining-budget cap behavior.
- integrator_handoff: preserve `[17,9,2]` / `[9,5,1]` remaining-budget semantics or equivalent strict assertions.

### ERR-0010 — Direct total-deadline hardening invalidates stream timing harness
- first_seen: 2026-09-04
- severity: P2
- area: Backend / Provider-Transport / local HTTP test harness
- status: `FIXED`
- original evidence: failing Backend `33916312429`; corrected descendant `33921338439 = success`.
- recurrent evidence: Backend `33933291735` and UI `33936799048` reproduced the exact node `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline` with `TimeoutError`.
- repro: stale fixture `[10.0, 10.2, 10.6, 11.0]` is consumed by iterator plus direct `readline()` pre/post deadline checks before intended second-line timeout.
- root_cause: worker/integration drift reintroduced an obsolete four-timestamp harness fixture; product fail-closed deadline behavior is correct.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: corrected fixture lineage Backend `e62fcc2db49815e7d32579d0dc68a143f8af07b0` / corrected owner head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0`; UI exact-green descendant `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0`.
- verification: Backend `33936396203 = success`; UI `33937005854 = success`; current Develop preserves the corrected six-timestamp fixture `[10.0,10.2,10.4,10.6,10.8,11.0]`.
- risk: low if correction remains harness-only; no timeout, cumulative-byte, network, storage, recovery or security guard may be weakened.
- integrator_handoff: preserve the corrected fixture and direct total-deadline fail-closed behavior. Exact-current-Develop global Quality remains a separate readiness question.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- severity: P2
- status: `FIXED`
- evidence: failing UI `33922277491`; exact fix-head canonical UI Quality `33926653411 = success`.
- repro: `provider=None` detail state exposed `fresh` metadata.
- root_cause: provider/detail metadata reused snapshot freshness even when provider was unavailable.
- files: `src/athena/desktop/pathena_settings_runtime.py`, `tests/unit/test_pathena_settings_provider_detail_state.py`.
- fix_sha: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- verification: exact fix-head UI Quality `33926653411 = success`.
- risk: preserve fail-closed unavailable/error presentation semantics.
- integrator_handoff: no action required.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
