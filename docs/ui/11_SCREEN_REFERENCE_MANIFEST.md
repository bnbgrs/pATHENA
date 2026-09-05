# pATHENA 11-Screen Reference Manifest

Baseline: `d14aca9504021bdacadb89dc478ca41545ab4316`
Integration target: `develop/pathena-next`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. The original image payloads are still not available for direct visual opening in the current repository/tool path. Therefore all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector; glyph-only primary rail retains human destination names through explicit accessible item text; global top navigation and primary glyph rail have explicit keyboard-focus treatment; composer Send has an explicit keyboard-focus candidate | `IMPLEMENTED_PENDING_VERIFY` | `UI-GAP-0028 candidate 8c132673f7a991ae1fc16e27b0d65342bdae02e9` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation; Local Core state is explicitly not Internet-access state; no-model and unsaved persistence states fail closed; provider identity/status remains truthful during non-fresh model snapshots; unavailable-provider and Core-failure detail copy is self-describing; empty/whitespace Core failure messages and Core health status cannot produce incomplete visible/accessibility errors; blank provider identity/status use self-describing presentation fallbacks; blank/whitespace provider detail uses a self-describing runtime fallback | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `77b3f9582d4530dbe081e3c81b8768ad00d3f050` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research; lifecycle regression technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; hierarchy/copy and contextual visibility technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d14aca9504021bdacadb89dc478ca41545ab4316` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists and known technical interaction gaps for the stated state are closed or separately registered, but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a real surface exists but a concrete current technical gap has a candidate fix that is not yet verification/integration complete.
- `PARTIAL` means a concrete structural, interaction or copy gap is evidenced and remains unresolved.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
