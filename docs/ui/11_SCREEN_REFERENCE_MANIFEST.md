# pATHENA 11-Screen Reference Manifest

Baseline: `c830b96a12d25914c52a0abc7749a6724b19cfae`
Integration target: `develop/pathena-next`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. Slot 01 has direct pixel evidence from the opened user-library image `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png`. Remaining slots stay `VISUAL_REFERENCE_PENDING` unless their original image payload is opened directly. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state from the exact implementation SHA.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `AVAILABLE_OPENED` — `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector; narrow left-owned primary navigation | `IMPLEMENTED_PENDING_VISUAL_REVIEW` — real composer 88 px; prompt 44 px; Sources 36 px; send target 44×44 outer geometry, with 42 px QSS content-box plus inherited 1 px border per side. Exact candidate Quality is green. | `90a51e111851f80c5e2388c11c4026c6ec62fa09` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research; UI-GAP-0003 lifecycle regression is technically verified and integrated | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; hierarchy/copy and contextual visibility are technically verified/integrated | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `c830b96a12d25914c52a0abc7749a6724b19cfae` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists and known technical interaction gaps for the stated state are closed, but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a real surface exists but a concrete current technical gap has a candidate fix that is not yet verification/integration complete.
- `PARTIAL` means a concrete structural, interaction or copy gap is evidenced and remains unresolved.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
