# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA observed this run: `25089e434412e7c1b8ede229438324338a0d5da0`
- Worker branch: `postmerge/errors`
- Latest history-preserving NON-FORCE synchronization already present in Error lineage: `88725f431fe46e30e49d03d487f8ef9a8935260e`; no force, rebase or history rewrite was performed this run.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0011`.
- FIXED: `ERR-0001` through `ERR-0010`.
- BLOCKED: none.

## Fresh evidence

- `ERR-0004` remains fixed; its historical startup/readiness Ruff failures have not recurred.
- `ERR-0010` is now fixed: exact Backend descendant `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5` completed canonical Quality `33921338439` with conclusion `success`.
- UI Quality `33922277491` on `3d74d43279d9a80bf891bb6bc31001b1e43490e2` is a real new red signal. Windows path safety, Linux storage, local-install smoke, specification validator, Ruff and mypy all passed; full pytest failed.
- Exact primary failure: `tests/unit/test_pathena_settings_provider_detail_state.py::test_unavailable_provider_detail_fails_closed_as_error`, line 77, expected provider/detail accessibility freshness `unavailable` but observed `fresh`.
- Root cause: `SettingsRuntimePanel.apply_snapshot()` reused snapshot-level `resolved_model_freshness` for provider/detail metadata even when `provider is None`. This allowed an unavailable/error presentation to expose contradictory `fresh` metadata.
- UI owner already applied the minimal product correction in `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`: `provider_freshness = "unavailable" if provider is None else freshness`, applied only to provider/detail presentation metadata.
- Exact fix-head canonical Quality `33926653411` on `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` remains in progress; therefore `ERR-0011` is `FIXED_PENDING_VERIFY`, not `FIXED`.
- Current Backend Quality `33925587762` on `d507de617f27976b174c1beadb22d8432fef63d6` remains in progress and is not PASS/failure evidence yet.
- Current Develop `25089e434412e7c1b8ede229438324338a0d5da0` has no exact-head global PASS claim from this scan.

## ERR-0010 closure

- Severity: P2.
- Area: Backend / Provider-Transport / local HTTP test harness.
- Failing run: `33916312429` on `f459035a701d6dad90d7be130e7a0644ae78201c`.
- Harness correction: `14cdda954d621e9b9cb5fd8b7b2fdbda8297dc81`.
- Verification head: `c9d1a7a9ab782ae081e4699eecd436d6a0ff5fb5`.
- Verification run: `33921338439 = success`.
- Status: `FIXED`.
- Guard statement: preserve direct fail-closed total-deadline behavior; no timeout, byte-limit, routing or security guard was weakened.

## ERR-0011

- Severity: P2.
- Area: UI / Settings / provider detail accessibility state.
- Failing exact SHA: `3d74d43279d9a80bf891bb6bc31001b1e43490e2`.
- Failing canonical run: `33922277491`.
- Exact failing node: `tests/unit/test_pathena_settings_provider_detail_state.py::test_unavailable_provider_detail_fails_closed_as_error`.
- Exact assertion: expected `unavailable`, actual `fresh`.
- Owner correction: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- Verification run: `33926653411`, currently in progress.
- Status: `FIXED_PENDING_VERIFY`.

## Integrator handoff

- `ERR-0001` through `ERR-0010` are cleared.
- Backend direct total-deadline lineage may be treated as verified on exact canonical success `33921338439`; preserve its fail-closed behavior.
- Reject UI `3d74d43279d9a80bf891bb6bc31001b1e43490e2` as globally green because full pytest failed on the exact unavailable-provider freshness contradiction.
- Do not integrate or mark UI-GAP-0018 READY until exact fix head `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` completes canonical Quality `33926653411` successfully.
- The `ERR-0011` correction is UI-local metadata coherence only. Do not change Provider/Transport, network, security, storage, recovery or actual runtime freshness behavior to satisfy this test.
- If `33926653411` turns red, inspect the exact new diagnostic and mutate only that deduplicated primary cause; do not repeat the current root-cause narrative without new evidence.
- Current Develop still requires exact-head canonical verification after integration.

## Next scan

1. Consume completion of UI `33926653411`; mark `ERR-0011` `FIXED` only on exact canonical success.
2. Consume Backend `33925587762` and allocate `ERR-0012` only for a concrete deduplicated primary failure.
3. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, local install/start, Windows path safety and Linux storage scanning.
