# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current evidence — 2026-09-11 14:38 CEST

Develop: `dfa4a81b4c650339a16be5f60f87804e7cf6a68b`; exact canonical Quality `34596386099 = SUCCESS`. Worker before this evidence update: `8df01eef4d4c1b55f70e54f7fb99a542a9ebef33`. Exact rendered UI product head remains `199f123f893251b9fc6984e78c24f9ab5813cdc8`.

All 11 user reference images and all 11 exact Windows/PySide6 runtime images for `199f123f…` were opened directly again. Sources visibly retains the truthful `SOURCE / NONE` context; the prior `CHAT / NONE` mismatch remains closed. No same-state visual parity is claimed for any slot. Fresh source inspection confirms Help content is capability-derived but still hosted by a standalone `QDialog`.

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN / HIGHEST PRIORITY`

Across the references the dominant composition is one integrated pATHENA shell: narrow rail, strong workspace hierarchy, contextual right column and consistent top navigation. Current Chat/Knowledge/Research/Jobs/System/Settings share that shell partially, while Help, ComfyUI and PALLAS remain visibly separate or much less integrated; the Command Palette is still presented as a standalone dialog rather than a shell overlay.

Next bounded correction: Help alone, after the Develop/worker baseline is reconciled history-preservingly. Its content is real and already capability-driven, so host that existing content inside the current shell without inventing capability state or altering backend/storage/security semantics.

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
| 10 Light workspace | UNVERIFIED / CURRENT_RENDER_UNAVAILABLE for same-state Light |
| 11 Local Memory/Knowledge | GAP / STATE_UNVERIFIED |

References opened: `11/11`. Exact current runtime surfaces opened: `11/11`. Same-state/reference-equivalent pairs: `0/11`. `MATCH_0_OF_11`. `PAIRS_VERIFIED_0_OF_11`.

## Readiness

Develop exact Quality is green, but the worker is now 33 commits behind current Develop and 674 commits ahead from the merge-base. Several shell/render/workflow paths overlap on both sides, including the shell host, so no blind merge and no technical or visual READY claim is made. `command_palette.py` is identical on current Develop and worker, but Help integration still depends on a trustworthy shell-host baseline. Exact visual run `34580743951` produced the 11 current surfaces and uploaded the exact-SHA artifact; its final baseline verdict is not promoted to MATCH evidence.

## Next visual slice

History-preserving Develop compatibility first. Then Help shell integration only, followed by focused Qt/UI tests and a fresh exact-SHA 11-surface capture. Open all eleven AFTER images and compare slot-by-slot before any ComfyUI or PALLAS mutation.
