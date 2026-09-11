# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11

Current Develop checked first: `1b83466490291fe07dd3d99dd476d0cb6290d307`; exact ATHENA Quality Gate `34548505498 = SUCCESS`.

Run-start worker head: `ac3d3c851186b8caa152d4a22815bd1390998e55`. The bounded top-navigation product commit remains `2a726ff2155d41d256e244bc05dbbd01c7dd9809`; later worker commits add focused coverage and evidence documentation without changing that product file.

All 11 user reference PNGs were opened directly again in this run. An exact native-Windows PySide6 visual artifact for product commit `2a726ff…` was discovered and downloaded from run `34547920919`; its eleven PNGs were all opened directly. The run successfully checked out the exact SHA, captured all eleven surfaces, generated/uploaded the artifact, and failed only at the final fail-closed visual verdict because no approved baseline exists.

The artifact itself exposed a capture-identity defect. Its `manifest.json` records `03-research.png` first with `row=2/page_index=2`, then `02-knowledge.png` with `row=1/page_index=2`, and `01-chat.png` with `row=0/page_index=2`. Therefore the files labelled Chat and Knowledge actually captured the Research page. They are real runtime pixels but are not valid same-state Chat/Knowledge evidence. The renderer currently schedules all seven workspace captures independently and calls `app.processEvents()` inside each capture without asserting that `pages.currentIndex()` still equals the requested row, so overlapping/re-entrant timer processing can produce mislabeled captures.

The top-navigation slice is visibly present on the normal shell renderings, so its existence is pixel-confirmed. Route-by-route visual parity is not confirmed because the harness miscaptured two primary routes and the remaining reference states are not state-equivalent.

| Slot | Reference | Current exact render | Checked branch + SHA | Status | Visible deviation / evidence limit | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED `11-comfyui.png` | `postmerge/ui@2a726ff…` | GAP | Real local ComfyUI dialog is compact/standalone; reference is a full integration workspace with shell and connection inspector. | Preserve real controller; later integrate framing without fake state. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED `08-pallas.png` | same | GAP | Real full PALLAS renderer is standalone diagnostic graph; reference includes shell, graph hierarchy and contextual knowledge/provenance inspector. | Keep real semantic data; address shell/context framing after capture repair. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED `07-settings.png` | same | GAP | Real Settings route exists, but hierarchy/inspector/state differ materially from reference. | Re-evaluate after reliable serialized shell capture; then contextual Settings inspector. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED `10-help.png` | same | GAP | Real Help is standalone capability dialog; reference is full Help workspace with navigation and shortcuts inspector. | Reuse real capability catalogue in shell composition; no decorative mock. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | `01-chat.png` OPENED BUT INVALID ROUTE IDENTITY (`page_index=2`) | same | UNVERIFIED | File labelled Chat actually captured Research; no valid current Chat pixel exists in this artifact. | Serialize workspace capture and assert selected row/page before saving; recapture. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED `04-jobs.png` (`row=3/page_index=3`) | same | GAP / STATE_UNVERIFIED | Real Jobs route is empty/recovery state versus active execution reference. | Capture a real active job state after harness repair; do not fabricate data. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED `09-command-palette.png` | same | GAP / CONTEXT_UNVERIFIED | Real palette is captured standalone rather than as an overlay over Knowledge. | Capture palette over the real workspace context. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED `06-system.png` (`row=5/page_index=5`) | same | GAP / STATE_UNVERIFIED | Real System route is disconnected/limited versus healthy populated reference; inspector hierarchy differs. | Recapture a real healthy state when available; retain fail-closed semantics. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED `03-research.png` (`row=2/page_index=2`) | same | GAP / STATE_UNVERIFIED | Correct route identity, but current state is sparse versus populated synthesis/graph/evidence reference. | Obtain a real loaded Research state after harness repair. |
| 10 Light workspace variant | AVAILABLE_OPENED | no same-state light current render | same | UNVERIFIED | Dark/orange product direction remains authoritative; no same-state light pair. | Compare geometry only when an equivalent real state exists; do not copy light palette. |
| 11 Local-memory workspace | AVAILABLE_OPENED | `02-knowledge.png` OPENED BUT INVALID ROUTE IDENTITY (`page_index=2`) | same | UNVERIFIED | File labelled Knowledge actually captured Research; no valid current Knowledge pixel exists in this artifact. | Serialize capture and assert route/page identity; recapture Knowledge. |

## Current verification accounting

- References opened this run: `11/11`.
- Exact current product artifact images opened: `11/11` (`2a726ff…`).
- Valid same-state/reference-equivalent pairs: `0/11` under the hard same-state rule.
- `MATCH`: `0/11`.
- `PAIRS_VERIFIED_0_OF_11`.

## Highest-priority next visual slice

Do not make another visual product mutation yet. First repair the visual harness so workspace captures are serialized and each saved workspace image fails closed unless both `navigation.currentRow()` and `pages.currentIndex()` equal the requested row. Then obtain an exact-SHA Windows artifact and reopen all eleven images. Only after valid Chat/Knowledge pixels exist should the next product gap be selected; based on the currently valid renders, the contextual page-specific inspector remains the leading product candidate.
