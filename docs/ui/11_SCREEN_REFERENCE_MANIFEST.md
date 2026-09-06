# pATHENA 11-Screen Reference Manifest

Baseline: `6c7fdb4f2cf22215ac065ce6d2fad7b15e54b650`
Integration target: `develop/pathena-next`

This manifest is the canonical inventory for the eleven user-provided pATHENA UI references. The original image payloads are still not available for direct visual opening in the current repository/tool path. Therefore all pixel/composition claims remain `VISUAL_REFERENCE_PENDING`. No slot may be promoted to `MATCH` without opening the actual reference and comparing it against a real rendered pATHENA state.

| Slot | Surface / state | Reference source | Evidence-backed intent available now | Implementation status | Last checked SHA |
|---|---|---|---|---|---|
| 01 | Workspace / Chat | `VISUAL_REFERENCE_PENDING` | Quiet central workspace; chat as work document; large composer; contextual evidence/activity inspector; glyph-only primary rail retains human destination names through explicit accessible item text; global top navigation, primary glyph rail, composer Send and Workspace action controls have explicit keyboard-focus treatments | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `a0ba6bd47f4b8a6e91e8f6c222334c99cbe1a3aa` |
| 02 | Library / Knowledge | `VISUAL_REFERENCE_PENDING` | Reduced knowledge workspace with real durable knowledge/claim provenance; canonical memory tab, detail-reader focus and focused-current row presentation for Knowledge/Claim/Decision lists are technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `644c3cd5e3fd9c646b5e9d881a821b25d55b70ea` |
| 03 | Research | `VISUAL_REFERENCE_PENDING` | Real durable research process/results with restrained hierarchy and provenance; research job list focused-current keyboard state and read-only research detail focus presentation are technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `089a0e4b0b8fc43e37f00f8288f64cd62014fbb4` |
| 04 | Jobs | `VISUAL_REFERENCE_PENDING` | Real durable-job state and controls; no fabricated queue state; read-only job detail focus and durable-job list focused-current presentation are technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `6558031bb31e5e35f5c8639bf4f5c8591f7fa250` |
| 05 | Sources / Files | `VISUAL_REFERENCE_PENDING` | Real source/file state with import and provenance surfaces; source-list focused-current keyboard presentation and read-only source detail focus are technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `d955ccd53e3e2c7f98af0f6f3838be1ffa9b6fe6` |
| 06 | System | `VISUAL_REFERENCE_PENDING` | Real local runtime/core/provider/storage/backup state; System detail and runtime status-value keyboard focus are technically verified; Security posture live values have technically verified keyboard selection/copy coverage under `UI-GAP-0042` | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `81b8d6c2c250a412bb2947b2b356d9111c10b995` |
| 07 | Settings | `VISUAL_REFERENCE_PENDING` | Local-model/context/output/reasoning controls with reduced presentation; Local Core state is explicitly not Internet-access state; no-model and unsaved persistence states fail closed; provider identity/status remains truthful during non-fresh model snapshots; unavailable-provider and Core-failure detail copy is self-describing; empty/whitespace Core failure messages and Core health status cannot produce incomplete visible/accessibility errors; blank provider identity/status use self-describing presentation fallbacks; blank/whitespace provider detail uses a self-describing runtime fallback; the keyboard-focusable reasoning/thinking checkbox has verified canonical visible focus under `UI-GAP-0043` | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `b021424a3d6b79786b695b00356c2f98fa7390dc` |
| 08 | PALLAS | `VISUAL_REFERENCE_PENDING` | Characteristic but non-dominant, data-driven semantic view based on real Sources/Claims/Knowledge/Research; lifecycle regression technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `b1537fc138560fe85d4d97cf76c887b92e63c8f4` |
| 09 | Command Palette / Help | `VISUAL_REFERENCE_PENDING` | Keyboard-first command/search surface backed by real capabilities; command query inherits canonical `QLineEdit:focus`; F1 read-only help content deliberately receives focus and has explicit verified focus presentation (`UI-GAP-0030`) | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `f09406daab9440ee77a06e907add84280b3ae936` |
| 10 | Grounded Chat / Evidence & Activity | `VISUAL_REFERENCE_PENDING` | Contextual evidence, claims, sources and activity without synthesized provenance; hierarchy/copy and contextual visibility technically verified | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `b1537fc138560fe85d4d97cf76c887b92e63c8f4` |
| 11 | Startup / Empty / Disconnected state | `VISUAL_REFERENCE_PENDING` | Quiet local-first startup and truthful unavailable/empty states | `IMPLEMENTED_PENDING_VISUAL_REVIEW` | `b1537fc138560fe85d4d97cf76c887b92e63c8f4` |

## Promotion rules

- `MATCH` requires an opened original reference plus a real rendered state from the exact implementation SHA.
- `IMPLEMENTED_PENDING_VISUAL_REVIEW` means a real product surface exists and known technical interaction gaps for the stated state are closed or separately registered, but visual parity is not proven.
- `IMPLEMENTED_PENDING_VERIFY` means a real surface exists but a concrete current technical gap has a candidate fix that is not yet verification/integration complete.
- `PARTIAL` means a concrete structural, interaction or copy gap is evidenced and remains unresolved.
- Missing image access is an evidence limitation, not permission to invent dimensions, colors, spacing or controls.
- Controls shown in a future reference may only be implemented when backed by a real product path or explicitly represented as unavailable.
