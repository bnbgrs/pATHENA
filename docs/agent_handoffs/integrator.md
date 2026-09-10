# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T17:48Z
Branch: `develop/pathena-next`
HEAD at run start: `e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `86a990c600643a25168013ee18dce62fa35b55e1`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `c8ee2b0b0152a646a63ad4116526a8ce1fdabf90`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34504620300@e316843d1f45fc2fd3733d4ae10ec0ad1ac90f58 = SUCCESS`; immediately before mutation there were zero queued and zero in-progress canonical Develop runs.
- No new worker product slice is promotion-ready. Errors opens `ERR-0033` as the Backend-owned BE-046 Windows emergency-reserve directory-identity gap and makes no product mutation; Backend confirms BE-046/BE-052 remain OPEN but provides no bounded focused candidate; Spec/Core and UI expose no new unintegrated bounded product slice.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present under those exact names in current searchable repository evidence and therefore are not synthesized or treated as authoritative.
- UI source of truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven and all eleven slots remain `IMPLEMENTED_PENDING_VISUAL_REVIEW` pending real exact-SHA renders against opened originals.

## Bounded cross-cutting slice — Windows Core/API server lifecycle contract

Current Develop already contains `tests/unit/test_api_server_lifecycle_boundaries.py`. It protects fail-fast port validation before runtime construction, complete server cleanup ordering and exception propagation, duplicate/noncanonical Content-Length rejection, exact canonical request-body reads, and cleanup-failure translation.

Canonical Linux full pytest already covers this file, but the native Windows release lane did not explicitly execute it. This slice adds that existing focused test to the already-established `Run Windows Core/API ownership lifecycle regressions` step beside the process lock/lifecycle contracts.

This changes no API/server/process production code, worker topology, lock semantics, request parsing behavior, Storage, Recovery or Security behavior, and changes no test assertion. It supplies direct native-Windows evidence for the Core/API startup/shutdown boundary that participates in the persistent one-Desktop/bounded-worker and Core-startup release guards.

## Persistent release guards

- pypdf packaging remains fail-closed and explicitly exercised on Linux and Windows canonical lanes.
- Frozen argv remains fail-closed and explicitly exercised in the Windows packaged runtime lane.
- Desktop/Worker two-EXE topology remains explicit in canonical Windows Quality.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement; process ownership/lifecycle plus server lifecycle are now explicitly selected for native Windows verification without claiming this exhausts the topology guard.
- Adaptive 2048-context Chat reserve remains explicitly exercised in Windows canonical Quality.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization remain explicitly represented in Windows canonical Quality.
- BE-046 and BE-052 remain Backend-owned OPEN source-trace gaps; this Integrator slice does not mutate or weaken those invariants.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued/in progress.
2. If exact Quality is red, diagnose only that exact-SHA failure and do not weaken server/process lifecycle contracts.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate; BE-046/BE-052 require focused candidate evidence before integration.
4. Do not re-integrate already landed UI/Core/runtime slices.
