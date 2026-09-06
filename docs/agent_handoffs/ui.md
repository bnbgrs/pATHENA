# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@da493c1390192425d50caddc451c1a497027027a`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `2da645b6b9fd24427e3fc70c36df21d8da1676fa`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0030 — Help reader explicit keyboard-focus presentation

Status: `FIXED / INTEGRATOR_READY`, P1.

- The rejected Command Palette query-focus hypothesis remains rejected: the Foundation already supplies canonical `QLineEdit:focus` presentation for `commandPaletteQuery`.
- Product `811b43c37e6010667b6779ccbf886715647e23dc` adds the missing explicit focus presentation for read-only `QPlainTextEdit#helpText`.
- Focused regression `9875e1c4e3a33753225398d0f2a08971e78977fe` verifies the canonical accent-border contract.
- Exact documentation successor `f09406daab9440ee77a06e907add84280b3ae936` passed ATHENA Quality Gate `34001923188 = success`.
- Existing F1 focus landing, read-only behavior, help content, shortcuts, command routing, accessibility metadata and backend/runtime semantics remain unchanged.

## UI-GAP-0031 — Canonical memory tabs need an explicit focused-selected state

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `canonicalMemoryTabs` already has specialized normal/hover/selected tab presentation, but no focused-selected rule. The selected state therefore did not distinguish keyboard focus on the tab bar from an unfocused selected tab.
- Product `089f005aa6d81a6a4a15cc8594c74eeeed417373` adds `QTabWidget#canonicalMemoryTabs QTabBar:focus::tab:selected` using only canonical readable text, `surface_hover`, and the existing 2px accent bottom edge.
- Focused regression `e18fe9945e805230aa9c1af95202d8b9c81ba822` verifies the selector and canonical tokens without changing tab labels, routing, selected semantics, accessibility metadata, or backend/runtime behavior.
- Canonical Quality `34004657500` is pending on exact product/test head `e18fe9945e805230aa9c1af95202d8b9c81ba822`.

## Integrator handoff

- UI-GAP-0030 is READY: bounded lineage `811b43c37e6010667b6779ccbf886715647e23dc -> 9875e1c4e3a33753225398d0f2a08971e78977fe`, verified by exact successor `f09406daab9440ee77a06e907add84280b3ae936` and Quality `34001923188 = success`.
- UI-GAP-0031 is NOT Integrator-ready until exact-head canonical Quality succeeds.
- Preserve the current Develop synchronization parent `da493c1390192425d50caddc451c1a497027027a`; do not absorb unrelated Backend/Core/Error worker heads.

## Next UI step

Consume canonical Quality `34004657500`. If green, promote UI-GAP-0031 to `FIXED / INTEGRATOR_READY`, update the Visual Gap Ledger and manifest, then continue with the next evidence-backed keyboard/accessibility/state gap without reopening completed focus diagnoses.
