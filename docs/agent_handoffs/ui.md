# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@62aa4e9ff20919f32d5147d183521fbf98f49535`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `ed009ba30f78f31dd9152e8001f96fb4c7ad4def`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0031 — Canonical memory tabs explicit focused-selected state

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `089f005aa6d81a6a4a15cc8594c74eeeed417373` adds `QTabWidget#canonicalMemoryTabs QTabBar:focus::tab:selected` using canonical readable text, `surface_hover`, and the existing 2px accent bottom edge.
- Focused regression `e18fe9945e805230aa9c1af95202d8b9c81ba822` verifies the selector and canonical tokens without changing tab labels, routing, selected semantics, accessibility metadata, or backend/runtime behavior.
- Exact documentation successor `856d9f56fac059f257451c2e31fd35b4e554e55f` passed ATHENA Quality Gate `34004718037 = success`.

## UI-GAP-0032 — Library detail readers need explicit keyboard-focus presentation

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `KnowledgeWorkspace` creates three read-only, keyboard-focusable detail readers with object names `persistentKnowledgeDetails`, `persistentClaimDetails`, and `semanticReviewDetails`. The shared Foundation styles all `QPlainTextEdit` surfaces but its explicit focus selector covered only `QPlainTextEdit#helpText`, leaving these Library readers without the same explicit pATHENA focus-state contract.
- Product `4be86b946333e88160d4f7a11fe4199c23d2c0ec` adds only those three object-specific `:focus` selectors to the existing canonical accent-border focus block.
- Focused regression `ebe9aaa0d465df78e52782ce0f2d4d5dab6a2086` verifies all three selectors share the canonical accent-border declaration.
- Read-only behavior, detail contents, selection routing, provenance, copy/history controls, persistence and backend/runtime semantics are unchanged.

## Integrator handoff

- UI-GAP-0031 is READY: product `089f005aa6d81a6a4a15cc8594c74eeeed417373`, focused regression `e18fe9945e805230aa9c1af95202d8b9c81ba822`, verified on exact successor `856d9f56fac059f257451c2e31fd35b4e554e55f` by Quality `34004718037 = success`.
- UI-GAP-0032 is NOT Integrator-ready until exact-head canonical Quality succeeds.
- Current worker history includes Develop synchronization merge `ed009ba30f78f31dd9152e8001f96fb4c7ad4def` with `develop/pathena-next@62aa4e9ff20919f32d5147d183521fbf98f49535` as second parent.

## Next UI step

Run/consume canonical Quality on the exact UI-GAP-0032 successor. If green, promote UI-GAP-0032 to `FIXED / INTEGRATOR_READY`, return Screen 02 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then inspect the next distinct Library/Knowledge keyboard-accessibility/state gap without reopening completed tab-focus or detail-reader-focus diagnoses.
