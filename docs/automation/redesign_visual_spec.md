# pATHENA Eleven-Screenshot Visual Specification

Status: **AUTHORITATIVE TEXTUAL FALLBACK**

Derived interactively on 2026-08-25 from the actual eleven original PNG references stored in the user's ChatGPT File Library. This file exists because scheduled UI/QA runs can currently find the image files but may not receive native image pixels. The original PNGs remain the highest visual authority whenever a run can actually open them. This document must never be treated as permission to claim pixel-perfect parity without image access.

## Source references

1. `pATHENA im eleganten Dunkelmodus.png`
2. `PALLAS – Lebendes semantisches Wissensfeld.png`
3. `pATHENA Einstellungen für lokale KI.png`
4. `pATHENA Hilfe: Fähigkeiten im Überblick.png`
5. `pATHENA – Dunkles Studio für Wissensforschung.png`
6. `pATHENA: Intelligenzstudio für lokales Wissen.png`
7. `pATHENA: Lokales Gedächtnis neu gedacht.png`
8. `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png`
9. `pATHENA Such- und Befehlspalette.png`
10. `pATHENA Systemübersicht für lokale KI.png`
11. `ComfyUI-Integration im pATHENA Studio.png`

## Non-negotiable global visual language

### 1. The current orange legacy shell is not the target

The target is a refined editorial/knowledge-studio application, not the current ATHENA-derived text-sidebar workspace. Do not preserve the old 218 px orange-highlighted text rail merely because existing widgets already exist.

### 2. Global shell

Across the dark references, the dominant shell is:

- a full-width top bar, approximately 54–64 px high;
- `pATHENA` wordmark at far left;
- horizontal primary navigation in the top bar (`CHAT`, `KNOWLEDGE`, `RESEARCH`, `JOBS`, `SOURCES`) or, in the studio-family references, (`WORKSPACE`, `LIBRARY`, `SESSIONS`, `RUNS`);
- active top-nav item indicated by electric/cobalt blue text and/or a thin blue underline;
- utility icons at top right: search, filter/sliders, compose/edit, settings and similar contextually relevant controls;
- a green-dot `Local · Private` status at the far right;
- a very narrow icon-only vertical rail on the far left, roughly 68–82 px wide, not a wide text navigation sidebar;
- icon rail uses outlined monochrome icons; current context may use a blue outlined/filled selection state;
- optional second navigation column appears only on screens that need local section navigation (Settings, Help, System, Knowledge, Integrations, Jobs), usually roughly 210–280 px;
- a persistent right-side inspector/context/evidence column on information-rich screens, typically roughly 330–390 px;
- fine 1 px separators and restrained borders organize regions; avoid card soup and avoid thick orange outlines.

### 3. Color system

Dark references use a deep blue-black/navy background rather than flat pure black. The primary interaction accent is electric/cobalt blue, not orange. Semantic colors are used sparingly:

- blue: selection, navigation, sources, primary actions;
- green: healthy/verified/supported/knowledge states;
- cyan/teal: design principle or informational semantic nodes;
- violet/purple: questions and some integration semantics;
- orange/red/coral: conflicts, risks, disconnected/error states;
- neutral gray: secondary text, disabled, pending.

No neon glow, CRT, cyberpunk bloom or glassmorphism. Surfaces are dark matte panels with subtle border contrast.

One of the eleven references is an intentional light-mode variant (`pATHENA: Intelligenzstudio für lokales Wissen.png`). It preserves the same geometry, hierarchy and blue-led semantic system in an ivory/off-white theme. Treat it as evidence that geometry and information architecture must be theme-independent; do not force the entire application into light mode unless that theme is explicitly active.

### 4. Typography

The reference family deliberately mixes:

- large high-contrast editorial serif headings for primary workspace titles (for example `How should local memory evolve?`, `Settings`, `System`, `ComfyUI`, `Adaptive memory`);
- clean sans-serif for navigation, body copy, labels, controls and metadata;
- restrained small caps/uppercase only where functional.

This serif/sans hierarchy is one of the strongest differences from the current all-sans legacy shell. Do not reduce primary page titles to tiny utility labels.

### 5. Density and spacing

The target is spacious but not empty. Large areas are occupied by meaningful composition: synthesis text, reasoning maps, graph cards, lists, evidence, activity, settings, execution steps or structured status. Empty black rectangles are not acceptable substitutes for the reference composition.

Use generous margins around primary headings, compact but readable row spacing, and clear sectional rhythm. Controls are generally medium-height, with thin borders and modest corner radii.

### 6. Composer

Workspace/chat references use a large, anchored bottom composer rather than a tiny single-line bar. It includes context/action icons at the left, prompt text centered/left, optional privacy/status controls and a prominent circular blue send/action button at the right.

### 7. Right inspector

