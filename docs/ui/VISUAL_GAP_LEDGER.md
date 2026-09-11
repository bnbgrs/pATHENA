# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current evidence — 2026-09-11 21:39 CEST

Run-start Develop: `c670d7809c9f0aa5e6c31956b57e897091f1b9d6`; run-start worker: `ecbc661224917f1793b122a94e269ae88b450bc2`. Exact worker canonical Quality `34635102754` and UI Focused Candidate `34635102820` are `SUCCESS`. Exact visual run `34635099776` produced all eleven Windows/PySide6 captures and the exact-SHA artifact; only its final fail-closed baseline verdict remains red.

All eleven user references and all eleven exact runtime captures were opened directly. Strict same-state accounting remains `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11`; the Light reference still has no real same-state runtime capture, and several other slots intentionally expose truthful empty/unavailable states instead of the populated references.

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN / HIGHEST RECURRING PRIORITY`

The reference family consistently preserves a narrow rail, large central workspace and contextual right column. Exact Help AFTER evidence at `ecbc661…` now proves the Help surface no longer covers the full shell: topbar, rail, central Help and right inspector are all visible in one real MainWindow capture. That closes the Help-host-geometry subgap, not the overall hierarchy gap.

Remaining recurrent examples are standalone ComfyUI, standalone/minimal PALLAS and standalone Command Palette, plus sparse/empty central compositions in state-mismatched core workspaces.

## VISUAL-GAP-0002 — contextual inspector

Category: `INSPECTOR / PAGE CONTEXT`
Severity: `P0/P1 visual`
Status: `OPEN / HELP CONTEXT NOW REPRODUCED`

Route-context work remains improved for Knowledge, Research, Jobs, Settings and Sources. The new exact Help MainWindow capture exposes a concrete remaining defect: Help is open while the right inspector still displays the previously active `SETTINGS / LOCAL` context. The reference instead presents Help-specific `Quick shortcuts` and `Help is current` status.

Next bounded correction must use real installed shortcuts and live capability-catalogue state only. Do not fabricate shortcut availability or runtime health.

## VISUAL-GAP-0003 — standalone/shell-host framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

- Help: workspace-host framing is now visually verified; remaining gap is information hierarchy + Help contextual inspector.
- ComfyUI: real local workflow controls, wrong standalone host and missing reference Connection framing.
- PALLAS: real graph, wrong standalone/minimal framing and missing rich contextual inspector.
- Command Palette: real commands, but standalone capture rather than overlay over active workspace.

Do not combine these. Finish Help first.

## Help BEFORE → AFTER

- BEFORE evidence path: child-only Help capture could not prove persistent shell chrome.
- AFTER exact `ecbc661224917f1793b122a94e269ae88b450bc2`: full MainWindow capture visibly retains topbar, rail and right inspector while Help is bounded to the central workspace.
- Remaining visible Help deviations: no Help secondary nav; no search field; no structured capability rows/cards; flatter typography/spacing; right inspector is stale Settings context; no Help-specific shortcut/current-status panel.
- Status remains `GAP`; no `CLOSE` or `MATCH` claim.

## Slot accounting

| Slot | Exact current status at `ecbc661…` |
|---|---|
| 01 ComfyUI | GAP |
| 02 PALLAS | GAP |
| 03 Settings | GAP / STATE_UNVERIFIED |
| 04 Help | GAP — host geometry visually verified; hierarchy + inspector context remain |
| 05 Workspace/Evidence | UNVERIFIED |
| 06 Jobs | GAP / STATE_UNVERIFIED |
| 07 Command Palette | GAP / CONTEXT_UNVERIFIED |
| 08 System | GAP / STATE_UNVERIFIED |
| 09 Research | GAP / STATE_UNVERIFIED |
| 10 Light workspace | UNVERIFIED / CURRENT_RENDER_UNAVAILABLE |
| 11 Local Memory/Knowledge | GAP / STATE_UNVERIFIED |

References opened: `11/11`. Exact runtime surfaces opened: `11/11`. Same-state/reference-equivalent pairs: `0/11`. `MATCH_0_OF_11`. `PAIRS_VERIFIED_0_OF_11`.

## Develop synchronization

Current Develop is one bounded Core/Knowledge commit beyond the worker merge base. This candidate imports the exact Develop Integrator handoff, Concept Note provenance/update source and their focused tests history-preservingly as the second parent. No UI product semantics, Backend/Storage/Security behavior or release guard is changed by that synchronization.

## Next visual slice

After consuming exact CI for the synchronized worker, keep Help as the only UI slice. Preserve its verified workspace host and seven-primary-page invariant; implement a live-data Help hierarchy and honest Help contextual inspector. Then run focused Qt/UI tests, canonical Quality and a new exact 11-surface capture before touching ComfyUI, PALLAS or Command Palette.
