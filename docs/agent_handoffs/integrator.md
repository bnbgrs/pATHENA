# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T14:52Z
Branch: `develop/pathena-next`
HEAD at run start: `0d3ca68731ded061b0720bd94d649f3dfed59a45`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `6477760a9fd2e849d20d128e62390ba27458a710`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `64dc45191f4d099b098ddd0a8a19666d9af1215c`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34486592055@0d3ca68731ded061b0720bd94d649f3dfed59a45 = SUCCESS`; immediately before mutation no canonical Develop Quality was queued or in progress.
- No new worker product slice is promotion-ready. Errors is documentation-only stale reclassification; Backend records exact Windows runtime evidence but its BE-046/BE-052 gaps have no focused candidate; Spec/Core and UI expose no new unintegrated bounded product slice.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not present under those exact names in the inspected current Develop tree; no percentage or substitute status is fabricated from them.
- UI source-of-truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven and status remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`.

## Bounded cross-cutting slice — Windows adaptive chat reserve contract

Current Develop contains `tests/unit/test_chat_context_reserve_contract.py`, a focused fail-closed contract that asserts the direct-chat default output reserve remains 2048 tokens, preserves the adaptive available-output calculation, caps the requested reserve to actual context availability, and keeps generation defaults aligned with the same 2048 reserve.

Canonical Linux full pytest already covers this test, but the Windows lane did not explicitly execute it. This slice adds only that existing focused test to `windows-path-safety` using the locked dev environment. It changes no chat production code, model/provider behavior, context arithmetic, Storage, Recovery, Security, tests or assertions.

Purpose: convert the persistent adaptive 2048-context Chat reserve requirement into explicit Windows canonical evidence before Windows Beta rather than inferring cross-platform behavior from Linux full-suite coverage.

## Persistent release guards

- pypdf packaging remains fail-closed and explicitly exercised on Linux and Windows canonical lanes.
- Frozen argv remains fail-closed and explicitly exercised in the Windows packaged runtime lane.
- Desktop/Worker two-EXE topology remains explicit in canonical Windows Quality.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement.
- Adaptive 2048-context Chat reserve remains guarded and is now explicitly exercised in Windows canonical Quality.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization remain explicitly represented in Windows canonical Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued/in progress.
2. If exact Quality is red, diagnose only that exact-SHA failure and do not weaken the adaptive reserve contract.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate; BE-046/BE-052 require focused candidate evidence before integration.
4. Do not re-integrate already landed UI/Core/runtime slices.
