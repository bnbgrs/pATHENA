# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T06:51Z
Branch: `develop/pathena-next`
Run-start HEAD: `e6ba3d7557bd46094ad4e8f067a238e1c2375f8e`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Worker heads consumed: Errors `4134bb4ff3ab48b7e57fbfa86d92d6fd0e38cc2b`; Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `069dff56d64cd78e2ddd255460db375f8eeb3041`.
- Exact Develop canonical Quality `34567856833@e6ba3d7557bd46094ad4e8f067a238e1c2375f8e = SUCCESS`.
- Current Errors lineage is documentation/ledger-only versus Develop and keeps Backend-owned ERR-0033/BE-046 and ERR-0035/BE-052 open without competing product mutation.
- Backend still has no tested bounded candidate for BE-046 or BE-052; broad Backend history remains HOLD.
- UI has a new bounded Jobs/Settings contextual-inspector product candidate at `069dff56…`, but its exact Windows visual workflow `34571754932` fails during native eleven-surface capture before comparison/verdict. It is NOT READY.
- `docs/agent_logs/ERROR_LEDGER.md` exists on Develop but is historically stale relative to the current baseline; current Errors handoff/worker ledger evidence controls current open state. No `ALPHA_BETA_PROGRESS.md` is present on Develop and no synthetic completion percentage is recorded.
- Visual source of truth remains the current 11-screen manifest plus Visual Gap Ledger; every slot remains pending visual review and no screenshot-level `MATCH` is claimed.

## Cross-cutting tooling slice

No Worker product slice is READY. This run therefore adds one collision-free diagnostic hardening to the Windows visual workflow.

When native eleven-surface capture exits non-zero, `.github/workflows/ui-snapshot.yml` now preserves the renderer exit code and emits the generated `artifacts/visual-actual/manifest.json` into the job log before failing. If capture dies before the manifest exists, that state is logged explicitly. The workflow remains fail-closed; no capture, comparator, baseline, product, Security, Storage, Recovery or runtime acceptance condition is weakened.

This directly unblocks diagnosis of the current UI candidate, whose exact-SHA workflow fails inside the capture step while artifact metadata alone does not expose the renderer's recorded per-surface error.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv and Desktop/Worker two-EXE topology remain guarded.
- Exactly one Desktop instance with bounded workers remains guarded.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety and duplicate-column/Core-startup/storage-bootstrap signatures remain protected.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume canonical Quality for this tooling commit before any further Develop mutation.
2. Have the UI worker resynchronize from current Develop before producing its next candidate so the exact visual run includes current focused tests and capture diagnostics.
3. Keep `069dff56…` NOT READY until a new exact-head run shows the native capture/focused contracts succeed; do not infer readiness from a failed capture.
4. Keep Backend BE-046/BE-052 HOLD until bounded focused adversarial evidence exists.
5. Never promote visual `MATCH` without state-equivalent reference/current evidence.
