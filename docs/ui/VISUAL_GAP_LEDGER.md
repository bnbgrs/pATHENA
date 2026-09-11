# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
UI worker: `postmerge/ui`

## Current evidence — 2026-09-11 18:41 CEST

Run-start Develop: `fec368f50307a9e24038baca3a80b10ee2a3c4fc`; run-start worker: `f94a6d1edaddd2c4fc009f60134fd1bce6440500`. Exact Quality for `f94a6d1…` is `SUCCESS`. Product correction `b6aaaac887535bfcafa7e5784d0dc0b590758f36` preserves the seven primary pages and hosts Help as a transient shell child.

All 11 references and all 11 exact Windows/PySide6 runtime images for `b6aaaac…` were opened directly. Visual run `34623205385` passed immutable checkout, Ruff, mypy, comparator contracts, hierarchy tokens, primary-navigation accessibility, exactly-eleven capture, route identity, comparison/proposal and artifact upload; only the final fail-closed visual baseline verdict failed.

## VISUAL-GAP-0001 — shared shell / workspace hierarchy

Category: `APP SHELL / GEOMETRY / HIERARCHY`
Severity: `P0 visual`
Status: `OPEN / HIGHEST PRIORITY`

The references consistently use one integrated shell: persistent topbar, narrow rail, central workspace and contextual right column. Normal workspaces partially follow this. Help is now technically shell-owned without altering the seven primary routes, but its current overlay fills the entire shell rectangle and therefore hides the chrome that should remain visible. ComfyUI and PALLAS remain standalone/minimal; Command Palette remains visually standalone.

Next bounded correction: Help only. Host it inside the central workspace region rather than over the full shell while preserving the fixed `7 nav == 7 primary pages` invariant.

## VISUAL-GAP-0002 — contextual inspector

Category: `INSPECTOR / PAGE CONTEXT`
Severity: `P0/P1 visual`
Status: `REDUCED / ROUTE-CONTEXT SUBGAP CLOSED`

Exact `b6aaaac…` pixels retain truthful contexts for Knowledge, Research, Jobs, Settings and Sources. System remains fail-closed and runtime-derived. Remaining deviations are primarily empty-vs-populated state and richer reference composition.

## VISUAL-GAP-0003 — standalone/shell-host framing

Category: `SURFACE INTEGRATION`
Severity: `P1 visual`
Status: `OPEN`

- Help: **structural invariant improved** — no longer an eighth primary page; full 11-surface capture succeeds. Visual framing still wrong because the transient Help surface covers shell chrome.
- ComfyUI: real local workflow controls, wrong standalone host and missing reference Connection framing.
- PALLAS: real graph, wrong standalone/minimal framing and missing rich contextual inspector.
- Command Palette: real commands, but standalone capture rather than overlay over active workspace.

Do not combine these. Finish Help first.

## Slot accounting

| Slot | Status at exact `b6aaaac…` |
|---|---|
| 01 ComfyUI | GAP |
| 02 PALLAS | GAP |
| 03 Settings | GAP / STATE_UNVERIFIED |
| 04 Help | GAP — 7-page invariant fixed; shell chrome still obscured |
| 05 Workspace/Evidence | UNVERIFIED |
| 06 Jobs | GAP / STATE_UNVERIFIED |
| 07 Command Palette | GAP / CONTEXT_UNVERIFIED |
| 08 System | GAP / STATE_UNVERIFIED |
| 09 Research | GAP / STATE_UNVERIFIED |
| 10 Light workspace | UNVERIFIED / CURRENT_RENDER_UNAVAILABLE for same-state Light |
| 11 Local Memory/Knowledge | GAP / STATE_UNVERIFIED |

References opened: `11/11`. Exact current runtime surfaces opened: `11/11`. Same-state/reference-equivalent pairs: `0/11`. `MATCH_0_OF_11`. `PAIRS_VERIFIED_0_OF_11`.

## Readiness

The bounded product correction has exact Windows visual evidence that the former `7 nav / 8 pages` capture failure is removed. `b6aaaac…` captured all eleven surfaces successfully; workflow failure is only the final fail-closed baseline verdict. Run-start Develop remains one CI-only commit ahead from the worker merge-base, so no Integrator-ready claim is made. The Help-focused unit test is updated alongside this ledger but must receive exact candidate evidence before a PASS claim.

## Next visual slice

Help only: keep seven primary pages, retain real capability-derived data and keyboard/accessibility behavior, but constrain the Help transient surface to the shell workspace body so persistent shell chrome remains visible. Re-run focused Qt/UI tests and an exact-SHA 11-surface Windows capture, then open all eleven AFTER images before considering ComfyUI or PALLAS.
