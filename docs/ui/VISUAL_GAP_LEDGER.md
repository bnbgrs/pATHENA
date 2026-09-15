# pATHENA Visual Gap Ledger

Reference review: `2026-09-15`
Candidate branch: `manual/ui-11screen-longrun-20260915`
Base: `develop/pathena-next@3a8120805e41d0fe9d283fc948d6e52b327a8e58`
Integration target: `develop/pathena-next`

All eleven originals in `/pATHENA/Designreferenz – 11 Screenshots` were opened directly before this run. The old evidence blocker that treated ten references as unavailable is closed. No screenshot-level `MATCH` claim is made: exact-head native rendering and side-by-side review remain required.

## UI-GAP-0001 — Inspector naming / evidence ownership

- Category: `HIERARCHY`
- Severity: `P1`
- Status: `FIXED_IN_DEVELOP`
- Contract: evidence and activity are contextual, provenance-backed content rather than a generic always-on status panel.
- Current run: preserved; no regression introduced.

## UI-GAP-0002 — Generic inspector visible on unrelated workspaces

- Category: `INTERACTION / COMPOSITION`
- Severity: `P1`
- Status: `CANDIDATE_REASSERTED`
- Reference evidence: Workspace variants show Evidence/Activity when context exists; Settings, Jobs and System own dedicated detail structures.
- Candidate behavior: final parity controller shows the generic inspector only for Chat when real context is available. Dedicated workspaces keep their own detail panes.
- Product behavior changed: `NO` — presentation/visibility only.

## UI-GAP-0003 — PALLAS full-view lifecycle / shell ownership

- Category: `INTERACTION`
- Severity: `P1`
- Status: `FIXED_IN_DEVELOP / VISUAL_POLISH_CANDIDATE`
- Current Develop already hosts full PALLAS inside the shared shell and preserves living state.
- Candidate adds only reference-family host/status/lens styling; no graph, provenance, force, lens or persistence semantics change.

## UI-GAP-0004 — Composer underscaled relative to Workspace references

- Category: `HIERARCHY / ACCESSIBILITY`
- Severity: `P1`
- Previous state: earlier passes moved the composer to 88 px and a 44×44 send target.
- Status: `CANDIDATE_REFINED`
- Candidate geometry: composer `80–92 px`, centered with `620–980 px` width bounds; prompt `48–56 px`; send target exactly `48×48 px`.
- Rationale: the opened dark Workspace references consistently treat the composer as a major work surface and the send action as a clearly separated circular primary control.
- Functional contract: existing prompt, Sources/grounding and send routes are retained.

## UI-GAP-0005 — Shared visual tokens diverge from the eleven-reference family

- Category: `COLOR / SYSTEM`
- Severity: `P1`
- Status: `CANDIDATE_FIXED`
- Previous Develop: neutral black surfaces with global orange interaction accent.
- Reference evidence: the opened dark family consistently uses deep navy-black surfaces and cobalt blue for primary navigation/focus/action. Warm colors are semantic status accents.
- Candidate: canonical tokens move to navy surfaces (`#061421`, `#06121F`, `#0D1A2A`) and cobalt interaction accent (`#3B82F6`). Warning remains amber (`#E9A84D`).
- Accessibility: subtle metadata contrast remains WCAG AA on canonical dark surfaces and is covered by token tests.

## UI-GAP-0006 — Missing textual primary navigation and visible search affordance

- Category: `NAVIGATION / DISCOVERABILITY`
- Severity: `P1`
- Status: `CANDIDATE_FIXED`
- Reference evidence: the dominant reference family exposes textual top routes and a top-level search/command affordance in addition to the icon rail.
- Candidate: installs `CHAT / KNOWLEDGE / RESEARCH / JOBS / SOURCES`; System and Settings remain utility destinations; search routes to the existing command palette.
- No duplicate routing model is introduced: buttons set the existing navigation row.

## UI-GAP-0007 — Administrative surfaces do not share the reference visual language

- Category: `CONSISTENCY`
- Severity: `P2`
- Status: `CANDIDATE_FIXED_PENDING_RENDER`
- Settings: existing truthful secondary navigation gets canonical navy/cobalt styling and width.
- Jobs: real durable job list/details receive master-detail styling; no synthetic step/resource data is added.
- System: existing snapshot-backed subnav/status/security-posture layout receives reference styling; unavailable telemetry stays unavailable.
- Command palette/help: existing keyboard-first surfaces receive the opened palette/search hierarchy.

## UI-GAP-0008 — PALLAS visual chrome competes with the living graph

- Category: `HIERARCHY`
- Severity: `P2`
- Status: `CANDIDATE_FIXED_PENDING_RENDER`
- Reference evidence: PALLAS is graph-first; controls and status are subordinate.
- Candidate: shell host becomes canvas-level, living status uses semantic green, lens controls become small quiet bordered controls with cobalt selected state.
- No PALLAS simulation or graph behavior changes.

## UI-GAP-0009 — Light-theme reference could be misread as a required capability

- Category: `PRODUCT TRUTH`
- Severity: `P2`
- Status: `GUARDED`
- The opened light screenshot is retained as a composition/reference-language variant only.
- Candidate does not add a light-theme toggle or claim light-theme support.

## Remaining blocker — exact native visual comparison

The candidate must not be promoted to screenshot `MATCH` until:

1. the exact candidate head passes canonical Quality/focused UI tests;
2. the current native Windows build renders the relevant surfaces from that same SHA;
3. those captures are opened side-by-side with the eleven originals;
4. any remaining geometry, typography, density or state-color differences are recorded here rather than patched blindly.

Repository snapshot tests are regression evidence, not proof of fidelity to the user-provided references.
