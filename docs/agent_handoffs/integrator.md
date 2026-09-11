# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-11T02:50Z
Branch: `develop/pathena-next`
Run-start HEAD: `f729959c7b2b0f14b495f06779c790d6cd0d281d`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Current worker heads: Errors `d9a74db65557bb1db89641c3cbc910d6d1bf6ec1`; Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `8ba83c27fcfc19c94339908a42352617421556f8`.
- Exact Develop canonical Quality `34552555541@f729959c7b2b0f14b495f06779c790d6cd0d281d = SUCCESS`.
- `ERROR_LEDGER.md` and `ALPHA_BETA_PROGRESS.md` are not treated as authoritative unless present on current Develop; no synthetic completion percentage is recorded.
- Visual source of truth remains the current 11-screen manifest plus Visual Gap Ledger; no screenshot-level `MATCH` is claimed.

## Worker qualification

- Errors current head is documentation-only and hands off current ERR-0033 evidence; no Error-owned product candidate is promoted.
- Spec/Core has no newer product head.
- Backend current head is documentation-only; Backend/Storage/Runtime prerequisites remain conservative HOLD without bounded exact-head candidate evidence.
- UI exact native-Windows evidence confirms the serialized capture harness now records truthful row/page identity for all seven workspace routes, but the current UI head is a documentation handoff and no new product slice is integrator-ready.

## Cross-cutting tooling slice

No bounded Worker product slice is READY. This run therefore adds one collision-free visual-harness guard.

`.github/workflows/ui-snapshot.yml` now parses `artifacts/visual-actual/manifest.json` immediately after native Windows capture and fails closed unless exactly seven workspace captures exist with one-to-one row, page-index, ordinal and canonical label identity for Chat, Knowledge, Research, Jobs, Files, System and Settings.

This turns the recently discovered mislabeled-route failure mode into an explicit CI invariant rather than relying on manual artifact inspection. It does not alter product rendering, baseline thresholds, comparator policy, visual verdict policy, Security, Storage, Recovery, Runtime or provider behavior. No Skip/XFail or assertion weakening is introduced.

## Persistent release guards

- pypdf packaging, fail-closed Frozen argv and Desktop/Worker two-EXE topology remain guarded.
- Exactly one Desktop instance with bounded workers remains guarded.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety and duplicate-column/Core-startup/storage-bootstrap signatures remain protected.
- Historical signatures are not reopened without exact-current reproduction.

## Next integration

1. Consume the exact-current Develop canonical Quality before any further Develop mutation.
2. Require exact candidate focused tests and native-Windows evidence for any UI product promotion.
3. Do not promote visual `MATCH` without state-equivalent reference/current evidence.
4. Keep Backend/Storage/Runtime prerequisites conservative until bounded exact-head evidence exists.
