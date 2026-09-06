# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@3bd2b7f0bc25f9b3b756a1765b27db7ab787b789`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `aa51997f2370e7456be5e57612f56806c3709012`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0034 — Research job list focused-current row

Status: `FIXED / INTEGRATOR_READY`, P1.

- Evidence: `ResearchWorkspace` creates keyboard-focusable `QListWidget#researchJobList`; existing foundation styling provided widget focus and selected-row presentation but no row-level focused-current state.
- Product `0da430fdccb469b1edf8fd7adf01773b5ec5340f` adds only `QListWidget#researchJobList:focus::item:current` to the established focused-current selector block, using canonical readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `3d9339295f3c413c4c7a31c2a7037600bc3b93f6` verifies selector and canonical tokens. Durable research selection, refresh, cancellation, scheduler, backend/storage/security and runtime semantics are unchanged.
- Exact UI documentation head `5a40e75ed78293ddd8c1ea3533c5632d6dea2910` passed ATHENA Quality Gate `34014713429 = success`; exact synchronized documentation successor `bf7fadf849140697dc63c92c6a5c6c69335e3278` passed Quality `34017125454 = success`.

## UI-GAP-0035 — Research detail reader keyboard focus

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Current product evidence: `ResearchWorkspace` creates read-only `QPlainTextEdit#researchDetails`. It is keyboard-focusable for reading/copying, while the shared explicit focus selector already covered Help and Library detail readers but omitted this Research reader.
- Product `f9d0a01de648ea806bfd725c3b35a68fc9eb425d` adds only `QPlainTextEdit#researchDetails:focus` to the existing canonical accent-border focus block.
- Focused regression `4183addc10689496101c2b4d6ae7d45fcb4cf3d1` verifies the selector and canonical accent token without changing read-only behavior, content, durable research selection, cancellation, scheduler behavior, backend/storage/security semantics or runtime ownership.
- Canonical Quality `34019811058` was started on exact product/test head `4183addc10689496101c2b4d6ae7d45fcb4cf3d1`; it is not yet claimed green here.

## Integrator handoff

- UI-GAP-0034 is READY: product `0da430fdccb469b1edf8fd7adf01773b5ec5340f`, focused regression `3d9339295f3c413c4c7a31c2a7037600bc3b93f6`, exact documentation head `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`, Quality `34014713429 = success`, synchronized successor `bf7fadf849140697dc63c92c6a5c6c69335e3278`, Quality `34017125454 = success`.
- UI-GAP-0035 is NOT READY until canonical Quality succeeds on an exact candidate containing product and focused regression.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Consume the exact canonical Quality result for the UI-GAP-0035 product/test candidate. If green, promote UI-GAP-0035 to `FIXED / INTEGRATOR_READY`, return Screen 03 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, and then inspect one distinct Research or Jobs accessibility/state/interaction gap without reopening research-job focused-current or research-detail focus diagnoses.
