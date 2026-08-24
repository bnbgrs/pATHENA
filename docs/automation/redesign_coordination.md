# pATHENA Redesign Coordination

Last updated: 2026-08-25
Lead source: `agent/pathena`
Accepted source SHA: `fbbf44dc8c8175499528f07be079061b644d1604`
Candidate branch: `bot/pathena-candidate`
Candidate base SHA before this coordination commit: `fbbf44dc8c8175499528f07be079061b644d1604`

## Promotion policy

- `main`, ATHENA, and user branches are read-only.
- Global legacy Quality red is recorded but does not block redesign work.
- A targeted slice failure remains RED.
- Promotion from candidate to `agent/pathena` requires a GREEN Cloud-Windows report bound to the exact candidate SHA.
- No current candidate has that report; promotion is blocked.

## Exclusive ownership

| Owner branch | Exclusive product scope | Must not edit |
| --- | --- | --- |
| `bot/pathena-design-system` | design tokens, `pathena_theme.py`, shared shell/layout in `pathena_window.py`, shared components, focus/hover/disabled states, reduced motion | screen-specific controllers and workspace behavior |
| `bot/pathena-screens-core` | Chat, Knowledge, Research, PALLAS adapters/views/actions; use extension modules or workspace modules | `pathena_theme.py`, shared shell/layout, Jobs/Files/System/Settings/Help/ComfyUI |
| `bot/pathena-screens-ops` | Jobs, Files/Sources, System, Settings, Help, ComfyUI and command palette behavior/views | shared theme/shell and Chat/Knowledge/Research/PALLAS |
| `bot/pathena-cloud-windows` | Windows candidate workflow, process-tree harness, packaging entry points and packaging-specific runtime fixes | screen design and shared visual system |
| `bot/pathena-candidate` | Lead-only integration and `docs/automation/**` | direct feature development |

Ownership arbitration:

- `pathena_window.py` is Design-System-owned. Core/Ops request hooks through a handoff and prefer extension/workspace modules.
- The PALLAS container's shared geometry is Design-System-owned; its semantic adapter, renderer, simulation state and interactions are Core-owned.
- `app.py` integration edits require Lead arbitration because all workspaces install there. A worker must provide an exact minimal handoff instead of editing it concurrently.
- Cloud-Windows may edit packaging-only entry points but not the normal desktop interaction model.

## Eleven-screen matrix

| Reference image | Target area | Owner | Status | First acceptance slice |
| --- | --- | --- | --- | --- |
| ComfyUI-Integration im pATHENA Studio.png | ComfyUI | Operations | ASSIGNED | Real endpoint/workflow state; no simulated Ready/Run success |
| PALLAS – Lebendes semantisches Wissensfeld.png | PALLAS | Core | ASSIGNED | Deterministic real-data semantic adapter plus selectable nodes; no invented knowledge |
| pATHENA Einstellungen für lokale KI.png | Settings | Operations | ASSIGNED | Existing model/context/output/thinking values persist and expose honest provider/network state |
| pATHENA Hilfe: Fähigkeiten im Überblick.png | Help | Operations | ASSIGNED | Capability-derived help only; unavailable features remain explicit |
| pATHENA im eleganten Dunkelmodus.png | shared dark shell | Design System | ASSIGNED | Tokens, typography, rail, workspace and inspector foundation without signal/controller changes |
| pATHENA Jobs: Prüfung der Speicher-Richtlinie.png | Jobs | Operations | QUEUED | Real job selection, progress, pause/resume/cancel and logs |
| pATHENA Such- und Befehlspalette.png | universal search/palette | Operations | QUEUED | Existing actions, blockers and navigation remain truthful and keyboard-safe |
| pATHENA Systemübersicht für lokale KI.png | System | Operations | QUEUED | Real Core/provider/storage/network/runtime status and recovery links |
| pATHENA – Dunkles Studio für Wissensforschung.png | Research workspace | Core | QUEUED | Real research phases, evidence and proposal ownership |
| pATHENA: Intelligenzstudio für lokales Wissen.png | Chat/workspace shell | Core + Design handoff | QUEUED | Real chat/source/provenance flow in shared shell; no bubble rewrite |
| pATHENA: Lokales Gedächtnis neu gedacht.png | Knowledge/memory | Core | QUEUED | Real Knowledge/Claim/Decision selection, provenance and actions |