The right column is a first-class part of the composition, not an optional afterthought. Depending on screen it shows evidence cards, activity timeline, selected knowledge details, security posture, system status, execution metadata or connection state. It should visually align with the main canvas and use semantic status color sparingly.

## Screen-specific acceptance targets

### A. `pATHENA im eleganten Dunkelmodus.png` — canonical dark workspace/chat shell

This is the strongest canonical shell reference.

- Top bar: `pATHENA`, `WORKSPACE`, `LIBRARY`, `SESSIONS`, `RUNS`; blue active underline under WORKSPACE; utilities and `Local · Private` on right.
- Left icon rail only; no wide text nav.
- Main workspace title is very large serif: `How should local memory evolve?`.
- Left/center content includes `Synthesis` in blue, substantial explanatory text and numbered evidence markers.
- Lower-left contains a compact branching `Reasoning outline`, not a generic empty panel.
- Center/right main canvas contains semantic cards/nodes on a dotted graph field with curved connectors: Design principle, User need, Risk.
- Right inspector has `Evidence` source cards and an `Activity` timeline.
- Bottom composer is wide, rounded, feature-rich and ends in a large circular blue action button.
- Background is navy-black; blue is primary; green/cyan/red semantic accents.

Any screen still dominated by the legacy orange left text sidebar fails this reference structurally.

### B. `PALLAS – Lebendes semantisches Wissensfeld.png`

- Top bar has PALLAS as an active primary destination with blue underline.
- Far-left icon rail remains narrow.
- Large central graph canvas occupies most of the window.
- Breadcrumb above graph: knowledge field → architecture → selected knowledge.
- A selected central knowledge object is visually prominent and connected by curved lines to grouped semantic regions.
- Semantic groups and colors: Sources blue; Claims green; Questions violet; Conflicts coral/red; Related knowledge green.
- Nodes are readable and spatially organized, not ASCII/terminal art.
- Lower-left graph controls include Focus/Fit-to-view and a minimap/zoom module.
- Right inspector shows selected object's title, description, confidence, provenance counts, connection legend and history timeline.
- PALLAS should feel like an interactive semantic field, not a decorative mini-panel.

### C. `pATHENA Einstellungen für lokale KI.png`

- Top bar uses `WORKSPACE`, `LIBRARY`, `SESSIONS`, `RUNS`, `SETTINGS`, with SETTINGS active in blue.
- Narrow far-left icon rail plus a second Settings category column (`General`, `Models & inference`, `Privacy`, `Network`, `Appearance`, `Knowledge`, `Advanced`).
- `Settings` is a large serif heading.
- Main form uses horizontal label/description on left and control on right.
- Model configuration section includes Primary model, Context length, Fallback model, automatic fallback toggle and Edit system prompt.
- Privacy/network section includes Internet access, Tor and Local processing toggles.
- Sticky/bottom save row includes unsaved indicator and prominent blue `Save changes` button.
- Right inspector is `System status`, showing model, database and Tor states with semantic green/red icons.

### D. `pATHENA Hilfe: Fähigkeiten im Überblick.png`

- Global top bar uses CHAT/KNOWLEDGE/RESEARCH/JOBS/SOURCES.
- Narrow icon rail + Help subnavigation (`Getting started`, Chat, Knowledge, Research, Jobs, Sources, Integrations, Shortcuts).
- Large serif heading `What can pATHENA do?` and a help-search field below.
- Main content is a clean vertical capability catalogue with large line icons, serif capability names, one-line descriptions and blue `Open` actions.
- Right inspector contains Quick shortcuts (`Ctrl K`, `Ctrl Space`) and a `Help is current` status sourced from active capabilities.

### E. `pATHENA – Dunkles Studio für Wissensforschung.png`

- Studio-family shell: pATHENA left, top nav WORKSPACE/LIBRARY/SESSIONS/RUNS.
- Very narrow icon rail.
- Main view is a three-region composition: left synthesis/reasoning, center graph/card canvas, right Evidence + Activity.
- Large multi-line serif research question title.
- Left contains synthesis and explicit principles plus a reasoning map.
- Center is a dotted canvas with substantial semantic cards connected by lines.
- Right contains source cards and timeline activity.
- Wide anchored bottom composer overlays/anchors the main area with circular blue send button.

### F. `pATHENA: Intelligenzstudio für lokales Wissen.png`

- This is the light-mode sibling of the studio workspace.
- Preserve the same structural hierarchy as the dark studio: horizontal top nav, narrow icon rail, large serif title, synthesis, reasoning outline, graph cards, right Evidence/Activity, bottom composer.
- Theme uses off-white/ivory surfaces with dark text, fine gray lines and the same blue/green/red semantic system.
- Do not interpret this as a different product architecture; it proves the shell should theme cleanly.

### G. `pATHENA: Lokales Gedächtnis neu gedacht.png`

