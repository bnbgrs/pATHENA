# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T13:53Z
Branch: `develop/pathena-next`
HEAD at run start: `38586782fd9b615ecd4226a4b0afe674d5520978`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `df3f63e0c0c717f0bbd8a4388535c5cd645e83ee`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34473603186@38586782fd9b615ecd4226a4b0afe674d5520978 = SUCCESS`; immediately before mutation no canonical Develop Quality was queued or in progress.
- No new worker product slice is promotion-ready. Errors only reclassifies stale worker evidence; Backend explicitly keeps broad Storage/Migration/WAL history HOLD; Spec/Core and UI expose no new unintegrated bounded product slice.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present under those exact names in the inspected current Develop tree; no percentage or substitute status is fabricated from them.
- UI source-of-truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven and status remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`.

## Bounded cross-cutting slice — Windows packaged runtime contracts

Current Develop already contains focused tests for packaged/frozen application dispatch, packaged process command construction, and the Windows Desktop/Worker packaging topology: `tests/unit/test_packaged_app_dispatch.py`, `tests/unit/test_packaged_process_launch.py`, and `tests/unit/test_windows_packaging_contract.py`. The canonical Linux full pytest covers these tests, but the Windows lane did not explicitly execute them.

This slice adds those three existing focused tests to the existing `windows-path-safety` job using the locked dev+desktop environment. It does not modify packaged runtime production code, argv handling, process supervision, packaging metadata, Storage, Recovery, Security, tests, or assertions.

Purpose: make fail-closed Frozen argv behavior and the Desktop/Worker two-EXE contract explicit Windows canonical evidence rather than inferring Windows behavior from Linux full-suite coverage.

## Persistent release guards

- pypdf packaging remains fail-closed and is explicitly exercised on Linux and Windows canonical lanes.
- Frozen argv remains fail-closed; its existing focused packaged-dispatch contract is now explicitly exercised in the Windows lane.
- Desktop/Worker two-EXE topology remains guarded; its existing Windows packaging contract is now explicit in canonical Windows Quality.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization remain explicitly represented in Windows canonical Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued/in progress.
2. If exact Quality is red, diagnose only that exact-SHA failure and do not weaken packaged/frozen argv or two-EXE contracts.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate.
4. Do not re-integrate already landed UI/Core slices.