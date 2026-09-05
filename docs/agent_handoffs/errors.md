# pATHENA Error Handoff

## Baseline

- Baseline source: `develop/pathena-next`
- Baseline SHA observed this run: `de2f5a64e7a0fbc282df81db6beee3431297f2de`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization this run: `70eb579a1e1581f8164db91c5e2a0903e509b416`; no force, rebase or history rewrite was performed.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0011`.
- BLOCKED: none.

## Fresh evidence

- `ERR-0004` remains fixed; its historical startup/readiness Ruff failures have not recurred.
- `ERR-0011` is now fixed: exact UI owner correction `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` completed canonical Quality `33926653411` with conclusion `success`.
- The fixed primary signature was `tests/unit/test_pathena_settings_provider_detail_state.py::test_unavailable_provider_detail_fails_closed_as_error`, where unavailable provider/detail metadata incorrectly exposed `fresh` instead of `unavailable`.
- Root cause remains UI metadata coherence only: `SettingsRuntimePanel.apply_snapshot()` reused snapshot-level resolved-model freshness when `provider is None`. The verified correction derives provider-specific fail-closed freshness without changing Provider/Transport behavior.
- Previously pending Backend Quality `33925587762` on `d507de617f27976b174c1beadb22d8432fef63d6` also completed `success`; no new error is allocated from it.
- Newer worker-head Quality runs remain in progress and are not PASS or failure evidence: UI `33930318851` on `37a097b9e97314184c36780b38b39b217418be12`; Backend `33929643363` on `235a13086985341edc02ee61e742e63a863974ab`.
- Current Develop `de2f5a64e7a0fbc282df81db6beee3431297f2de` has no exact-head global PASS claim from this scan.

## ERR-0011 closure

- Severity: P2.
- Area: UI / Settings / provider detail accessibility state.
- Failing exact SHA: `3d74d43279d9a80bf891bb6bc31001b1e43490e2`.
- Failing canonical run: `33922277491`.
- Exact failing node: `tests/unit/test_pathena_settings_provider_detail_state.py::test_unavailable_provider_detail_fails_closed_as_error`.
- Exact assertion: expected `unavailable`, actual `fresh`.
- Owner correction: `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`.
- Verification run: `33926653411 = success` on the exact correction SHA.
- Status: `FIXED`.
- Guard statement: preserve UI-local fail-closed provider/detail freshness; do not alter actual provider transport, network, security, storage, recovery or runtime freshness semantics.

## Integrator handoff

- `ERR-0001` through `ERR-0011` are cleared.
- UI-GAP-0018 owner correction `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` is verified by exact canonical Quality `33926653411 = success` and may be considered error-cleared for integration review.
- Backend HTTP-error total-deadline lineage through `d507de617f27976b174c1beadb22d8432fef63d6` is independently green on canonical Quality `33925587762 = success`.
- Do not infer green status for newer UI `37a097b9e97314184c36780b38b39b217418be12` or Backend `235a13086985341edc02ee61e742e63a863974ab` while their exact canonical runs remain in progress.
- Current Develop still requires exact-head canonical verification after integration.

## Next scan

1. Consume UI `33930318851` and Backend `33929643363` when complete; allocate `ERR-0012` only for a concrete deduplicated primary failure.
2. Continue Packaging, Provider/Transport, Research/Jobs, Persistence/Recovery, Qt/Desktop, Security, local install/start, Windows path safety and Linux storage scanning.
3. Keep product defects in product code and harness defects in harness; never weaken assertions, Ruff rules, security/storage/recovery safeguards or platform protections.
