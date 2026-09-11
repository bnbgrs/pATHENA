# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11 21:39 CEST

Run-start Develop was checked first at `c670d7809c9f0aa5e6c31956b57e897091f1b9d6`; run-start worker was `ecbc661224917f1793b122a94e269ae88b450bc2`. Current Develop is one Core/Knowledge commit ahead of the UI merge base; that commit changes only the Integrator handoff plus Concept Note provenance/update source and focused tests. This candidate imports those exact Develop blobs history-preservingly without altering UI, Backend, Storage, Security, Runtime or release semantics.

Exact worker evidence consumed before this synchronization:

- canonical `ATHENA Quality Gate` run `34635102754` on `ecbc661224917f1793b122a94e269ae88b450bc2`: `SUCCESS`;
- `pATHENA UI Focused Candidate` run `34635102820`: `SUCCESS`;
- `pATHENA 11-Surface Visual Regression` run `34635099776`: capture/artifact produced for the exact worker SHA; final workflow result remains fail-closed red at the visual-baseline verdict;
- exact artifact `pathena-visual-ecbc661224917f1793b122a94e269ae88b450bc2` contains all eleven native Windows/PySide6 runtime PNGs.

All eleven canonical user references were enumerated from the reference folder and opened directly. All eleven exact runtime PNGs from the `ecbc661…` artifact were also opened directly. This proves capture coverage, not parity: slot 10 still has no same-state Light runtime render, and the populated/healthy reference states differ materially from several truthful unavailable/empty runtime states. `MATCH` therefore remains fail-closed.

The new Help full-MainWindow capture is the important BEFORE→AFTER evidence of this run. BEFORE, the harness photographed only the Help child surface and could not prove persistent shell chrome. AFTER at exact `ecbc661…`, `10-help.png` shows the real top bar, icon rail, workspace-bounded Help surface and right inspector simultaneously. The host-geometry correction is therefore visually verified. The Help composition itself remains a visible GAP: no Help secondary navigation, no search field, much flatter text hierarchy, and the right inspector still shows the prior `SETTINGS / LOCAL` context instead of Help-specific shortcuts/status.

| Slot | Reference | Current exact render | Checked branch + SHA | Status | Visible deviations / evidence limit | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED (`11-comfyui.png`) | `postmerge/ui@ecbc661…` | GAP | App-shell/navigation: absent in current standalone utility; workspace hierarchy: compact form only; inspector: no Connection column; composer/controls: real endpoint/workflow/activity controls but different grouping; typography/spacing/ratios: substantially smaller and denser; colors/borders: generic utility styling; states/interactions: real controls, no invented state; screen-specific: reference integrations subnav + workflow stepper missing. | After Help is closed, integrate real ComfyUI surface into shell without changing workflow semantics. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED (`08-pallas.png`) | same | GAP | App-shell/navigation absent; central graph is real but diagnostic/minimal; inspector/provenance/history absent; no composer; typography/spacing/ratios and border treatment diverge strongly; graph interaction/state remains real; minimap, focus/fit controls and screen-specific rich relation groups missing. | Separate PALLAS shell/framing slice after Help. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED (`07-settings.png`) | same | GAP / STATE_UNVERIFIED | Shell/navigation present; hierarchy much sparser; inspector exists but runtime/provider is unavailable rather than healthy; controls are real and fail-closed; typography/spacing/ratios differ; colors/borders broadly directionally aligned but flatter; reference secondary navigation and richer status composition remain incomplete. | Improve hierarchy only from real settings/runtime facts; do not fake healthy state. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED (`10-help.png`, full MainWindow) | same | GAP | Shell geometry: AFTER now visibly preserves topbar + rail + right inspector and bounds Help to workspace; navigation: primary rail retained but Help secondary navigation missing; workspace hierarchy: raw capability text instead of search + capability rows; inspector: incorrectly retains `SETTINGS / LOCAL` instead of Help-specific shortcuts/status; controls: F1/Esc/Ctrl-K paths remain real; typography/spacing/ratios: flat/monospaced relative to reference; colors/borders: understated generic text surface; state: live capability-derived catalogue; screen-specific: Quick shortcuts and “Help is current” absent. | Keep current host geometry; next bounded Help slice is live-data hierarchy plus contextual Help inspector, without inventing shortcuts/capabilities. |
| 05 Workspace / Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED (`01-chat.png`) | same | UNVERIFIED | Shell/navigation/composer real; current state is reconnecting/empty while reference is populated synthesis + graph + Evidence/Activity; inspector content therefore not same-state; typography/spacing/ratios/colors cannot support parity claim; interactions remain truthful. | Obtain a real populated grounded state before parity work/claims. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED (`04-jobs.png`) | same | GAP / STATE_UNVERIFIED | Shell/navigation present; workspace currently empty/error with raw startup diagnostics; inspector `JOB / NONE`; reference has active job timeline/log/resources; controls/states are truthful but non-equivalent; typography/spacing/ratios and hierarchy differ strongly. | Compare a real active job later; do not synthesize execution/resource values. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED (`09-command-palette.png`) | same | GAP / CONTEXT_UNVERIFIED | Current capture is the real standalone dialog; reference is an overlay over populated Knowledge shell; command controls/keyboard state are real; background shell context, dimensions, spacing and border/radius composition do not match. | Shell-overlay slice only after Help. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED (`06-system.png`) | same | GAP / STATE_UNVERIFIED | Full shell present; current runtime values are truthfully `Unavailable` and composition sparse; reference shows healthy runtime/storage/connectivity/background work plus Security posture; no healthy-state fabrication permitted; typography/spacing/hierarchy differ. | Recompare when real healthy state exists; preserve fail-closed semantics. |
| 09 Research | AVAILABLE_OPENED | AVAILABLE_OPENED (`03-research.png`) | same | GAP / STATE_UNVERIFIED | Shell/navigation present; current empty/failure state and raw startup traceback differ from populated Research Studio; Evidence/Activity and rich synthesis/graph absent in current state; controls are real; spacing/ratios/hierarchy diverge. | Shared workspace hierarchy only after shell surfaces, with real research data. |
| 10 Light workspace variant | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE (no same-state Light render) | same | UNVERIFIED | No real equivalent Light-theme runtime surface exists in this artifact; no comparison or inferred color/contrast/border parity is allowed. | Produce a real same-state Light render before any visual claim. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED (`02-knowledge.png`) | same | GAP / STATE_UNVERIFIED | Shell/navigation and Knowledge inspector identity are real; current Core-unavailable/empty state differs from populated synthesis/graph/Evidence/Activity reference; composer reconnecting; typography/spacing/ratios and hierarchy cannot be compared as same state. | Obtain populated canonical-memory state; then address shared workspace hierarchy. |

## Current verification accounting

- References opened this run: `11/11`.
- Exact runtime surfaces opened this run: `11/11` at `postmerge/ui@ecbc661224917f1793b122a94e269ae88b450bc2`.
- Same-state/reference-equivalent pairs: `0/11` under the strict rule.
- `MATCH_0_OF_11`.
- `PAIRS_VERIFIED_0_OF_11`.

## Highest-priority next visual slice

The recurring cross-screen gap remains `APP SHELL / SURFACE INTEGRATION`; the active bounded slice remains Help until it is compositionally coherent. Preserve the now-verified workspace-bounded Help geometry and seven-primary-page invariant. Next, replace the flat Help catalogue presentation with a live-capability-derived hierarchy closer to the reference and give Help an honest contextual inspector sourced only from real installed shortcuts/capability state. Do not start ComfyUI/PALLAS/Palette integration in the same candidate.