All eleven Library files were resolved and visually inspected in this Lead cycle.

## Current status

| Slice | Branch | Status | Evidence / blocker |
| --- | --- | --- | --- |
| Branch bootstrap | all four worker branches + candidate | READY | All created from exact SHA `fbbf44dc8c8175499528f07be079061b644d1604` |
| Design foundation | Design System | ASSIGNED | Await targeted tests and offscreen render |
| Core/PALLAS adapter | Core Screens | ASSIGNED | Await real-data adapter tests and render |
| Settings provider-state slice | Operations Screens | ASSIGNED | Await persistence/controller tests and render |
| Windows safety harness | Cloud Windows | ASSIGNED / P0 | Exact candidate has no full Windows acceptance report |
| Candidate promotion | Lead | BLOCKED | Requires exact-SHA Cloud-Windows GREEN |

## Windows status

Current candidate: **NOT_EXECUTABLE for promotion**.

No SHA-bound full desktop/packaging Windows report exists for the current candidate. Historical PR #9 run `32634986477` is not transferable: the runner reported shutdown/cancel during cleanup and its log terminated 608 orphan processes named `pATHENA`. A smoke step that only counted `pATHENA-Core` and `pATHENA-Scheduler` is insufficient.

Cloud-Windows acceptance must capture the complete descendant/product process tree, reject growth or recursion, verify zero product orphans after controlled exit, and withhold distributable artifacts on RED.

## Assigned next slices

### Design System — DS-001

- Files: `pathena_theme.py`; new design-token/component modules and focused tests. `pathena_window.py` only for shared shell geometry.
- Acceptance: #060606–#090909 foundations, warm white hierarchy, #F26A21 semantic accent, consistent focus/hover/disabled states, no glow/CRT/glass, reduced-motion path.
- Verification: focused unit tests plus a real offscreen 1480x900 shell render.
- Handoff: stable component and object-name contract for both screen bots.

### Core Screens — CORE-001

- Files: new PALLAS semantic adapter/view modules and tests; no shared theme/shell edits.
- Acceptance: stable IDs from real Sources/Claims/Knowledge/Research/Memory/Jobs; deterministic layout input; selection/focus/inspector contract; honest empty/error/loading states.
- Verification: adapter tests, deterministic render-state test, offscreen PALLAS slice render.
- Handoff: exact shared-container geometry/hook request to Design System or Lead if needed.

### Operations Screens — OPS-001

- Files: Settings/System extension modules and focused tests; no shared theme/shell edits.
- Acceptance: real model selection, context/output/thinking persistence and provider/network readiness; no invented status; unchanged backend contracts.
- Verification: persistence/controller tests and offscreen Settings render.
- Handoff: reusable field/status component requirements to Design System.

### Cloud Windows — WIN-001

- Files: Windows candidate workflow, process-tree harness, packaging-specific entry points and tests only.
- Acceptance: exact candidate SHA; native Windows; install/import/start; process-tree sampling; bounded descendants; zero orphans; controlled exit; database reopen; artifact only on GREEN.
- Verification: runner/job/log/artifact all bound to one SHA. RED/NOT_EXECUTABLE is never promoted.

## Next Lead integration step

Read worker handoffs next cycle, verify branch SHAs and exclusive file ownership, integrate at most the smallest coherent READY foundation/vertical slice into `bot/pathena-candidate`, then request a new exact-SHA Windows acceptance. Do not promote to `agent/pathena` before GREEN.
