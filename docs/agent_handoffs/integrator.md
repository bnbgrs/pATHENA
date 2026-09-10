# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T16:48Z
Branch: `develop/pathena-next`
HEAD at run start: `3330a0092eaddf58fd3a4fdcb7128f77f01b0301`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `b7933c64c15763cc09b791b422ce0a09a83e9b4d`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `338e4514d144f4701e52515c0196e0f968f5db47`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34492275924@3330a0092eaddf58fd3a4fdcb7128f77f01b0301 = SUCCESS`; immediately before mutation no canonical Develop Quality was queued or in progress.
- No new worker product slice is promotion-ready. Errors has no active current error; Backend records BE-046/BE-052 as current source-trace gaps but has no bounded focused candidate; Spec/Core and UI expose no new unintegrated bounded product slice.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` were not treated as authoritative absent current exact-name evidence; no percentages are fabricated.
- UI source-of-truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven and status remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`.

## Bounded cross-cutting slice — Windows Core/API ownership lifecycle contracts

Current Develop contains focused Core/API process-boundary tests. `tests/unit/test_api_process_lock_boundaries.py` protects ownership-lock path/symlink and lock-close behavior; `tests/unit/test_api_process_lifecycle_boundaries.py` protects startup rollback, cleanup completion, invalid-port fail-fast behavior and shutdown-error translation.

Canonical Linux full pytest already covers these contracts, but the Windows lane did not explicitly execute them. This slice adds only those existing focused tests to `windows-path-safety` using the locked dev environment. It changes no process/runtime production code, worker topology, lock implementation, Storage, Recovery, Security, tests or assertions.

Purpose: convert Core/API ownership and lifecycle behavior relevant to the persistent one-Desktop/bounded-worker release guard into direct native Windows canonical evidence instead of relying only on Linux full-suite coverage and restart smoke.

## Persistent release guards

- pypdf packaging remains fail-closed and explicitly exercised on Linux and Windows canonical lanes.
- Frozen argv remains fail-closed and explicitly exercised in the Windows packaged runtime lane.
- Desktop/Worker two-EXE topology remains explicit in canonical Windows Quality.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement; this slice adds direct Windows ownership/lifecycle contract coverage without claiming that these two files alone exhaust the topology guard.
- Adaptive 2048-context Chat reserve remains explicitly exercised in Windows canonical Quality.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization remain explicitly represented in Windows canonical Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued/in progress.
2. If exact Quality is red, diagnose only that exact-SHA failure and do not weaken process ownership/lifecycle contracts.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate; BE-046/BE-052 require focused candidate evidence before integration.
4. Do not re-integrate already landed UI/Core/runtime slices.
