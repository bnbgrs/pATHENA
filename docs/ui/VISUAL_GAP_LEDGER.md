# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current evidence — 2026-09-11 13:39 CEST

Develop: `85bd5f19c8aca56273ad43ac708fe13ac4798415`; exact canonical Quality `34591361659 = SUCCESS`. Exact rendered UI candidate: `199f123f893251b9fc6984e78c24f9ab5813cdc8`.

All 11 user reference images and all 11 exact Windows/PySide6 runtime images for `199f123f…` were opened directly. Sources now visibly shows the truthful `SOURCE / NONE` context; the prior `CHAT / NONE` mismatch is closed by current pixels. No same-state visual parity is claimed for any slot.

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN / HIGHEST PRIORITY`

Across the references the dominant composition is one integrated pATHENA shell: narrow rail, strong workspace hierarchy, contextual right column and consistent top navigation. Current Chat/Knowledge/Research/Jobs/System/Settings share that shell partially, while Help, ComfyUI and PALLAS remain visibly separate or much less integrated; the Command Palette is still presented as a standalone dialog rather than a shell overlay.

Next bounded correction: Help alone. Its content is real and already capability-driven, so host that existing content inside the current shell without inventing capability state or altering backend/storage/security semantics.

## VISUAL-GAP-0002 — contextual inspector

Category: `INSPECTOR / PAGE CONTEXT`
Severity: `P0/P1 visual`
Status: `REDUCED / ROUTE-CONTEXT SUBGAP CLOSED`

Exact current pixels at `199f123f…` show truthful route identity for Knowledge, Research, Jobs, Settings and Sources. System retains its own real Runtime/Backup/Security path. Remaining differences are primarily populated-vs-empty runtime state and richer reference composition, not the previous generic Chat inspector defect.

## VISUAL-GAP-0003 — standalone PALLAS / Help / ComfyUI / Palette framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

- Help: real capability content, wrong standalone host.
- ComfyUI: real local workflow controls, wrong standalone host and missing reference Connection framing.
- PALLAS: real graph, wrong standalone/minimal framing and missing rich contextual inspector.
- Command Palette: real commands, but standalone capture rather than overlay over the active workspace.

Prioritize Help first because it is presentation-only and lowest semantic risk. Do not combine Help and ComfyUI in one mutation.

## Slot accounting

| Slot | Status at exact `199f123f…` |
|---|---|
| 01 ComfyUI | GAP |
| 02 PALLAS | GAP |
| 03 Settings | GAP / STATE_UNVERIFIED |
| 04 Help | GAP |
| 05 Workspace/Evidence | UNVERIFIED |
| 06 Jobs | GAP / STATE_UNVERIFIED |
| 07 Command Palette | GAP / CONTEXT_UNVERIFIED |
| 08 System | GAP / STATE_UNVERIFIED |
| 09 Research | GAP / STATE_UNVERIFIED |
| 10 Light workspace | UNVERIFIED / no same-state render |
| 11 Local Memory/Knowledge | GAP / STATE_UNVERIFIED |

References opened: `11/11`. Exact current runtime surfaces opened: `11/11`. Same-state/reference-equivalent pairs: `0/11`. `MATCH_0_OF_11`. `PAIRS_VERIFIED_0_OF_11`.

## Readiness

Develop exact Quality is green, but the worker remains materially divergent from current Develop. No technical or visual READY claim is made. Exact visual run `34580743951` produced the 11 current surfaces and uploaded the exact-SHA artifact; its final baseline verdict remains fail-closed because no approved committed visual baseline exists.

## Next visual slice

Help shell integration only, followed by focused Qt/UI tests and a fresh exact-SHA 11-surface capture. Then open all eleven AFTER images and compare slot-by-slot before any ComfyUI or PALLAS mutation.
