# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@14ca6fece527d6b51956b3e5fa3ec7b291252420`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `a48cfbaea74c80792316777a7491b5e8245d0b23`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0033 — Library list focused-current rows

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `5b6f8a5740d463524daf4cfae14c0335b2207693` adds only object-specific focused-current selectors for `persistentKnowledgeList`, `persistentClaimList`, and `semanticReviewList`, using canonical readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d` verifies all three selectors and canonical focus tokens without changing selection routing, content, refresh behavior, provenance, persistence, or runtime semantics.
- Exact UI documentation head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea` passed ATHENA Quality Gate `34012079406 = success`.

## UI-GAP-0034 — Research job list focused-current row

Status: `FIXED / INTEGRATOR_READY`, P1.

- Evidence: `ResearchWorkspace` creates keyboard-focusable `QListWidget#researchJobList`; existing foundation styling provided widget focus and selected-row presentation but no row-level focused-current state.
- Product `0da430fdccb469b1edf8fd7adf01773b5ec5340f` adds only `QListWidget#researchJobList:focus::item:current` to the established focused-current selector block, using canonical readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `3d9339295f3c413c4c7a31c2a7037600bc3b93f6` verifies selector and canonical tokens. Durable research selection, refresh, cancellation, scheduler, backend/storage/security and runtime semantics are unchanged.
- Exact documentation head `5a40e75ed78293ddd8c1ea3533c5632d6dea2910` passed ATHENA Quality Gate `34014713429 = success`.

## Integrator handoff

- UI-GAP-0033 is READY: product `5b6f8a5740d463524daf4cfae14c0335b2207693`, focused regression `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d`, exact documentation head `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea`, Quality `34012079406 = success`.
- UI-GAP-0034 is READY: product `0da430fdccb469b1edf8fd7adf01773b5ec5340f`, focused regression `3d9339295f3c413c4c7a31c2a7037600bc3b93f6`, exact documentation head `5a40e75ed78293ddd8c1ea3533c5632d6dea2910`, Quality `34014713429 = success`.
- Current worker history includes Develop synchronization merge `a48cfbaea74c80792316777a7491b5e8245d0b23` with `develop/pathena-next@14ca6fece527d6b51956b3e5fa3ec7b291252420` as second parent.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Inspect the next distinct Research accessibility/state/interaction gap from current product evidence without reopening completed Library focus or research-job focused-current diagnoses. Register a new stable UI-GAP only when the current implementation proves a real gap, then keep the slice bounded and run canonical Quality on the exact candidate.
