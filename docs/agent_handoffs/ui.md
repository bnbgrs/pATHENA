# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@b5d888b09774e70a389457f568a8079faf130b5e`.
- Worker: `postmerge/ui`.
- Current Develop history was synchronized history-preservingly through two-parent NON-FORCE commit `43c3fdd7304210e88f4acb6f6cf6747542fc27d7`; the exact current Integrator handoff was then copied onto the worker at `ee34615775157a949400d3c8adf40a0357556e69`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0028 — explicit keyboard focus for composer Send

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product/test `8c132673f7a991ae1fc16e27b0d65342bdae02e9` adds the explicit `QPushButton#sendButton:focus` presentation while preserving 48px geometry, hover/pressed states and routing.
- Exact UI head `5a5ba2681412c32c181e63026ce1b92574675d64` passed ATHENA Quality Gate `33991088294 = success`.
- Exact synchronized successor `5604ee6bdf4783a096bd08cbbf2e08b9fb5ae303` passed ATHENA Quality Gate `33993942327 = success`.
- Develop subsequently integrated the bounded Send-focus slice at `996f07d3efca994536e5c9cadbf72eb24eb8dd25`.

## UI-GAP-0029 — explicit keyboard focus for Workspace action controls

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

Evidence from the current specialized stylesheet showed `detailsToggle`, `contextToggle`, `newChatButton`, `deleteChatButton`, `rememberMessageButton`, `addKnowledgeButton`, and `groundButton` with transparent normal borders plus hover and/or checked/disabled states but no explicit keyboard-focus presentation.

- Product `d25d563ed02ac677a038f522c050e7942d6b0462` adds a shared `:focus` presentation for the seven real Workspace controls using only canonical `text`, `surface_hover`, and `accent` tokens.
- Focused regression `a4cfa5522cb666c9cf53ae53c5a297746fee2f38` verifies all seven selectors and the canonical focus declarations.
- No routing, accessible labels, enabled/disabled behavior, checked-state semantics, Backend/Storage/Security/Provider/transport/persistence/provenance behavior, or runtime spawn logic changed.
- Ledger and exact eleven-slot manifest mark Screen 01 `IMPLEMENTED_PENDING_VERIFY`; no `FIXED`, visual-match, or Windows-runtime-ready claim is made before canonical exact-head Quality succeeds.

## Integrator handoff

- UI-GAP-0028 remains READY and is already integrated on Develop.
- UI-GAP-0029: DO NOT INTEGRATE until canonical Quality succeeds on the exact final UI descendant containing product `d25d563ed02ac677a038f522c050e7942d6b0462`, focused regression `a4cfa5522cb666c9cf53ae53c5a297746fee2f38`, ledger, manifest, and this handoff.
- Current worker is history-preservingly based on `develop/pathena-next@b5d888b09774e70a389457f568a8079faf130b5e` through `43c3fdd7304210e88f4acb6f6cf6747542fc27d7`.

## Next UI step

Consume exact-head Quality first. If green, promote UI-GAP-0029 to `FIXED / INTEGRATOR_READY`, return Screen 01 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, and then inspect the next concrete Workspace/Command-Palette keyboard-focus or accessibility inconsistency. Do not repeat completed glyph-label, top-bar-focus, rail-focus, Send-focus, or Workspace-action-focus diagnoses.