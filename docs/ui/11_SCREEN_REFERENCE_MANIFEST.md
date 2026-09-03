# pATHENA 11-Screen Reference Manifest

Baseline: `280066cc5450f172693e2ee913bd269b6755f7bb`
Worker: `postmerge/ui`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. File Library search can locate likely original pATHENA reference screenshots, but the relevant image payloads still could not be opened in this run. Therefore all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector | `PARTIAL` — contextual inspector slice exists but canonical pytest verification failed | `ff14f8fbe9c99e043521605c1ae790f20e807ae2` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; Evidence & Activity hierarchy is integrated; contextual visibility remains unverified after failed canonical pytest | `PARTIAL` | `ff14f8fbe9c99e043521605c1ae790f20e807ae2` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `280066cc5450f172693e2ee913bd269b6755f7bb` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a concrete evidence-backed implementation exists and has not yet produced contradictory exact-head verification.
- `PARTIAL` means a concrete structural, interaction, copy, or verification gap remains evidenced against the current design/product contract.
- A failed exact-head canonical run blocks promotion until the failing signature is understood and corrected.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
