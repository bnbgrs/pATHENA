# pATHENA 11-Screen Reference Manifest

Baseline: `0d4d621f8a38ddf8eccfa09622bf193687619943`
Worker: `postmerge/ui`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. The original image artifacts were not accessible in this run, so all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance | `PARTIAL` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `0d4d621f8a38ddf8eccfa09622bf193687619943` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists but visual parity is not proven.
- `PARTIAL` means a concrete structural, interaction or copy gap is already evidenced against the current design contract.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
