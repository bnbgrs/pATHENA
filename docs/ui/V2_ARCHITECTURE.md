# pATHENA UI v2 — Product Architecture

Status: ACTIVE IMPLEMENTATION
Branch: `ui/v2-rebuild`
Scope: native PySide6 desktop UI only. Backend, persistence, repositories, providers, scheduler and domain contracts remain unchanged.

## 1. Product intent

pATHENA v2 is a local intelligence workspace, not a dashboard and not a terminal skin. The UI should make powerful local AI workflows feel calm, obvious and controllable.

The visual design is intentionally new. Historical screenshots, the v1 regression bundle and `pathena_reference_parity.py` are not design targets.

Primary goals:

- one obvious place to work;
- progressive disclosure instead of permanent machinery;
- strong hierarchy without visual noise;
- fast keyboard and mouse operation;
- truthful local/offline state;
- durable evidence and provenance available when relevant;
- consistent behavior across every workspace;
- no invented backend capability.

## 2. Information architecture

Primary navigation is deliberately small:

1. Chat — everyday local AI work.
2. Knowledge — durable memory, claims, provenance and review.
3. Research — structured research runs, evidence and synthesis.
4. Jobs — durable background execution and recovery.
5. Sources — imported files, source state and ingestion.
6. PALLAS — dedicated semantic field, opened as a first-class workspace.
7. System — runtime health, storage, backup and security.
8. Settings — model, inference, integrations and application preferences.

Command Palette and Help are global overlays, not persistent primary destinations.

## 3. Shell anatomy

The persistent shell has four zones.

### A. Primary rail

A narrow 200–220 px rail containing:
- product identity;
- primary routes;
- PALLAS entry;
- System and Settings at the bottom.

The rail never carries live metrics, model configuration, logs or secondary controls.

### B. Context header

A 68–76 px header containing:
- current workspace title;
- one-line purpose/status hint;
- global command/search entry;
- compact Core/provider state.

No breadcrumbs unless hierarchy is actually deeper than one level.

### C. Main canvas

The main canvas owns the current workspace. It uses the full remaining width by default.

Workspace content must avoid generic card grids. Each route uses one of the canonical v2 compositions described below.

### D. Context inspector

The inspector is optional and contextual. It is hidden by default and opens only for:
- grounded Chat evidence/provenance;
- selected Knowledge/Claim details;
- selected Research evidence/result details;
- selected Job execution details;
- selected Source details;
- PALLAS selection.

It is never an always-visible generic panel.

Target width: 320–380 px. It must not force the primary canvas into an unusably narrow state.

## 4. Canonical workspace compositions

### Chat

Composition:
- compact conversation/model toolbar;
- large scrollable document-like transcript;
- contextual evidence rail only when grounded evidence exists;
- anchored composer at the bottom;
- optional inspector.

The composer is the visual anchor. Conversation text is not rendered as consumer-messenger bubbles.

Primary actions:
- choose conversation;
- choose local model;
- new/delete conversation;
- Ground toggle;
- send.

Secondary inference controls belong in Settings or a compact per-model popover, not permanently in Chat.

### Knowledge

Composition:
- filter/search line;
- compact mode tabs where required by real contracts;
- master list on the left;
- readable selected-item detail in the center;
- optional provenance inspector on demand.

The selected object must dominate visual hierarchy. Lists should be scan-friendly, not spreadsheet-like.

### Research

Composition:
- query/start control at top;
- run list/history in a narrow pane;
- current synthesis/result as the primary document surface;
- evidence/proposals as contextual secondary material.

Research should visually communicate process and result, not expose every execution mechanism at once.

### Jobs

Composition:
- durable jobs list;
- selected job status, phases and recovery actions;
- execution/log detail as progressive secondary content.

State colors are semantic only: success, warning, failure, running.

### Sources

Composition:
- source list/filter;
- selected source details and ingestion state;
- import/process actions near the relevant context;
- no fake library browser.

### PALLAS

PALLAS is a separate immersive workspace rather than a decorative widget in the sidebar.

Composition:
- semantic field gets the majority of the canvas;
- minimal viewport controls;
- selection inspector;
- explicit node semantics for Sources, Claims, Knowledge, Questions, Conflicts and related entities.

### System

Composition:
- quiet grouped health rows;
- runtime/provider/storage state;
- backup/recovery grouped separately;
- security posture and recent events only when real data exists.

