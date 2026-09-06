# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@fd15a75212acac7f88886117835b8d754577ea91`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `b87a34706e1acb77087345f81412ca2b70f6eb1d`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0033 — Library list focused-current rows

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `5b6f8a5740d463524daf4cfae14c0335b2207693` adds only object-specific focused-current selectors for `persistentKnowledgeList`, `persistentClaimList`, and `semanticReviewList`, using canonical readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d` verifies all three selectors and canonical focus tokens without changing selection routing, content, refresh behavior, provenance, persistence, or runtime semantics.
- Exact UI documentation head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea` passed ATHENA Quality Gate `34012079406 = success`.

## UI-GAP-0034 — Research job list focused-current row

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: `ResearchWorkspace` creates keyboard-focusable `QListWidget#researchJobList`; existing foundation styling provided widget focus and selected-row presentation but no row-level focused-current state.
- Product `0da430fdccb469b1edf8fd7adf01773b5ec5340f` adds only `QListWidget#researchJobList:focus::item:current` to the established focused-current selector block, using canonical readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `3d9339295f3c413c4c7a31c2a7037600bc3b93f6` verifies selector and canonical tokens. Durable research selection, refresh, cancellation, scheduler, backend/storage/security and runtime semantics are unchanged.
- Canonical Quality `34014651392` was started on the exact product/test head and was pending when documentation was written.

## Integrator handoff

- UI-GAP-0033 is READY: product `5b6f8a5740d463524daf4cfae14c0335b2207693`, focused regression `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d`, exact documentation head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea`, Quality `34012079406 = success`.
- Do not integrate UI-GAP-0034 until exact candidate Quality succeeds.
- Current worker history includes Develop synchronization merge `b87a34706e1acb77087345f81412ca2b70f6eb1d` with `develop/pathena-next@fd15a75212acac7f88886117835b8d754577ea91` as second parent.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Consume exact-candidate Quality for UI-GAP-0034. If green, promote UI-GAP-0034 to `FIXED / INTEGRATOR_READY` and Screen 03 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, then inspect the next distinct Research accessibility/state gap without reopening completed Library focus diagnoses.
