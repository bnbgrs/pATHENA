# pATHENA UI Handoff

## Current baseline

- Base reviewed: `develop/pathena-next@3ad1437409eb4104aba5484afe56b139191a0a54`.
- Worker: `postmerge/ui`.
- Current Develop history was synchronized history-preservingly through two-parent NON-FORCE commit `747cfa4a77d54d669512fa8adc7d3ce31989f164`; independent comparison confirms Develop is the merge base with `behind_by=0`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## Runtime/release regression guard

Known Windows packaging/process-tree/startup/chat-context/lane-lock crash classes remain release-acceptance regressions only unless reproduced on the exact current SHA. This UI slice does not alter Desktop/Worker/Scheduler spawn ownership, backend/storage/security semantics, or claim Windows promotion readiness.

## UI-GAP-0029 — explicit keyboard focus for Workspace action controls

Status: `FIXED / INTEGRATOR_READY`, P1.

- Product `d25d563ed02ac677a038f522c050e7942d6b0462` adds a shared `:focus` presentation for `detailsToggle`, `contextToggle`, `newChatButton`, `deleteChatButton`, `rememberMessageButton`, `addKnowledgeButton`, and `groundButton` using only canonical `text`, `surface_hover`, and `accent` tokens.
- Focused regression `a4cfa5522cb666c9cf53ae53c5a297746fee2f38` verifies all seven selectors and the canonical focus declarations.
- Exact final UI head `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa` passed ATHENA Quality Gate `33996745959 = success`.
- No routing, accessible labels, enabled/disabled behavior, checked-state semantics, Backend/Storage/Security/Provider/transport/persistence/provenance behavior, or runtime spawn logic changed.

## UI-GAP-0030 — Command Palette query lacks explicit keyboard-focus presentation

Status: `OPEN`, P1.

- Current `QLineEdit#commandPaletteQuery` has a specialized canvas background and strong border but no explicit `:focus` rule.
- `CommandPaletteController.open()` deliberately lands keyboard focus on `commandPaletteQuery`, so this is an evidenced keyboard-state gap rather than a speculative visual mismatch.
- The existing query already exposes `accessibleName="Command search"`, an accessible description, placeholder copy, and real command filtering; those product contracts must remain unchanged.
- Smallest intended correction: add a canonical-token `QLineEdit#commandPaletteQuery:focus` treatment, then add focused stylesheet coverage and run canonical Quality on the exact candidate. No command routing or backend/runtime behavior belongs in this slice.

## Integrator handoff

- UI-GAP-0029 is READY: exact UI head `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa`, Quality `33996745959 = success`.
- Current worker is history-preservingly synchronized with `develop/pathena-next@3ad1437409eb4104aba5484afe56b139191a0a54` through `747cfa4a77d54d669512fa8adc7d3ce31989f164`.
- UI-GAP-0030 is OPEN and not Integrator-ready; no product candidate is claimed yet.

## Next UI step

Implement only UI-GAP-0030: add explicit canonical focus presentation for `commandPaletteQuery`, preserve query focus landing, accessibility metadata, command filtering and activation behavior, add focused stylesheet/Qt coverage, and run canonical Quality on the exact candidate. Do not repeat completed glyph-label, top-bar-focus, rail-focus, Send-focus, or Workspace-action-focus diagnoses.
