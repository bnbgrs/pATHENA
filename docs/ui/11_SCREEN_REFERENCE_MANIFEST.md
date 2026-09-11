# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11

Current Develop checked first: `7a6b9ee59f059202f1f3b5c5b8f7b70e319bec2c`; exact canonical Quality `34544225707 = SUCCESS`.

Run-start worker head: `d55877cd353f7ee598df8213b9508fb143e51e15`. Last exact rendered product candidate remains `6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc`; native-Windows visual run `34533820471` produced all 11 canonical PySide6 captures with zero capture errors. All 11 of those BEFORE renders were opened again in this run.

All 11 user reference PNGs were independently opened again in this run. A new product/test candidate now exists at `1c298018b126c357a1c4f56ecbc07d629190964b`: it adds functional textual top navigation by reusing the existing navigation row model, plus focused interaction/accessibility coverage. No exact runtime capture exists yet for that new candidate. GitHub reports zero workflow runs for that exact SHA, and the local execution environment could not resolve `github.com`, so an AFTER render could not be produced without inventing evidence.

Therefore every slot is fail-closed for the new candidate: reference pixels are available, BEFORE pixels are available, but the current candidate rendering is `CURRENT_RENDER_UNAVAILABLE`. No `MATCH`, `CLOSE`, or visual-improvement claim is made for `1c298018…` until its real PySide6 renders are opened.

| Slot | Reference | BEFORE rendering | Current candidate | Checked branch + SHA | Status | Visible BEFORE gap / candidate intent | Concrete next correction |
|---|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED `11-comfyui.png` | CURRENT_RENDER_UNAVAILABLE | `postmerge/ui@1c298018…` | UNVERIFIED | Standalone utility versus full integration workspace; top-nav slice does not alter this standalone surface. | Render candidate; then keep real controller and address workspace framing separately. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED `08-pallas.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Standalone semantic graph versus reference shell + contextual inspector; top-nav slice does not alter standalone full view. | Render candidate; retain semantic data and handle shell integration separately. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED `07-settings.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | BEFORE lacks textual top navigation and uses generic inspector. Candidate exposes real primary routes, but reference-family labels differ for this Settings variant. | Render candidate before judging geometry; contextual Settings inspector remains separate. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED `10-help.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Standalone text-heavy Help versus full workspace; top-nav slice does not alter standalone Help. | Render candidate; later reuse real catalogue in shell composition. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED `01-chat.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | BEFORE reconnecting Chat lacks reference textual top nav and loaded synthesis/evidence state. | Render candidate; separately obtain a real loaded grounded-chat state. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED `04-jobs.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | BEFORE empty scheduler lacks textual top nav and active execution context. | Render candidate; later capture a real active job state. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED `09-command-palette.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Standalone capture instead of overlay-over-Knowledge reference context. | Render candidate and extend capture to palette-over-workspace before geometry tuning. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED `06-system.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | BEFORE same route lacks textual top nav; runtime state is disconnected versus healthy reference. | Render candidate; later recapture healthy runtime without fake state. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED `03-research.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | BEFORE empty Research lacks top nav and populated synthesis/graph composition. | Render candidate; later capture a real loaded research result. |
| 10 Light workspace variant | AVAILABLE_OPENED | AVAILABLE_OPENED analogous dark `01-chat.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | No same-state light runtime; dark/orange product direction remains authoritative. | Render candidate for geometry only; do not copy light palette. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED analogous `02-knowledge.png` | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | BEFORE empty Knowledge lacks textual top nav and populated memory/evidence composition. | Render candidate; later capture populated real Knowledge state. |

## Product slice this run

`VISUAL-GAP-0001` remains the selected P0. The bounded slice does not create a second router: `NavigationContextAccessibility` inserts `Chat`, `Knowledge`, `Research`, `Jobs`, and `Sources` buttons into the existing `topBar`; each button changes the existing `QListWidget#navigation` row, and the same existing row-change signal synchronizes checked and accessibility state. System and Settings remain existing utility controls. Backend, Storage and Security semantics are unchanged.

Product commit: `2a726ff2155d41d256e244bc05dbbd01c7dd9809`.
Focused-test commit/head: `1c298018b126c357a1c4f56ecbc07d629190964b`.

## Verification accounting

- References opened this run: `11/11`.
- Exact BEFORE worker renderings opened this run: `11/11` (`6b1777ef…`).
- Exact AFTER/current-candidate renderings opened: `0/11` (`CURRENT_RENDER_UNAVAILABLE`).
- Current-candidate `MATCH`: `0/11`.
- `PAIRS_VERIFIED_0_OF_11` for `1c298018…`.

The preceding `6b1777ef…` evidence remains historical BEFORE evidence only; its previous same-state/direct accounting must not be projected onto the new candidate.