- Dark knowledge/workspace composition with large serif question/title and structured synthesis.
- Main right/center area uses semantic memory cards connected in a small knowledge map; Evidence and Activity occupy the right inspector.
- Reasoning outline/tree appears below the synthesis.
- Bottom composer is anchored and prominent.
- Same narrow rail, horizontal top navigation and blue-led dark theme.

### H. `pATHENA Jobs: Prüfung der Speicher-Richtlinie.png`

- Global top bar with JOBS active in blue.
- Narrow icon rail.
- Second left column is a job navigator grouped into Running, Scheduled and Completed.
- Main pane: large serif job title, running status/step count, Goal text, vertical stepper with completed/current/pending states, Live log table, Pause and Cancel actions.
- Right inspector: Execution metadata (model, permissions, network, workspace, elapsed, IDs) and collapsible Resources (CPU, memory, disk I/O, threads).
- Layout is information-dense and three-column, not a blank jobs list plus generic details.

### I. `pATHENA Such- und Befehlspalette.png`

- Underlying screen is the full Knowledge UI: top KNOWLEDGE active, narrow icon rail, secondary Knowledge navigation, main list and right note inspector.
- Command palette appears as a centered modal approximately half-to-two-thirds of the content width, with a blue-focused search field.
- Results are grouped (`Recent`, `Knowledge`, `Sources`, `Actions`) with icon, label and right-side affordance (`Open`, `Enter`).
- Selected result uses a restrained blue selection band.
- Bottom help row shows keyboard navigation, Enter/Open and Esc/Close.
- Background application remains visible but dimmed/subdued; palette is not a separate full page.

### J. `pATHENA Systemübersicht für lokale KI.png`

- Global top bar; narrow icon rail + secondary System nav (`Overview`, `Runtime`, `Storage`, `Network`, `Logs`).
- Large serif `System` heading.
- Main column is not an eight-card metrics grid. It is a vertical set of major status rows: Local runtime, Knowledge storage, Connectivity, Background work. Each row has a large outlined icon, semantic status text and a quiet right-side action.
- Below is a `Recent events` table/list with timestamps and categories.
- Right inspector is `Security posture`: Loopback only, Local processing, Encrypted at rest, Tor status, followed by a network-settings action.
- If a backend metric is unavailable, show truthful unavailable state; do not invent data. But lack of telemetry must not be used to preserve the old card-grid geometry.

### K. `ComfyUI-Integration im pATHENA Studio.png`

- Global CHAT/KNOWLEDGE/RESEARCH/JOBS/SOURCES top bar and narrow icon rail.
- Second column titled `Integrations`, listing LM Studio, Obsidian and ComfyUI; ComfyUI selected in blue.
- Main pane has large serif `ComfyUI`, green Connected state, prompt textarea and a compact 2-column form for Workflow, Resolution, Steps, Output and VRAM policy.
- A horizontal six-step workflow visualization (`Prepare`, `Load`, `Generate`, `Decode`, `Save`, `Attach`) occupies a bounded panel.
- Lower status row may show integration readiness (e.g. Obsidian sync) with semantic status.
- Right inspector `Connection`: Ready state, endpoint, available VRAM, current model and a prominent blue `Run workflow` button.
- Do not collapse this into a generic dialog if ComfyUI is meant to be a first-class integration surface.

## Structural implementation order

Until the candidate visibly matches the family, prioritize:

1. Replace legacy wide text sidebar with shared top navigation + narrow icon rail architecture.
2. Introduce shared page geometry supporting optional secondary section nav and persistent right inspector.
3. Replace orange-first legacy tokens with navy/blue-led reference token system and semantic colors.
4. Establish serif primary-heading + sans UI hierarchy.
5. Rebuild canonical Workspace/Chat shell and bottom composer.
6. Rebuild shared inspector/evidence/activity components.
7. Implement Knowledge/Research/Jobs/System/Settings layouts against this geometry.
8. Implement PALLAS as full semantic graph workspace with inspector and graph controls.
9. Implement Palette/Help/ComfyUI reference layouts.
10. Only after these structural milestones should small cosmetic polish or unrelated UI features outrank visual parity.

## Acceptance terminology

- `MATCH`: actual original image was visible in the run and the relevant candidate surface was visually reviewed against it with no material structural/design mismatch.
- `PARTIAL`: original image was visible and the structure is moving toward it but material gaps remain.
- `VISUAL_FAIL`: original image was visible and material mismatch exists.
- `REFERENCE_IMAGES_UNAVAILABLE`: original pixels were unavailable; use this textual spec for implementation planning, but do not claim MATCH.
- `TEXT_SPEC_CONFORMING`: may be used when pixels are unavailable but the rendered candidate has been checked against this textual fallback. It is never equivalent to MATCH.

## Important distinction: capture vs design validation

The candidate-bound 11-surface capture harness proves only that the real Qt surfaces can be rendered consistently. A generated baseline from the current candidate proves regression stability of that current look. Neither is evidence that the target reference design has been implemented.
