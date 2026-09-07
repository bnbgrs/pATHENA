# pATHENA 11-Screen Reference Manifest

Baseline: `30dd27c97e948e59994e8cfbe01b1c77ce6c917b`
Integration target: `develop/pathena-next`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. The original image payloads are still not available for direct visual opening in the current repository/tool path. Therefore all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; UI-GAP-0067 action-help accessibility is exact-green; UI-GAP-0068 replaces visible receipt-validation implementation jargon with human job-action response language | `IMPLEMENTED_PENDING_VERIFY` | `849b72a882f8d07a5678bc0e4770b55229c18723` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation; UI-GAP-0061 accessibility help is exact-green | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research; lifecycle regression technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; UI-GAP-0060 accessibility help is exact-green | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `30dd27c97e948e59994e8cfbe01b1c77ce6c917b` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists and known technical interaction gaps for the stated state are closed, but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a real surface exists but a concrete current technical gap has a candidate fix that is not yet verification/integration complete.
- `PARTIAL` means a concrete structural, interaction or copy gap is evidenced and remains unresolved.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.