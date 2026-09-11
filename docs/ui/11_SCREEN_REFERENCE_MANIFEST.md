# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11 19:40 CEST

Run-start Develop was checked first at `fec368f50307a9e24038baca3a80b10ee2a3c4fc`; run-start worker was `d71bf6951c10920eb709dbe5bb3e708c72b43c6a`. The exact UI Focused Candidate for that worker is `SUCCESS`; canonical Quality completed `FAILURE` solely because mypy reported one UI-owned unreachable statement in `src/athena/desktop/pathena_capability_help.py`. The same canonical run completed Ruff, specification validation, full pytest (`4854 passed, 3 skipped`) and the platform/storage smoke lanes successfully. `main` and `bnbgrs/ATHENA` remain untouched.

All eleven canonical user references were enumerated from the Library folder and opened directly again. The exact Windows/PySide6 artifact for the last rendered product SHA `b6aaaac887535bfcafa7e5784d0dc0b590758f36` was downloaded again and all eleven runtime PNGs were opened directly. This run therefore confirms the same strict pre-mutation visual baseline: Help is shell-owned but covers the entire shell rectangle; the next bounded correction is to host it in the real central `conversation` workspace frame instead.

This candidate also synchronizes the one Develop-only UI CI commit history-preservingly and applies the bounded Help-host correction plus focused test in the same candidate. A new exact current render is not claimed until CI produces it.

| Slot | Reference | Current exact render | Checked branch + SHA | Status | Visible deviations / evidence limit | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED (`11-comfyui.png`) | rendered `postmerge/ui@b6aaaac…` | GAP | Real local workflow controls remain standalone; reference uses persistent shell, integrations navigation and Connection inspector. | Separate ComfyUI shell-integration slice after Help. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED (`08-pallas.png`) | same | GAP | Real diagnostic graph remains standalone/minimal versus reference shell, controls, minimap and Knowledge/Provenance/History inspector. | Separate PALLAS surface-integration slice. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED (`07-settings.png`) | same | GAP / STATE_UNVERIFIED | Shell and truthful Settings context exist; runtime is reconnecting/unavailable and hierarchy is much sparser than populated reference. | Improve hierarchy only with real runtime state. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED (`10-help.png`) | same | GAP | Real capability content exists and 7-page invariant is fixed, but rendered Help obscures topbar/rail/inspector. Reference preserves all shell chrome with Help navigation, central content and shortcuts/status. | This candidate reparents Help to the real central workspace body; exact AFTER render required before status can improve. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED (`01-chat.png`) | same | UNVERIFIED | Current real state is reconnecting/empty versus populated synthesis/graph/evidence reference. | Obtain real populated grounded state before parity claims. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED (`04-jobs.png`) | same | GAP / STATE_UNVERIFIED | Truthful no-selection context; reference shows a running job, timeline, log and resources. | Compare a real active job state later. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED (`09-command-palette.png`) | same | GAP / CONTEXT_UNVERIFIED | Real command dialog is captured standalone rather than overlaying the active Knowledge shell. | Shell-overlay slice after Help. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED (`06-system.png`) | same | GAP / STATE_UNVERIFIED | Real fail-closed unavailable state versus healthy/populated reference. | Preserve fail-closed semantics; compare healthy state only when real. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED (`03-research.png`) | same | GAP / STATE_UNVERIFIED | Truthful Research context but empty state is far simpler than synthesis/graph/evidence reference. | Shared workspace hierarchy after shell work. |
| 10 Light workspace variant | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE (no same-state Light render) | same | UNVERIFIED | Harness has no real equivalent Light-theme state for this reference. | Compare only when a real equivalent Light state exists. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED (`02-knowledge.png`) | same | GAP / STATE_UNVERIFIED | Truthful Knowledge context; reference is populated synthesis/reasoning/evidence. | Shared workspace hierarchy after shell work. |

## Current verification accounting

- References opened this run: `11/11`.
- Exact runtime surfaces opened this run: `11/11` at rendered product SHA `b6aaaac887535bfcafa7e5784d0dc0b590758f36`.
- Same-state/reference-equivalent pairs: `0/11` under the strict rule.
- `MATCH_0_OF_11`.
- `PAIRS_VERIFIED_0_OF_11`.

## Current bounded mutation

Help remains the only product slice. The correction uses the existing real `conversation` frame as transient Help parent so the topbar, icon rail and contextual inspector remain sibling shell chrome. It does not add a primary page, route or backend state. The focused test asserts `7 nav == 7 primary pages`, unchanged route, workspace-body ownership, workspace-bounded geometry and visible topbar/rail/inspector while Help is open. It also removes the exact mypy-unreachable `centralWidget() is None` branch that failed the previous canonical gate.

## Highest-priority next visual slice

Consume exact focused/canonical/visual evidence for this candidate first. If the Help AFTER image proves persistent shell chrome and no regression in the other ten slots, then finish any remaining Help composition gap before moving to ComfyUI or PALLAS.
