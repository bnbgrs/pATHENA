# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@8ca3c7b87677a59b9d99d6a5b8703cfc78da6c28`.
- Worker: `postmerge/ui`.
- Current Develop was synchronized history-preservingly through two-parent NON-FORCE commit `769e5b0903ce26abab3f83369d2a4ef5b22159c6`; `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0032 — Library detail readers explicit keyboard-focus presentation

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `4be86b946333e88160d4f7a11fe4199c23d2c0ec` adds only the object-specific focus selectors for `persistentKnowledgeDetails`, `persistentClaimDetails`, and `semanticReviewDetails` to the existing canonical accent-border focus block.
- Focused regression `ebe9aaa0d465df78e52782ce0f2d4d5dab6a2086` verifies all three selectors and the canonical accent border without changing read-only behavior, content, selection routing, provenance, persistence, or runtime semantics.
- Exact UI head `062440397c9330ac23e9f8b3293d822f2451c902` passed ATHENA Quality Gate `34007202893 = success`.
- Exact documentation successor `3c5fe2e16293e9bfb8228e62b0f7a183b34a92f7` passed ATHENA Quality Gate `34009763554 = success`.

## UI-GAP-0033 — Library list focused-current rows

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

- Evidence: Screen 02 uses keyboard-focusable `persistentKnowledgeList`, `persistentClaimList`, and `semanticReviewList`. The foundation gave the list widget itself an accent focus border but had no row-level focused-current presentation, leaving the current row visually identical to its unfocused selected state.
- Product `5b6f8a5740d463524daf4cfae14c0335b2207693` adds only three object-specific `:focus::item:current` selectors using canonical readable text, `surface_hover`, and the existing 2px accent left edge.
- Focused regression `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d` verifies all three selectors and canonical focus tokens. Selection routing, item content, refresh behavior, provenance, persistence, and backend/runtime semantics are unchanged.
- Canonical Quality `34012044664` is pending on exact product/test head `35dacd3fc1ef3e6aa37051cfa14fb751f03c726d`.

## Integrator handoff

- UI-GAP-0032 remains READY: product `4be86b946333e88160d4f7a11fe4199c23d2c0ec`, focused regression `ebe9aaa0d465df78e52782ce0f2d4d5dab6a2086`, verified on exact successor `062440397c9330ac23e9f8b3293d822f2451c902` by Quality `34007202893 = success` and documentation successor `3c5fe2e16293e9bfb8228e62b0f7a183b34a92f7` by Quality `34009763554 = success`.
- Do not integrate UI-GAP-0033 until exact-head Quality `34012044664` succeeds.
- Current worker history includes Develop synchronization merge `769e5b0903ce26abab3f83369d2a4ef5b22159c6` with `develop/pathena-next@8ca3c7b87677a59b9d99d6a5b8703cfc78da6c28` as second parent.
- No backend/storage/security/provider/worker/scheduler semantics changed.

## Next UI step

Consume exact-head Quality `34012044664`; if green promote UI-GAP-0033 to `FIXED / INTEGRATOR_READY`, then inspect the next distinct Library/Knowledge keyboard-accessibility/state gap without reopening canonical-tab-focus, detail-reader-focus, or focused-current-list diagnoses.
