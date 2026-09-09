# pATHENA 11-Screen Reference Manifest

Baseline: `7617509e405c47fd872ad49f9a047e098c9f06a0`
Integration target: `develop/pathena-next`

This is the canonical eleven-slot inventory. Original user reference pixels are now partially available through the connected file library and have been directly opened for Workspace/Chat, Knowledge/PALLAS, Evidence/Inspector, Research and a multi-screen Chat/Knowledge/Research/Jobs composition. A screenshot-level `MATCH` still requires opening a real rendered current build beside the corresponding original reference.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `ACTUAL_REFERENCE_OPENED` | Near-black quiet workspace, narrow navigation, large central work area, large composer, sparse orange, contextual inspector | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a426469b503c6276cd6d1fd3ed6d89be0af67948` |
| 02 | Library / Knowledge | `ACTUAL_REFERENCE_OPENED` | Reduced knowledge workspace, graph/provenance structure, dark neutral panels, restrained orange | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a426469b503c6276cd6d1fd3ed6d89be0af67948` |
| 03 | Research | `ACTUAL_REFERENCE_OPENED` | Research workflow/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a426469b503c6276cd6d1fd3ed6d89be0af67948` |
| 04 | Jobs | `ACTUAL_REFERENCE_OPENED_IN_MULTI_SCREEN_REFERENCE` | Durable job state and controls; no fabricated queue state; dark neutral shell with sparse orange emphasis | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a426469b503c6276cd6d1fd3ed6d89be0af67948` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `7617509e405c47fd872ad49f9a047e098c9f06a0` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `7617509e405c47fd872ad49f9a047e098c9f06a0` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `7617509e405c47fd872ad49f9a047e098c9f06a0` |
| 08 | PALLAS | `ACTUAL_REFERENCE_OPENED` | Characteristic but non-dominant data-driven semantic view based on real Sources/Claims/Knowledge/Research | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a426469b503c6276cd6d1fd3ed6d89be0af67948` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `7617509e405c47fd872ad49f9a047e098c9f06a0` |
| 10 | Grounded Chat / Evidence & Activity | `ACTUAL_REFERENCE_OPENED` | Explicit Sources/Evidence/Claims/Knowledge relationships and contextual inspector without synthesized provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a426469b503c6276cd6d1fd3ed6d89be0af67948` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `7617509e405c47fd872ad49f9a047e098c9f06a0` |

## Global verified visual-foundation slice

`UI-GAP-0004` changes the shared visual token foundation from navy/blue-led surfaces to deep neutral black surfaces with functional orange `#F26A21`. Exact worker head `a426469b503c6276cd6d1fd3ed6d89be0af67948` passed ATHENA Quality Gate `34291934346`. This is a technical/reference-direction closure, not screenshot parity.

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means the real surface exists and its stated technical contracts are implemented, but screenshot parity is not proven.
- `PARTIAL` means a concrete structural, interaction or copy gap is evidenced and remains unresolved.
- Missing per-slot image access is an evidence limitation, not permission to invent dimensions, spacing, colors or controls.
- Visible controls require a real product path or an explicit unavailable/not-implemented state.
