# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11

Current Develop checked first: `29540b7a1f2cb09e3a1be9aee2a29e357c8a8724`; canonical Quality `34534330414 = SUCCESS`. Current UI worker product head checked: `6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc`.

All 11 user reference PNGs were directly opened again in this run. The exact worker artifact `pathena-visual-6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc` from native-Windows visual run `34533820471` was downloaded and all 11 real PySide6 renderings were directly opened. Its manifest reports `candidate_sha=6b1777ef...`, `platform=win32`, 11 captures, zero capture errors, `status=PASS`. The workflow conclusion is red only because the generated visual baseline proposal is intentionally not an approved baseline.

No screenshot-level `MATCH` is claimed. Same-state/directly comparable pairs remain 3/11 (ComfyUI, PALLAS, Help); the other real current renders materially differ in data/context state or capture scope.

| Slot | Reference | Current rendering | Checked runtime | Status | Visible evidence | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED `11-comfyui.png` | `postmerge/ui@6b1777ef…` | GAP | Real queued loopback ComfyUI path exists, but current is a 760×560 standalone utility; reference is a full pATHENA integration workspace with shell, form hierarchy, process strip and Connection inspector. | Preserve real controller; integrate presentation into normal workspace framing. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED `08-pallas.png` | same | GAP | Real semantic graph exists but remains standalone and sparse versus reference shell + graph workspace + contextual knowledge/provenance/history inspector. | Integrate renderer into product shell without replacing semantic data. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED `07-settings.png` | same | GAP | Same Settings route. Typography is stronger than prior candidate, but current still lacks the reference-family textual top navigation and retains generic `Evidence & Activity / CHAT / NONE`; reference has Settings top-nav state and System-status context. | Add real primary textual top navigation first; contextual Settings inspector remains subsequent gap. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED `10-help.png` | same | GAP | Same real capabilities catalogue, but current is an 820×680 text-heavy standalone window; reference is a full Help workspace with secondary navigation, search, scannable rows and shortcuts/status context. | Reuse real catalogue in full workspace composition. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED `01-chat.png` | same | GAP / STATE_UNVERIFIED | Current is reconnecting empty Chat state. Shell proportions and enlarged title are visible, but textual top navigation and loaded synthesis/evidence composition are absent. | Add real top navigation; separately obtain loaded grounded-chat capture before state-level parity. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED `04-jobs.png` | same | GAP / STATE_UNVERIFIED | Current is real empty scheduler state; reference is active step 4/6 with job list, execution inspector, stepper and live log. Shell still lacks textual top nav and inspector is generic. | Add real top navigation; later capture a real active job state. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED `09-command-palette.png` | same | GAP / CONTEXT_UNVERIFIED | Functional command list and keyboard path exist, but capture remains standalone rather than overlaying Knowledge as in reference. | Extend real harness capture to palette-over-workspace before tuning overlay geometry. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED `06-system.png` | same | GAP / STATE_UNVERIFIED | Same System route but current state is unavailable/disconnected. Independent visual gap: no textual top nav; status hierarchy remains substantially lighter than reference. | Add real top navigation; later recapture healthy runtime without fake state. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED `03-research.png` | same | GAP / STATE_UNVERIFIED | Real empty Research state; reference is loaded synthesis/reasoning/graph composition. Current shell lacks textual top nav and uses generic inspector. | Add real top navigation; obtain loaded result for state-level comparison. |
| 10 Light workspace variant | AVAILABLE_OPENED | AVAILABLE_OPENED `01-chat.png` as analogous dark workspace | same | UNVERIFIED | No same-state light render; user direction remains dark/orange. Geometry only is usable evidence. | Keep dark theme; no palette copy. Obtain equivalent loaded workspace state before parity claim. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED `02-knowledge.png` as analogous Knowledge surface | same | GAP / STATE_UNVERIFIED | Real current Knowledge is empty/unavailable versus populated local-memory synthesis+graph+Evidence/Activity reference. Shared top textual navigation is absent. | Add real top navigation; later capture populated real Knowledge state. |

## Cross-screen finding

The largest evidence-backed repeated correction is now narrower than the prior broad shell label: the normal workspace shell already has the slim icon rail, large title tokens and bounded right inspector, but its top bar contains only the wordmark, two utility icons and `Local · Private`. The reference family repeatedly uses textual primary navigation across the top. The existing real routes are Chat, Knowledge, Research, Jobs and Sources; the next product slice should expose those same routes as functional top-bar controls, synchronized with the existing navigation model. No fake data or new product capability is needed.

## Verification accounting

- References opened: `11/11`.
- Exact current worker renderings opened: `11/11`.
- Same-state/direct pairs: `3/11`.
- `MATCH`: `0/11`.
- `PAIRS_VERIFIED_3_OF_11`.
