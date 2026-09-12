# pATHENA Visual Gap Ledger

Current Develop inspected: `develop/pathena-next@4dbefe2167b28bffab2c6b69b7a8df4b43770a6f`.
Current exact BEFORE render: `postmerge/ui@dce6d463b17474ec2da702a14b7a4365123df45d`.

All eleven original user references and all eleven real native BEFORE runtime PNGs were opened in the current UI run. Strict same-state evidence remains `PAIRS_VERIFIED_1_OF_11`, `MATCH_0_OF_11`; technical PNG existence is not treated as a same-state pair.

## Highest recurring open visual gap — detached product surfaces break the app shell

- Category: `APP_SHELL / GEOMETRY`
- Severity: `P0 VISUAL`
- Affected opened references: PALLAS, ComfyUI, Command Palette; the same shared-shell geometry also frames Help, Settings, Jobs, System, Research and Workspace references.
- Evidence: exact BEFORE `08-pallas.png` is the real PALLAS renderer in a detached window with no pATHENA top bar, narrow primary rail or shared right inspector. Exact BEFORE `11-comfyui.png` is likewise a detached local-tool dialog. Exact BEFORE `09-command-palette.png` is captured without its workspace context.
- Reference evidence: the opened PALLAS reference requires one app composition with top navigation, narrow rail, central semantic field and a right Knowledge/Provenance/Connections/History context. The opened ComfyUI reference uses the same app shell with integrations navigation and a Connection inspector. The opened palette reference is an overlay over Knowledge, not a standalone product window.
- Prioritization: PALLAS first because a real `PallasWorkspace` and real shared PALLAS inspector already exist, so this structural correction does not require synthetic product semantics.

### Current candidate — PALLAS shell host

Status: `CANDIDATE_PENDING_EXACT_AFTER`.

Product change in this commit:

- removes the full PALLAS `QDialog` host;
- reuses the real synchronized `PallasWorkspace` inside the existing `referenceBody`;
- inserts it between the real icon rail and the real shared inspector;
- temporarily hides only the normal routed `conversation` center while PALLAS is open;
- restores the routed center when any of the existing seven primary navigation items is selected;
- keeps `navigation.count() == 7` and `pages.count() == 7`;
- keeps real renderer selection and shared Inspector behavior;
- adds no eighth route, no mock graph, no synthetic provenance and no Backend/Storage/Security behavior.

Focused contract change in this commit requires one reused shell-hosted PALLAS workspace, route restoration, double-click opening and continued shared-inspector selection propagation. The native visual harness now fails if PALLAS is detached and captures the real main window with PALLAS hosted in-shell.

Acceptance for visual closure: exact candidate Screen 02 must be opened after native Windows/PySide6 capture. The shell-host gap can be closed only if top bar, primary rail, full PALLAS workspace and shared inspector are simultaneously visible. That still does **not** imply `MATCH`; semantic-state richness, geometry, typography, spacing, provenance/history and reference-specific composition remain separately judged.

## Other current open gaps

### ComfyUI shell integration

Status: `OPEN`.

Exact BEFORE is a detached real local-only utility while the original reference is shell-hosted with an Integrations secondary navigation and right Connection inspector. Do not address until the PALLAS candidate is exact-green and visually opened.

### Command Palette workspace context

Status: `OPEN`.

Exact BEFORE is an isolated dialog capture; original reference is an overlay over the Knowledge workspace. Real keyboard and capability semantics already exist. Future work should preserve those semantics and correct only hosting/composition.

### Populated-state gaps

Status: `STATE_UNVERIFIED` for Workspace, Knowledge/Local Memory, Research, Jobs, System and Settings where the exact current runtime is empty, reconnecting or unavailable but the reference is populated/healthy/running. No fake data may be introduced merely to satisfy screenshots.

### Light Workspace

Status: `CURRENT_RENDER_UNAVAILABLE`.

The original light Workspace reference was opened, but the real native harness has no equivalent light same-state product rendering. No visual pair is claimed.

## Historical closed technical gaps

Older numbered UI-GAP entries remain historical evidence only. This ledger's current priority is derived from the opened originals plus the exact BEFORE runtime, not old IDs or run numbers.