System is an operations page, not a monitoring dashboard full of decorative metrics.

### Settings

Composition:
- narrow section navigation when multiple categories are present;
- one readable settings form;
- contextual explanatory text;
- provider/model truth surfaced close to model controls.

## 5. Interaction architecture

Global:
- Ctrl+K opens command palette.
- Escape dismisses transient UI before changing workspace context.
- focus returns to the invoking control after dialogs/overlays.
- keyboard focus must remain visible.
- no action is enabled unless the underlying contract says it is available.

Navigation:
- primary navigation changes one workspace only;
- route state remains stable when secondary UI opens/closes;
- opening PALLAS or overlays must not mutate Chat/Knowledge selection.

Inspector:
- explicit show/hide API;
- current workspace owns inspector payload;
- inspector content may persist during loading only when marked as retained/stale.

## 6. Visual system

Aesthetic: modern precision, quiet depth, restrained contrast.

Base:
- near-black neutral background;
- slightly lifted neutral surfaces;
- thin low-contrast borders;
- crisp light typography;
- one cool primary accent;
- semantic green/amber/red only for state.

Avoid:
- glow;
- glassmorphism;
- gradients used as decoration;
- CRT/terminal motifs;
- oversized decorative icons;
- heavy card grids;
- permanent all-caps technical chrome.

Typography:
- human-readable sentence case;
- strong 17–22 pt workspace titles;
- 10–11 pt body/control text;
- small uppercase labels only for tiny metadata/eyebrows.

Spacing:
- 4 px base rhythm;
- 8/12/16 px local spacing;
- 24/28/32 px workspace spacing.

Corners:
- 8–10 px controls;
- 12–14 px major interactive surfaces;
- avoid rounding every container.

## 7. Component architecture

UI v2 should converge on four implementation layers:

### `pathena_v2_theme.py`
Tokens and stylesheet only. No product behavior.

### `pathena_v2_components.py`
Reusable presentation primitives:
- NavigationButton;
- WorkspaceHeader;
- SectionLabel;
- StatusPill;
- EmptyState;
- InspectorShell;
- SurfaceFrame;
- Toolbar.

No domain API calls.

### `pathena_v2_shell.py`
Application composition:
- primary rail;
- context header;
- workspace host;
- inspector host;
- global callbacks.

No backend logic.

### Workspace adapters
Small v2 composition adapters around existing functional workspace widgets. They may recompose/reparent real controls but must not duplicate controller behavior.

## 8. Legacy migration rules

The old UI is a compatibility source, not a visual source.

Keep:
- existing real controls where their signals/contracts are proven;
- controllers;
- repositories;
- process and persistence wiring;
- accessibility behavior that remains valid.

Retire from the v2 startup path as replacement coverage lands:
- `pathena_reference_parity.py`;
- shell-density overrides;
- legacy workspace presentation copy/styling;
- numbered visual refinement layers;
- old layout refinements;
- old progressive visual refinements.

A legacy layer may remain temporarily only when it provides functional behavior not yet represented in v2. Its ownership must be documented.

Do not add new numbered refinement modules.

## 9. Delivery sequence

Phase A — Foundation
- v2 theme;
- shared components;
- shell;
- Chat;
- command palette integration;
- inspector contract.

Phase B — Knowledge and Research
- recompose both as native v2 workspaces;
- preserve existing persistence and run contracts.

Phase C — Sources and Jobs
- master/detail patterns;
- state and recovery actions.

Phase D — PALLAS
- dedicated workspace composition;
- selection inspector.

Phase E — Settings and System
- administrative information architecture;
- remove remaining v1 presentation layers.

Phase F — Help, ComfyUI, polish
- global Help;
- integration surfaces;
- responsive sizing;
- native screenshot review;
- package acceptance.

## 10. Acceptance gates

A v2 slice is complete only when:

1. it changes a real visible or interaction surface;
2. it reuses real product contracts;
3. focused Qt tests cover the route/interaction contract;
4. Ruff and relevant type checks are clean;
5. a fresh native screenshot is generated from the exact SHA;
6. no historical screenshot baseline is used as the design goal.

UI v2 completion is not measured against v1 pixel similarity. It is measured by:
- functional route coverage;
- interaction correctness;
- consistency of the v2 component system;
- absence of legacy presentation layers in the startup path;
- fresh native review.
