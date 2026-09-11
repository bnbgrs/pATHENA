# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current evidence — 2026-09-11 19:40 CEST

Run-start Develop: `fec368f50307a9e24038baca3a80b10ee2a3c4fc`; run-start worker: `d71bf6951c10920eb709dbe5bb3e708c72b43c6a`. The previous exact worker UI Focused Candidate is green. Canonical Quality is red only at mypy for one UI-owned unreachable branch in `pathena_capability_help.py`; specification validation, Ruff, all 4854 executed tests and platform/storage smoke lanes passed.

All 11 references and all 11 exact Windows/PySide6 runtime images for rendered product `b6aaaac887535bfcafa7e5784d0dc0b590758f36` were opened again. Help still clearly covers the full shell. This candidate keeps the seven-primary-page invariant while moving Help from the full reference shell into the existing central `conversation` workspace frame. The one Develop-only UI CI change is synchronized history-preservingly in the same candidate.

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN / HIGHEST PRIORITY`

References consistently preserve topbar, narrow rail, central workspace and contextual right column. The pre-mutation Help screenshot obscures that chrome because its transient widget is parented to the full `referenceShell`. This candidate instead parents Help to the real central workspace frame and sizes it to that frame, leaving shell chrome as siblings.

Next evidence gate: exact AFTER Help rendering must visibly retain topbar, rail and inspector. Do not upgrade status from GAP from source/tests alone.

## VISUAL-GAP-0002 — contextual inspector

Category: `INSPECTOR / PAGE CONTEXT`
Severity: `P0/P1 visual`
Status: `REDUCED / ROUTE-CONTEXT SUBGAP CLOSED`

The rendered baseline retains truthful contexts for Knowledge, Research, Jobs, Settings and Sources. System remains fail-closed and runtime-derived. Remaining deviations are primarily empty-vs-populated state and richer reference composition.

## VISUAL-GAP-0003 — standalone/shell-host framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

- Help: shell-owned, seven-page invariant fixed; this candidate narrows its host to the central workspace body. Exact AFTER image still required.
- ComfyUI: real local workflow controls, wrong standalone host and missing reference Connection framing.
- PALLAS: real graph, wrong standalone/minimal framing and missing rich contextual inspector.
- Command Palette: real commands, but standalone capture rather than overlay over active workspace.

Do not combine these. Finish Help first.

## Slot accounting

| Slot | Status at last exact rendered product `b6aaaac…` |
|---|---|
| 01 ComfyUI | GAP |
| 02 PALLAS | GAP |
| 03 Settings | GAP / STATE_UNVERIFIED |
| 04 Help | GAP — shell chrome obscured; bounded workspace-host correction now in candidate |
| 05 Workspace/Evidence | UNVERIFIED |
| 06 Jobs | GAP / STATE_UNVERIFIED |
| 07 Command Palette | GAP / CONTEXT_UNVERIFIED |
| 08 System | GAP / STATE_UNVERIFIED |
| 09 Research | GAP / STATE_UNVERIFIED |
| 10 Light workspace | UNVERIFIED / CURRENT_RENDER_UNAVAILABLE for same-state Light |
| 11 Local Memory/Knowledge | GAP / STATE_UNVERIFIED |

References opened: `11/11`. Exact rendered runtime surfaces opened: `11/11`. Same-state/reference-equivalent pairs: `0/11`. `MATCH_0_OF_11`. `PAIRS_VERIFIED_0_OF_11`.

## CI blocker corrected in candidate

Previous canonical Quality on `d71bf695…` ran full pytest successfully (`4854 passed, 3 skipped`) but mypy rejected `if shell is None: return` because the typed `PathenaMainWindow.centralWidget()` boundary is non-null after shell installation. The new Help-host helper instead queries the nullable `QFrame` workspace by object name, preserving a real fail-closed runtime boundary without an unreachable branch.

## Next visual slice

First consume exact candidate gates and exact Windows 11-surface render. If Help now visibly preserves shell chrome, compare its remaining information hierarchy against the Help reference; only after that bounded slice is stable consider ComfyUI, PALLAS or Command Palette.
