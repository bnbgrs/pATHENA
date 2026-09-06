# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@be0e8da5127f17f6bbc3cbbc8c58496102c9135c`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `a0c499a580e7afd8ecbd66d0faddf463c0df5ad5`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0039 — Sources detail reader keyboard-focus presentation

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `6d2d0eb32fa0bcd6b2c1112070a36ce1401f6bfa` adds only `QPlainTextEdit#sourceDetails:focus` to the existing canonical accent-border selector block.
- Focused regression `57636da80d3f3db586d1d728b4e6d39dd11896bd` locks the selector and canonical accent token.
- Exact UI head `d955ccd53e3e2c7f98af0f6f3838be1ffa9b6fe6` passed ATHENA Quality Gate `34031028328 = success`.
- Source content, import/retrieval processing, selection routing, read-only semantics, provenance and backend/storage/security/runtime ownership remain unchanged.

## UI-GAP-0040 — System detail keyboard-focus presentation

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `SystemWorkspace` creates `QLabel#systemDetail` and explicitly enables `Qt.TextInteractionFlag.TextSelectableByKeyboard`; that label is keyboard-interactive for text selection, but the canonical focus block had no `QLabel#systemDetail:focus` selector.
- Product `330fd20ec285b44dee8c9f89597a9c75e55c9c95` adds only `QLabel#systemDetail:focus` to the existing accent-border focus selector block.
- Focused regression `4cba0e0235ea5094f9f39b4d3f615879ca4362df` locks the selector and canonical accent token.
- Runtime facts, refresh routing, Core/provider/storage/security semantics and text-selection behavior are unchanged.

## Develop synchronization

Develop advanced to `be0e8da5127f17f6bbc3cbbc8c58496102c9135c` with corrected-lineage Local HTTP runtime-boundary integration and Integrator documentation. Exact verified product/test blobs were composed onto the UI tree and both histories were joined by two-parent NON-FORCE merge `a0c499a580e7afd8ecbd66d0faddf463c0df5ad5`. No force, rebase, history rewrite, `main` mutation or `bnbgrs/ATHENA` mutation occurred.

## Integrator handoff

- UI-GAP-0039 is READY: product `6d2d0eb32fa0bcd6b2c1112070a36ce1401f6bfa`, focused regression `57636da80d3f3db586d1d728b4e6d39dd11896bd`, exact verified head `d955ccd53e3e2c7f98af0f6f3838be1ffa9b6fe6`, Quality `34031028328 = success`.
- UI-GAP-0040 is NOT READY until canonical Quality succeeds on an exact candidate containing product, focused regression, manifest, ledger and this handoff.
- No backend/storage/security/provider/worker/scheduler semantics changed by UI.

## Next UI step

Consume canonical Quality on the exact final UI-GAP-0040 candidate. If green, promote UI-GAP-0040 to `FIXED / INTEGRATOR_READY`, return Screen 06 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then inspect one distinct System/Settings keyboard-accessibility, state or interaction inconsistency without reopening System-detail, Sources-detail or Sources-list focus diagnoses.
