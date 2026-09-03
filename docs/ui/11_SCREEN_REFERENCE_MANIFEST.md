# pATHENA 11-Screen Reference Manifest

Baseline: `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`
Worker: `postmerge/ui`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. File Library search can locate likely original pATHENA reference screenshots, but the relevant image payloads still could not be opened in this run. Therefore all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector | `VERIFIED` interaction contract — contextual inspector exact-head Quality passed; visual parity pending | `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research | `IMPLEMENTED_PENDING_VERIFY` — Qt lifecycle crash on full-view opening patched with focused regression coverage; exact-head verification pending | `034cb8d923d48bea708b48cac0ef0f6343511051` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; Evidence & Activity hierarchy integrated; contextual visibility contract exact-head verified | `VERIFIED` interaction contract — visual parity pending | `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `VERIFIED` in the implementation-status column verifies the stated technical/interaction contract only; while the reference source is `VISUAL_REFERENCE_PENDING`, it does not mean screenshot-level `MATCH`.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a concrete evidence-backed implementation exists and its current exact-head verification has not completed successfully yet.
- `PARTIAL` means a concrete structural, interaction, copy, or verification gap remains evidenced against the current design/product contract.
- A failed exact-head canonical run blocks promotion until the failing signature is understood and corrected.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
