# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `adee2288d75b0abf56009d12e04bb0d63e9bc1d3`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0037 — Durable jobs list focused-current keyboard state

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `7a518d2ab2e7b0255187650ff961c6fa7132a284` adds only `QListWidget#durableJobList:focus::item:current` to the canonical focused-current selector block.
- Focused regression `3f17c1e68be68e6f560cd27e70dfca9f3961db95` locks the selector and canonical focus tokens.
- Exact UI documentation head `6558031bb31e5e35f5c8639bf4f5c8591f7fa250` passed ATHENA Quality Gate `34025529919 = success`.
- Durable job content, selection routing, refresh behavior, transition availability, scheduler behavior and backend/storage/security/runtime ownership are unchanged.

## UI-GAP-0038 — Sources list focused-current keyboard state

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `FilesWorkspace` creates keyboard-focusable `QListWidget#sourceList`. The shared foundation supplies widget-level focus and selected-row presentation, but the established focused-current selector block covered Library, Research and Jobs lists while omitting Sources.
- Product `ea1d62fedc1fa67715f4f1f7c20621931a4a3db8` adds only `QListWidget#sourceList:focus::item:current` to that canonical block, using readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `bc20c308e97cfdf88a8109f2b4a4d1d60b387a62` locks the selector and canonical focus tokens.
- Source capture, import, retrieval processing, provenance, selection routing, refresh behavior and backend/storage/security/runtime ownership are unchanged.

## Develop synchronization

Develop advanced to `86ab95c9bd31e52a8d65fd3b37f7c27556a6f3b9`, integrating the already-verified UI-GAP-0036 selector/test and refreshing the Integrator handoff. The exact Develop Integrator handoff was copied, then histories were joined by two-parent NON-FORCE merge `adee2288d75b0abf56009d12e04bb0d63e9bc1d3`. No force, rebase, history rewrite, `main` mutation or ATHENA mutation occurred.

## Integrator handoff

- UI-GAP-0037 is READY: product `7a518d2ab2e7b0255187650ff961c6fa7132a284`, focused regression `3f17c1e68be68e6f560cd27e70dfca9f3961db95`, exact verified head `6558031bb31e5e35f5c8639bf4f5c8591f7fa250`, Quality `34025529919 = success`.
- UI-GAP-0038 is NOT READY until canonical Quality succeeds on an exact candidate containing product, focused regression, manifest, ledger and this handoff.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Consume exact canonical Quality for the final UI-GAP-0038 candidate. If green, promote it to `FIXED / INTEGRATOR_READY`, return Screen 05 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then inspect the distinct `QPlainTextEdit#sourceDetails` keyboard-focus contract without reopening source-list focused-current or completed Jobs focus diagnoses.
