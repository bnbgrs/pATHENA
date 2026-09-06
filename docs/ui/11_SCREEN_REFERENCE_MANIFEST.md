# pATHENA 11-Screen Reference Manifest

Baseline: `ff780f2edf367320340771ffc3176d9fc1724c5c`
Integration target: `develop/pathena-next`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. The original image payloads are still not available for direct visual opening in the current repository/tool path. Therefore all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector; glyph-only primary rail retains human destination names through explicit accessible item text; global top navigation, primary glyph rail, composer Send and Workspace action controls have explicit keyboard-focus treatments | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real research process/results with restrained hierarchy and provenance | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation; Local Core state is explicitly not Internet-access state; no-model and unsaved persistence states fail closed; provider identity/status remains truthful during non-fresh model snapshots; unavailable-provider and Core-failure detail copy is self-describing; empty/whitespace Core failure messages and Core health status cannot produce incomplete visible/accessibility errors; blank provider identity/status use self-describing presentation fallbacks; blank/whitespace provider detail uses a self-describing runtime fallback | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `77b3f9582d4530dbe081e3c81b8768ad00d3f050` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research; lifecycle regression technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities; command query already inherits canonical `QLineEdit:focus`; F1 read-only help content deliberately receives focus and now has a bounded explicit focus candidate (`UI-GAP-0030`) pending canonical verification | `IMPLEMENTED_PENDING_VERIFY` | `9875e1c4e3a33753225398d0f2a08971e78977fe` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; hierarchy/copy and contextual visibility technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `ff780f2edf367320340771ffc3176d9fc1724c5c` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists and known technical interaction gaps for the stated state are closed or separately registered, but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a real surface exists but a concrete current technical gap has a candidate fix that is not yet verification/integration complete.
- `PARTIAL` means a concrete structural, interaction or copy gap is evidenced and remains unresolved.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
