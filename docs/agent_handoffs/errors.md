# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA: `6a9b933dcec80d4d104ac7d3be68351c46554864`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization: `88725f431fe46e30e49d03d487f8ef9a8935260e`, with parents prior Error head `2ee9c374fd931a099de27b5ea8bd9dae0c876b76` and exact Develop `6a9b933dcec80d4d104ac7d3be68351c46554864`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0010`.
- FIXED: `ERR-0001` through `ERR-0009`.
- BLOCKED: none.

## Fresh evidence

- `ERR-0004` remains fixed; its historical startup/readiness Ruff failures have not recurred.
- `ERR-0009` remains fixed on exact canonical Backend Quality `33911612711 = success`.
- Backend Quality `33916312429` on `f459035a701d6dad90d7be130e7a0644ae78201c` is a real new red signal: Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy passed; full pytest failed.
- Backend owner isolated the single current root cause to stale timing in `tests/unit/test_lm_studio_response_limits.py::test_stream_iteration_enforces_monotonic_total_deadline` after direct `read()`/`readline()` total-deadline enforcement was added in product `2270477ccf7631471379774430745f1a81f24d36`.
- Harness-only correction `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81` supplies timestamps for `__iter__` pre, `readline` pre/post and `__iter__` post so expiry occurs before the second underlying read. No product deadline, byte-limit, routing, storage, recovery or security guard is weakened.
- Exact descendant Backend Quality `33921338439` on `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` currently has Windows path safety PASS, Linux storage PASS, local-install smoke PASS, validator PASS, Ruff PASS and mypy PASS; full pytest is still running. Therefore `ERR-0010` remains `FIXED_PENDING_VERIFY`, not `FIXED`.
- UI Quality `33922277491` on `3d74d43279d9a80bf891bb6bc31001b1e43490e2` is still in progress and is neither PASS nor failure evidence yet.
- Current Develop `6a9b933dcec80d4d104ac7d3be68351c46554864` has no exact-head global PASS evidence yet.

## ERR-0010

- Severity: P2.
- Area: Backend / Provider-Transport / local HTTP test harness.
- Failing exact SHA: `f459035a701d6dad90d7be130e7a0644ae78201c`.
- Failing canonical run: `33916312429`.
- Product hardening: `2270477ccf7631471379774430745f1a81f24d36`.
- Focused product tests: `93e83640e69df9016fc4a10ac790e803fecf5d57`.
- Harness correction: `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`.
- Verification head: `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`.
- Verification run: `33921338439`, currently in progress.
- Status: `FIXED_PENDING_VERIFY`.

## Integrator handoff

- `ERR-0001` through `ERR-0009` remain cleared.
- Do not treat Backend `f459035a701d6dad90d7be130e7a0644ae78201c` as globally green; its full pytest failed.
- Do not integrate or mark the direct total-deadline slice READY until exact descendant `33921338439` completes success.
- Preserve product fail-closed total-deadline enforcement; the root cause is harness timing drift, not a reason to revert direct deadline checks.
- If `33921338439` turns red, inspect its exact diagnostics and mutate only the remaining primary root cause; do not repeat the existing hypothesis without new evidence.
- Current Develop must receive exact-head canonical verification after any integration.

## Next scan

1. Consume completion of Backend `33921338439`; mark `ERR-0010` `FIXED` only on real success, otherwise isolate the exact remaining signature.
2. Consume UI `33922277491` and allocate `ERR-0011` only for a concrete deduplicated primary failure.
3. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, local install/start, Windows path safety and Linux storage scanning.
