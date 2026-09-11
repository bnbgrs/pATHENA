# pATHENA 11-Screen Reference Manifest

Integration target: `develop/pathena-next` (READ-ONLY)
UI worker: `postmerge/ui`
Reference folder: `/pATHENA/Designreferenz – 11 Screenshots`

## Evidence state — 2026-09-11

Current Develop was checked first at run start: `e6ba3d7557bd46094ad4e8f067a238e1c2375f8e`; exact canonical ATHENA Quality Gate `34567856833` completed `SUCCESS` on that SHA. Run-start worker HEAD was `c51ef04787ef6affa2e6acc3a902e138cf6b7409`.

All 11 user reference PNGs were independently opened as images again. The previously blocked exact worker artifact for `103feb7ca6b3513077ce47f83569c13cc626b600` was also downloaded and all 11 native Windows/PySide6 runtime PNGs were opened. That fresh pixel review reproduced a repeated visual defect: Knowledge, Research, Jobs, Sources and Settings reused the Chat-oriented `CHAT / NONE` inspector even though the reference set requires route-specific context.

This run intentionally bounded the product change to two contexts only: Jobs and Settings. Candidate `069dff56d64cd78e2ddd255460db375f8eeb3041` exposed a real Qt capture failure (`QLabel` has no `textChanged` signal); no visual claim was made from that failed capture. Follow-up candidate `75029071aa63dbaa73ef42da16fb709cc6d8ca99` removed that invalid signal dependency while preserving the route-driven presentation. Exact visual run `34571930149` then completed immutable checkout, environment install, Ruff, mypy, comparator contract tests, all 11 native-font captures, comparison/proposal and artifact upload successfully. Only the final visual verdict failed because no approved committed baseline exists.

All 11 exact runtime PNGs from `75029071…` were downloaded and opened. Jobs now visibly presents `JOB / NONE`, `No job selected`, `EXECUTION` and `RESOURCES`; Settings visibly presents `SETTINGS / LOCAL`, `System status`, the actual captured core status and explicit no-synthetic-health-state copy. No job/resource/health values were fabricated. The product still has substantial reference gaps, so no MATCH is claimed.

| Slot | Reference | Current exact render | Checked branch + SHA | Status | Visible deviations / evidence limit | Concrete next correction |
|---|---|---|---|---|---|---|
| 01 ComfyUI | AVAILABLE_OPENED | AVAILABLE_OPENED (`11-comfyui.png`) | `postmerge/ui@75029071…` | GAP | Real utility is standalone; reference uses full shell, stronger workspace hierarchy and Connection inspector. | Preserve real ComfyUI path; address shell integration only after higher-repeat gaps. |
| 02 PALLAS | AVAILABLE_OPENED | AVAILABLE_OPENED (`08-pallas.png`) | same | GAP | Real semantic graph exists, but reference adds shell framing and selected Knowledge/Provenance/History context. | Revisit after shared inspector work. |
| 03 Settings | AVAILABLE_OPENED | AVAILABLE_OPENED (`07-settings.png`) | same | GAP / STATE_UNVERIFIED | BEFORE generic `CHAT / NONE`; AFTER now truthful `SETTINGS / LOCAL` + `System status`. Reference is a richer populated status composition. | Bind richer details only when real status data exists; no synthetic health. |
| 04 Help | AVAILABLE_OPENED | AVAILABLE_OPENED (`10-help.png`) | same | GAP | Real capability surface remains standalone and text-heavy versus full Help workspace reference. | Defer behind repeated shell/inspector gaps. |
| 05 Workspace/Evidence | AVAILABLE_OPENED | AVAILABLE_OPENED (`01-chat.png`) | same | UNVERIFIED | Current is real reconnecting/empty Chat; reference is populated grounded/synthesis state with inspector and richer composition. | Capture a real populated grounded state before parity claims. |
| 06 Jobs | AVAILABLE_OPENED | AVAILABLE_OPENED (`04-jobs.png`) | same | GAP / STATE_UNVERIFIED | BEFORE generic Chat inspector; AFTER now truthful Job empty-state context with Execution/Resources. Reference shows an actual running job and populated resource detail. | Connect selected-job data only through existing real job state. |
| 07 Command Palette | AVAILABLE_OPENED | AVAILABLE_OPENED (`09-command-palette.png`) | same | GAP / CONTEXT_UNVERIFIED | Real dialog remains standalone rather than overlay over the referenced Knowledge context. | Capture/compose real overlay context later. |
| 08 System | AVAILABLE_OPENED | AVAILABLE_OPENED (`06-system.png`) | same | GAP / STATE_UNVERIFIED | Route already has real Runtime/Backup and Security posture hierarchy; captured state is unavailable/disconnected rather than healthy reference state. | Preserve fail-closed semantics; compare a real healthy state when available. |
| 09 Dark research studio | AVAILABLE_OPENED | AVAILABLE_OPENED (`03-research.png`) | same | GAP / STATE_UNVERIFIED | Current route still exposes generic Chat inspector and failed/empty Research state; reference has research-specific synthesis/run context. | Next shared inspector candidate: truthful Research context from real selection/state. |
| 10 Light workspace variant | AVAILABLE_OPENED | NO SAME-STATE LIGHT RENDER | same | UNVERIFIED | Eleven runtime surfaces were opened, but none is a same-state light equivalent. Dark/orange product direction remains authoritative. | Geometry-only comparison when a real equivalent state exists. |
| 11 Local-memory workspace | AVAILABLE_OPENED | AVAILABLE_OPENED (`02-knowledge.png`) | same | GAP / STATE_UNVERIFIED | Current Knowledge still uses generic `CHAT / NONE`; reference requires selected Knowledge/Provenance/Evidence context and populated memory graph. | Next shared inspector candidate: truthful Knowledge context from real selection/state. |

## Current verification accounting

- References opened this run: `11/11`.
- Exact final-candidate native runtime surfaces opened this run: `11/11`.
- Final rendered product SHA: `75029071aa63dbaa73ef42da16fb709cc6d8ca99`.
- Same-state/reference-equivalent pairs: `0/11` under the strict rule; state/framing differences remain.
- `MATCH`: `0/11`.
- `PAIRS_VERIFIED_0_OF_11`.

## BEFORE -> AFTER for the bounded slice

- Jobs: generic `CHAT / NONE` inspector -> truthful `JOB / NONE` context with explicit `EXECUTION` and `RESOURCES` empty-state guidance.
- Settings: generic `CHAT / NONE` inspector -> truthful `SETTINGS / LOCAL` / `System status` context using the actually rendered core status and explicit no-synthetic-health-state wording.

## Highest-priority next visual slice

The repeated contextual-inspector gap remains the largest verified cross-screen defect, but Jobs and Settings are no longer the generic-Chat cases. Next, at most two tightly coupled contexts should be addressed: Knowledge and Research, using only real selections/controller state or explicit none/unavailable states. Do not touch System's already real Security posture semantics.
