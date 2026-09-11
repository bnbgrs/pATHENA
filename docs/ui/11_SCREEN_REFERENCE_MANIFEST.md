# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11

Current Develop checked first: `95b636c982a800d75f7d219162a04f6c87976e9f`. Exact canonical ATHENA Quality Gate `34560421777` completed `SUCCESS` on that SHA. This proves the preceding teardown-safe Qt lifecycle fix has reached Develop and is canonical-green.

Run-start worker HEAD: `103feb7ca6b3513077ce47f83569c13cc626b600`. Exact worker visual run `34559783835` exists for this SHA and uploaded artifact `pathena-visual-103feb7ca6b3513077ce47f83569c13cc626b600`; the workflow conclusion remains fail-closed because no approved committed visual baseline exists. In this run the artifact metadata was reachable but its binary PNG payload could not be materialized through the available GitHub connector/runtime. Therefore no current runtime pixels are claimed as opened this run.

All 11 user reference PNGs were independently opened directly again in this run. Source inspection also confirmed that the primary text top navigation still exists on the real desktop startup path: `install_navigation_context_accessibility(window)` installs `Chat`, `Knowledge`, `Research`, `Jobs`, `Sources` buttons into the real `topBar` and routes them through the existing `navigation.setCurrentRow(...)`; no second router is introduced. This is code/path evidence only, not screenshot parity.

Under the hard same-state rule, no previous screenshot pair is carried forward into this run. Every slot is therefore fail-closed as `CURRENT_RENDER_UNAVAILABLE` until exact current pixels can be opened again.

| Slot | Reference | Current exact render this run | Checked branch + SHA | Status | Evidence limit / visible reference requirement | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | `postmerge/ui@103feb7c…` | UNVERIFIED | Reference requires full shell integration, central workflow controls and Connection inspector. | Re-open exact runtime capture before any ComfyUI visual mutation. |
| 02 PALLAS | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires semantic field plus selected-object Knowledge/Provenance/History context. | Re-open exact runtime capture before mutation. |
| 03 Settings | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires full settings hierarchy and System status inspector. | Re-open exact runtime capture; then bind only real status. |
| 04 Help | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires Help workspace, contextual navigation and shortcut/status inspector. | Re-open exact runtime capture before mutation. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires large synthesis/reasoning workspace, Evidence/Activity inspector and large composer. | Obtain/open a real current populated state before geometry claims. |
| 06 Jobs | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires real running-job hierarchy with Execution/Resources context. | Open exact runtime state; never synthesize a job. |
| 07 Command Palette | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires palette over a real Knowledge workspace. | Capture/open palette in real context. |
| 08 System | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires runtime/storage/connectivity/background-work hierarchy and Security posture. | Re-open exact runtime state; preserve fail-closed health semantics. |
| 09 Dark research studio | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires populated synthesis/graph/Evidence composition. | Open a real current loaded Research state. |
| 10 Light workspace variant | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Product direction remains dark/orange; light palette is not authoritative. | Compare geometry only when a real equivalent state exists. |
| 11 Local-memory workspace | AVAILABLE_OPENED | CURRENT_RENDER_UNAVAILABLE | same | UNVERIFIED | Reference requires populated local-memory graph and Evidence/Activity. | Open a real populated current Knowledge state. |

## Current verification accounting

- References opened this run: `11/11`.
- Exact current candidate images opened this run: `0/11`.
- Exact artifact metadata available: `11-surface artifact exists for 103feb7c…`, bytes unavailable to this runtime.
- Valid same-state/reference-equivalent pairs: `0/11`.
- `MATCH`: `0/11`.
- `PAIRS_VERIFIED_0_OF_11`.

## Highest-priority next visual slice

Do not mutate another visual surface until the exact worker runtime PNGs can be opened again. Once pixels are available, re-evaluate the largest repeated gap using the actual current render. The prior evidence points to contextual inspector composition, but that priority is not promoted from historical screenshots without fresh current pixels.
