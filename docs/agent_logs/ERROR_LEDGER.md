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
- Baseline SHA observed this run: `cf33955bcaa91649f2b5ac1142940e5e72ffa43a`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization: `4c26809ce681afaa8d08bb1983c1b71f2975e237`, parents prior Error head `1b0ba3a3b9dd01641cac368b23f29573e6df19f0` and exact Develop head `cf33955bcaa91649f2b5ac1142940e5e72ffa43a`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0010` (recurrent exact signature on newer worker lineages; corrected owner heads are still under canonical verification).
- FIXED: `ERR-0001` through `ERR-0009`, `ERR-0011`.
- BLOCKED: none.

## Current scan

- `ERR-0004` remains `FIXED`; its startup/readiness Ruff signatures did not recur.
- Previously pending Backend Quality `33933291735` on `4adcf14dc67a617a4a2a5ff942cc600e40aaf456` completed `failure`. Canonical diagnostics artifact `9959994409` shows exactly one primary pytest failure: `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline`, `TimeoutError`, total `1 failed, 4625 passed, 3 skipped, 2 warnings`. This is the exact `ERR-0010` signature, not a new error.
- Previously pending UI Quality `33933890301` on `2193332eeb3a390c263baa66e83324ff70a61168` also completed `failure`; successor UI run `33936799048` on `62e217098f60fe3d1417b5572947abc7fc5b4b40` reproduced the same single `ERR-0010` pytest signature with `1 failed, 4627 passed, 3 skipped, 2 warnings`. Validator, Ruff, mypy, Windows path safety, Linux storage and local install smoke were PASS on `33936799048`.
- Exact current Develop `cf33955bcaa91649f2b5ac1142940e5e72ffa43a` still carries the stale timing fixture `times = iter([10.0, 10.2, 10.6, 11.0])` while product `local_http.py` performs iterator pre-check plus direct `readline()` pre/post deadline checks. Therefore current Develop cannot be globally claimed green without exact verification/correction.
- UI owner head `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` has already applied the minimal harness-only correction `times = iter([10.0, 10.2, 10.4, 10.6, 10.8, 11.0])`; canonical UI Quality `33937005854` is in progress.
- Backend owner head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0` records the corresponding correction lineage; canonical Backend Quality `33936396203` is in progress.
- No `ERR-0012` is allocated: both fresh reds deduplicate to recurrent `ERR-0010` harness drift. Product deadline, byte-limit, transport, storage, recovery and security guards remain unchanged.

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
- evidence: failing Quality `33900689788`; exact Backend Quality `33911612711 = success`.
- root_cause: correct product `remaining + 1` readline hardening left two old constant-size harness expectations.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- fix_sha: Error `67f3f447621c4544a5fb2fe321e76b62347290e0`; equivalent Backend `0e966a49cd37d9ee6a4572ac4e35ce3d8018ff8e`.

### ERR-0010 — Direct total-deadline hardening invalidates stream timing harness
- first_seen: 2026-09-04
- severity: P2
- area: Backend / Provider-Transport / local HTTP test harness
- status: `FIXED_PENDING_VERIFY`
- original evidence: failing Backend `33916312429`; exact corrected descendant `33921338439 = success` on `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`.
- recurrent evidence: Backend `33933291735` on `4adcf14dc67a617a4a2a5ff942cc600e40aaf456` and UI `33936799048` on `62e217098f60fe3d1417b5572947abc7fc5b4b40` reproduce the exact same primary node `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline` with `TimeoutError`.
- root_cause: worker/integration branch drift reintroduced the old four-timestamp fixture after direct `readline()` gained pre/post deadline checks; the product fail-closed deadline behavior is correct.
- repro: stale fixture `[10.0, 10.2, 10.6, 11.0]` is exhausted semantically by iterator/readline checks before the intended second-line timeout boundary.
- files: `tests/unit/test_lm_studio_response_limits.py`; product reference `src/athena/model/adapters/local_http.py`.
- owner correction: UI `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` uses `[10.0, 10.2, 10.4, 10.6, 10.8, 11.0]`; Backend correction lineage current head `dd1311dfeec02030fe6e05f6bd8a81fc13f5fce0`.
- verification: `33937005854` and `33936396203` are in progress; do not mark `FIXED` until an exact corrected owner head completes canonical Quality successfully and Integrator preserves that harness correction on Develop.
- risk: low if correction remains harness-only; no timeout/byte/network/security guard may be weakened.
- integrator_handoff: do not integrate a stale fixture; preserve product direct-deadline behavior and import the corrected timing fixture only after exact owner-head green evidence.

### ERR-0011 — Unavailable provider leaks fresh accessibility freshness
- severity: P2
- status: `FIXED`
- evidence: failing UI `33922277491`; exact fix-head canonical UI Quality `33926653411 = success`.
- root_cause: provider/detail metadata reused snapshot freshness even when `provider is None`.
- files: `src/athena/desktop/pathena_settings_runtime.py`, `tests/unit/test_pathena_settings_provider_detail_state.py`.
- fix_sha: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
