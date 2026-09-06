# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@451b2f39377653b44fb178e58d86705b6026bef8`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `19ba40144577f6b36df20f68ec20f7aabb30f57c`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0036 — Jobs detail reader keyboard focus

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `605c63992e112a168ddeda403b561740d524c018` adds only `QPlainTextEdit#jobDetails:focus` to the established canonical accent-border block.
- Focused regression `8ae0f51e0637e75d7619e7fb9c4fe65679c6f626` locks the selector and canonical accent token.
- Exact UI documentation head `8cbec3ef97a13caf626450a0111ee3dc50b262cc` passed ATHENA Quality Gate `34022762486 = success`.
- Durable job content, filtering, action enablement/transitions, scheduler behavior, read-only semantics and backend/storage/security/runtime ownership are unchanged.

## UI-GAP-0037 — Durable jobs list focused-current keyboard state

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `JobsWorkspace` creates keyboard-focusable `QListWidget#durableJobList`. The shared foundation already provides widget-level focus plus selected-row presentation, but the established focused-current selector block covered Library and Research lists while omitting Jobs.
- Product `7a518d2ab2e7b0255187650ff961c6fa7132a284` adds only `QListWidget#durableJobList:focus::item:current` to that canonical block, using readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `3f17c1e68be68e6f560cd27e70dfca9f3961db95` locks the selector and canonical focus tokens.
- Durable job content, selection routing, refresh behavior, transition availability, scheduler behavior and backend/storage/security/runtime ownership are unchanged.

## Develop synchronization

Develop advanced by two commits after the previous UI run: the already-verified Research detail selector/test was integrated onto Develop and the Integrator handoff was refreshed. The Research selector/test were already byte-equivalent on the UI worker; the exact Develop Integrator handoff was copied, then the histories were joined by two-parent NON-FORCE merge `19ba40144577f6b36df20f68ec20f7aabb30f57c`. No force, rebase, history rewrite, `main` mutation or ATHENA mutation occurred.

## Integrator handoff

- UI-GAP-0036 is READY: product `605c63992e112a168ddeda403b561740d524c018`, focused regression `8ae0f51e0637e75d7619e7fb9c4fe65679c6f626`, exact verified head `8cbec3ef97a13caf626450a0111ee3dc50b262cc`, Quality `34022762486 = success`.
- UI-GAP-0037 is NOT READY until canonical Quality succeeds on an exact candidate containing product, focused regression, manifest, ledger and this handoff.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Consume exact canonical Quality for the final UI-GAP-0037 candidate. If green, promote it to `FIXED / INTEGRATOR_READY`, return Screen 04 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then inspect one distinct Jobs or Sources accessibility/state/interaction gap without reopening job-detail focus or durable-job-list focused-current diagnoses.
