# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T11:50Z
Branch: `develop/pathena-next`
HEAD at run start: `675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads reviewed: Errors `567b61ccb36f5978c50568341318f43bea36fcce`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `a5e28d3c9d3f215620fe69a7dfa9e024155037cf`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact Develop canonical Quality `34468185990@675166fbf1d47b5bf9fe86d3a6b59cb28ea84d17 = SUCCESS`.
- No new worker product slice is promotion-ready. Errors only hands off the now-verified schema-reinitialization harness closure; Backend explicitly marks broad worker Storage/Migration/WAL history HOLD; Spec/Core and UI expose no new unintegrated bounded product slice.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not authoritative files under those names in the inspected current tree; no percentage or fabricated status is derived from them.
- UI source-of-truth remains `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` plus `docs/ui/VISUAL_GAP_LEDGER.md`; screenshot-level `MATCH` remains unproven.

## Bounded cross-cutting slice — Windows packaging parity

The persistent pypdf packaging guard was canonical-green only in the Linux Local-install smoke. Windows canonical Quality already covers native locality, storage/bootstrap/schema-reinitialization and Core/API restart behavior, but did not independently execute the packaging metadata smoke.

This slice adds the existing fail-closed `athena-packaging-smoke --json` command to the existing Windows path-safety job. It reuses the same locked environment and does not alter packaging metadata, dependency resolution, runtime code, Storage, Recovery, Security, tests or assertions.

Purpose: make pypdf packaging evidence explicitly cross-platform before Windows Beta instead of inferring Windows behavior from Linux-only packaging verification.

## Persistent release guards

- pypdf packaging remains fail-closed and is now explicitly exercised on Linux and Windows canonical lanes.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE topology remains guarded.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap, Core-startup and duplicate-column/schema-reinitialization remain explicitly represented in Windows canonical Quality.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA and freeze Develop while it is queued/in progress.
2. If exact Quality is red, use only diagnostics from that exact SHA and classify any Windows packaging failure separately from already-closed storage/schema signatures.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate.
4. Do not re-integrate already landed UI/Core slices.
