# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11 13:39 CEST

Run-start Develop was checked first at `85bd5f19c8aca56273ad43ac708fe13ac4798415`; exact canonical Quality run `34591361659` completed `SUCCESS`. Run-start worker HEAD was `199f123f893251b9fc6984e78c24f9ab5813cdc8`. `main` and `bnbgrs/ATHENA` were not mutated.

All eleven user reference images were enumerated from the canonical Library folder and all eleven were opened directly. The exact Windows/PySide6 artifact `pathena-visual-199f123f893251b9fc6984e78c24f9ab5813cdc8` from run `34580743951` was downloaded and all eleven current runtime PNGs were opened directly. Artifact metadata binds it to exact worker SHA `199f123f893251b9fc6984e78c24f9ab5813cdc8`.

The Sources correction is now visually verified: current `05-files.png` shows `SOURCE / NONE`, `No source selected`, `DETAILS`, and `PROVENANCE`; the previous misleading Chat inspector is gone. The visual run's final conclusion remains fail-closed because no approved committed visual baseline exists; that is not treated as a product-render failure.

| Slot | Reference | Current exact render | Checked branch + SHA | Status | Visible deviations / evidence limit | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED (`11-comfyui.png`) | `postmerge/ui@199f123f…` | GAP | Real ComfyUI controls exist, but the surface remains standalone and lacks the reference shell, integrations navigation and Connection inspector. | Shared shell integration; do not change ComfyUI backend semantics. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED (`08-pallas.png`) | same | GAP | Real graph exists, but current framing is standalone/minimal versus full shell, controls and rich Knowledge/Provenance/History inspector. | Shared surface integration after Help. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED (`07-settings.png`) | same | GAP / STATE_UNVERIFIED | Route-specific `SETTINGS / LOCAL` inspector is present; current runtime is reconnecting/unavailable while reference is populated/healthy. | Bind richer status only from real runtime data. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED (`10-help.png`) | same | GAP | Real capability content is present, but still rendered as a standalone dialog rather than the reference Help workspace inside the shell. | Highest-priority bounded shell slice: host Help in existing shell while preserving F1/Ctrl-K/accessibility. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED (`01-chat.png`) | same | UNVERIFIED | Current Chat is reconnecting/empty; reference is populated synthesis/graph/evidence with larger composer. | Obtain real populated grounded state before parity claims. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED (`04-jobs.png`) | same | GAP / STATE_UNVERIFIED | Correct Job no-selection context exists; reference shows running job, steps, log and resources. | Connect selected-job state only from real job data. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED (`09-command-palette.png`) | same | GAP / CONTEXT_UNVERIFIED | Palette is a real command surface but is captured standalone; reference is an overlay over populated Knowledge. | Integrate overlay through existing shell path after Help. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED (`06-system.png`) | same | GAP / STATE_UNVERIFIED | Real fail-closed Runtime/Backup/Security posture exists; captured state is unavailable versus healthy reference. | Preserve fail-closed semantics and compare a real healthy state later. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED (`03-research.png`) | same | GAP / STATE_UNVERIFIED | Truthful `RESEARCH / NONE` inspector exists; current failed/empty state is far simpler than reference synthesis/graph/evidence composition. | Shared workspace hierarchy after shell integration. |
| 10 Light workspace variant | AVAILABLE_OPENED | NO SAME-STATE LIGHT RENDER | same | UNVERIFIED | No real same-state Light rendering exists. | Compare only when a real equivalent is available. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED (`02-knowledge.png`) | same | GAP / STATE_UNVERIFIED | Truthful `KNOWLEDGE / NONE` inspector exists; reference is populated synthesis/reasoning/evidence. | Shared workspace hierarchy after shell integration. |

## Current verification accounting

- References opened this run: `11/11`.
- Exact current runtime surfaces opened this run: `11/11` at `199f123f893251b9fc6984e78c24f9ab5813cdc8`.
- Sources BEFORE -> AFTER route-context defect: visually verified fixed.
- Same-state/reference-equivalent pairs: `0/11` under the strict rule.
- `MATCH_0_OF_11`.
- `PAIRS_VERIFIED_0_OF_11`.

## Branch / readiness note

Current Develop and UI worker are materially divergent (`postmerge/ui` is 32 commits behind Develop and 673 commits ahead from the current merge-base view). No Integrator-ready claim is made. The next product mutation should not broaden this divergence unnecessarily.

## Highest-priority next visual slice

The repeated generic-Chat route-context defect is now visually reduced across Knowledge, Research, Jobs, Sources and Settings. Fresh 11-screen pixels make `APP SHELL / SURFACE INTEGRATION` the dominant remaining structural gap. The safest next bounded product slice is Help alone: preserve its real capability content and keyboard paths while hosting it inside the existing pATHENA shell. ComfyUI and PALLAS remain separate later slices.
