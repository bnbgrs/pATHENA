# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@b1537fc138560fe85d4d97cf76c887b92e63c8f4`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `82dd049c014cd62248ba8277595122bab42225de`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0038 — Sources list focused-current keyboard state

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `ea1d62fedc1fa67715f4f1f7c20621931a4a3db8` adds only `QListWidget#sourceList:focus::item:current` to the canonical focused-current selector block.
- Focused regression `bc20c308e97cfdf88a8109f2b4a4d1d60b387a62` locks the selector and canonical focus tokens.
- Exact UI documentation head `3d89bffeef82244361e701738ebc05862d1a2b64` passed ATHENA Quality Gate `34028122788 = success`.
- Source capture, import, retrieval processing, provenance, selection routing, refresh behavior and backend/storage/security/runtime ownership are unchanged.

## UI-GAP-0039 — Sources detail reader keyboard-focus presentation

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `FilesWorkspace` creates read-only `QPlainTextEdit#sourceDetails`; the reader is keyboard-focusable for reading/copying and previously was omitted from the object-specific canonical plain-text reader focus block used by Help, Library, Research and Jobs.
- Product `6d2d0eb32fa0bcd6b2c1112070a36ce1401f6bfa` adds only `QPlainTextEdit#sourceDetails:focus` to that existing accent-border selector block.
- Focused regression `57636da80d3f3db586d1d728b4e6d39dd11896bd` locks the selector and canonical accent token.
- Read-only semantics, source content, processing state, selection routing, provenance and backend/storage/security/runtime ownership remain unchanged.

## Develop synchronization

Develop advanced from the prior shared base to `b1537fc138560fe85d4d97cf76c887b92e63c8f4`, adding only the verified Personal-Memory inferred-provenance domain contract/test plus the Integrator handoff on that lineage. Exact Develop blobs for `src/athena/memory/models.py`, `tests/unit/test_personal_memory_inferred_provenance_validation.py`, and `docs/agent_handoffs/integrator.md` were composed onto the UI tree and histories were joined by two-parent NON-FORCE merge `82dd049c014cd62248ba8277595122bab42225de`. No force, rebase, history rewrite, `main` mutation or ATHENA mutation occurred.

## Integrator handoff

- UI-GAP-0038 is READY: product `ea1d62fedc1fa67715f4f1f7c20621931a4a3db8`, focused regression `bc20c308e97cfdf88a8109f2b4a4d1d60b387a62`, exact verified head `3d89bffeef82244361e701738ebc05862d1a2b64`, Quality `34028122788 = success`.
- UI-GAP-0039 is NOT READY until canonical Quality succeeds on an exact candidate containing product, focused regression, manifest, ledger and this handoff.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Reconcile the Visual Gap Ledger with stable `UI-GAP-0038`/`UI-GAP-0039`, then consume canonical Quality on the exact final UI-GAP-0039 candidate. If green, promote it to `FIXED / INTEGRATOR_READY`, return Screen 05 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, and inspect the next distinct Sources/System keyboard-accessibility or state inconsistency without reopening source-list or source-detail focus diagnoses.
