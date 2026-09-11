# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11 18:41 CEST

Run-start Develop was checked first at `fec368f50307a9e24038baca3a80b10ee2a3c4fc`; run-start worker was `f94a6d1edaddd2c4fc009f60134fd1bce6440500`. The exact Quality Gate for `f94a6d1…` completed `SUCCESS`. `main` and `bnbgrs/ATHENA` were not mutated.

All eleven canonical user references were enumerated from the Library folder and opened directly. The Help-host correction candidate `b6aaaac887535bfcafa7e5784d0dc0b590758f36` then completed Windows/PySide6 capture of exactly eleven canonical runtime surfaces. Artifact `pathena-visual-b6aaaac887535bfcafa7e5784d0dc0b590758f36` is exact-SHA bound; all eleven runtime PNGs were downloaded and opened directly.

The previous `7 navigation items / 8 pages` regression is fixed in this candidate: the visual harness primary-navigation contract passes and full 11-surface capture succeeds. Help is now a transient child of the real shell instead of an eighth primary page. The opened AFTER Help image still covers the shell chrome rather than matching the reference three-zone Help composition, so Help remains `GAP`, not `CLOSE` or `MATCH`.

| Slot | Reference | Current exact render | Checked branch + SHA | Status | Visible deviations / evidence limit | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED (`11-comfyui.png`) | `postmerge/ui@b6aaaac…` | GAP | Real local workflow controls remain a standalone utility; reference uses full pATHENA shell, integrations navigation and Connection inspector. | Separate ComfyUI shell-integration slice after Help. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED (`08-pallas.png`) | same | GAP | Real diagnostic graph remains standalone/minimal versus reference shell, controls, minimap and Knowledge/Provenance/History inspector. | Separate PALLAS surface-integration slice. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED (`07-settings.png`) | same | GAP / STATE_UNVERIFIED | Shell and truthful `SETTINGS / LOCAL` context exist; runtime is reconnecting/unavailable and hierarchy is much sparser than populated reference. | Improve hierarchy only with real runtime state. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED (`10-help.png`) | same | GAP | 7-page invariant is restored and Help is shell-owned, but current transient surface visually covers the topbar/rail/inspector. Reference keeps persistent shell chrome, Help sub-navigation, central capability cards and right shortcuts/status. | Re-host Help inside the shell workspace body while retaining 7 primary pages, F1/Esc/focus/accessibility and live catalogue content. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED (`01-chat.png`) | same | UNVERIFIED | Current real state is reconnecting/empty versus populated synthesis/graph/evidence reference. | Obtain real populated grounded state before parity claims. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED (`04-jobs.png`) | same | GAP / STATE_UNVERIFIED | Truthful `JOB / NONE` context; reference shows a running job, timeline, log and resources. | Compare a real active job state later. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED (`09-command-palette.png`) | same | GAP / CONTEXT_UNVERIFIED | Real command dialog still captured standalone rather than overlaying the active Knowledge shell. | Shell-overlay slice after Help. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED (`06-system.png`) | same | GAP / STATE_UNVERIFIED | Real fail-closed unavailable state versus healthy/populated reference; hierarchy remains sparser. | Preserve fail-closed semantics; compare healthy state only when real. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED (`03-research.png`) | same | GAP / STATE_UNVERIFIED | Truthful `RESEARCH / NONE` inspector but empty state is far simpler than synthesis/graph/evidence reference. | Shared workspace hierarchy after shell work. |
| 10 Light workspace variant | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE (no same-state Light render) | same | UNVERIFIED | Harness has no real equivalent Light-theme state for this reference. | Compare only when a real equivalent Light state exists. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED (`02-knowledge.png`) | same | GAP / STATE_UNVERIFIED | Truthful `KNOWLEDGE / NONE` context; reference is populated synthesis/reasoning/evidence. | Shared workspace hierarchy after shell work. |

## Current verification accounting

- References opened this run: `11/11`.
- Exact current runtime surfaces opened this run: `11/11` at `b6aaaac887535bfcafa7e5784d0dc0b590758f36`.
- Native capture contract: `11/11 SUCCESS`; route identity: `SUCCESS`.
- Same-state/reference-equivalent pairs: `0/11` under the strict rule.
- `MATCH_0_OF_11`.
- `PAIRS_VERIFIED_0_OF_11`.

## Branch / readiness note

Run-start Develop is one CI-only commit ahead of the worker merge-base. Product candidate `b6aaaac…` therefore is not declared Integrator-ready even though the bounded Help host invariant now passes the exact Windows visual harness. Its full visual workflow concludes failure only at the fail-closed baseline verdict after successful 11-surface capture/artifact upload. A focused Help unit-test contract is updated in the same documentation/test follow-up candidate; no focused PASS is claimed until that exact candidate runs.

## Highest-priority next visual slice

Keep `APP SHELL / SURFACE INTEGRATION` as the dominant gap, but stay on Help only. The next correction is narrower: preserve the now-fixed seven-primary-page invariant while positioning Help inside the central workspace region so topbar, rail and appropriate shell context remain visible. Do not start ComfyUI or PALLAS until the corrected Help AFTER image is inspected.
