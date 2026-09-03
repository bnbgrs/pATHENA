# pATHENA 11-Screen Reference Manifest

Baseline: `e98c88e0d3b41b81de7efa70873729f873038080`
Integration target: `develop/pathena-next`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. The original image payloads are still not available for direct visual opening in the current repository/tool path. Therefore all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state plus spec-required desktop tray lifecycle; UI-GAP-0005 candidate exposes only real Open/System/Quit paths and marks missing model/Internet/pause commands unavailable | `IMPLEMENTED_PENDING_VERIFY` | `27281ce08e1e3d5021cc8a362c11f172818c0742` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research; UI-GAP-0003 lifecycle regression is technically verified and integrated | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; hierarchy/copy and contextual visibility are technically verified/integrated | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `df60ad0e0b3084da05a8b55d94a227798296a1ac` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states; UI-GAP-0004 is canonically green in Quality run `33804193396` | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists and known technical interaction gaps for the stated state are closed, but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a real surface exists but a concrete current technical gap has a candidate fix that is not yet verification/integration complete.
- `PARTIAL` means a concrete structural, interaction or copy gap is evidenced and remains unresolved.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
