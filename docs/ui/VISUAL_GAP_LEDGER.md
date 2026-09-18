# pATHENA Visual Gap Ledger

Reference review: `2026-09-15`
Candidate consolidation: `2026-09-18`
Native Windows review: `2026-09-18`
Reviewed candidate: `0a9f92f8351500f07812857e374a5860884c3029`
Candidate branch: `ui/11-screen-longrun-r2-20260915` (PR `#236`)
Develop merged through: `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`
Integration target: `develop/pathena-next`

All eleven originals in `/pATHENA/Designreferenz – 11 Screenshots` were opened directly before this run. The old evidence blocker that treated ten references as unavailable is closed. Exact-head native rendering and side-by-side review are now complete. No screenshot-level `MATCH` claim is made because the reviewed truthful product states are not pixel-identical to the originals.

## Native Windows comparison — exact SHA `0a9f92f83515`

Evidence: Visual run `35313740239` (`windows-2025`, manifest `PASS`, `11/11`, zero capture
errors), UI Focused run `35313740166` (`SUCCESS`) and ATHENA Quality run `35313740153`
(`SUCCESS`). The Visual run is red only because no reviewed baseline was committed at that SHA;
proposal generation and artifact upload both succeeded. Teardown diagnostics are clean.

| Reference | Closest native capture | Confirmed alignment | Remaining difference / verdict |
|---|---|---|---|
| ComfyUI integration | `11-comfyui.png` | Navy form, bounded connection/workflow/activity groups, cobalt primary action | Current product is a truthful loopback dialog, not the reference's fabricated full integration route and rail. Composition-only; no `MATCH`. |
| PALLAS semantic field | `08-pallas.png` | Shell-hosted graph-first view; Source blue, Claim/Knowledge green, Conflict red; quiet semantic lens controls | Diagnostic graph is smaller and sparser; it has no reference-like grouped branches, minimap, history or selected-object inspector. No `MATCH`. |
| Settings | `07-settings.png` | Secondary navigation, wide model form and truthful System status column; navy/cobalt hierarchy | Only implemented `Models & inference` and `System status` destinations appear. Reference-only General/Privacy/Network/etc. are intentionally absent. No `MATCH`. |
| Help | `10-help.png` | Search-first two-column help hierarchy and real capability rows; PALLAS and Sources are discoverable | Current Help is a capability dialog without the reference shell, shortcut inspector or identical row density. No `MATCH`. |
| Elegant dark workspace | `01-chat.png` | Textual top navigation, narrow rail, navy canvas, restrained composer and cobalt send control | Capture truthfully shows reconnecting Chat instead of invented synthesis/evidence/graph content. No `MATCH`. |
| Jobs | `04-jobs.png` | Real durable Jobs master/detail frame and reference-family palette | No job exists in the isolated native runtime, so steps, logs, resources and execution state remain absent. No `MATCH`. |
| Command palette | `09-command-palette.png` | Keyboard-first search, selection, footer hints, and truthful `Open PALLAS`/`Open Sources` ordering | Current capture is the real dialog rather than the full Knowledge backdrop; category grouping and dimensions differ. No `MATCH`. |
| System | `06-system.png` | Secondary rail, broad health rows, recent-events region, security posture and navy diagnostic cards | Snapshot-backed facts are unavailable in the isolated run and stay labelled unavailable/awaiting rather than copied from the reference. No `MATCH`. |
| Dark research studio | `03-research.png` | Shared dark shell, explicit Research inputs and real result/canonical-memory master/detail region | No research run exists, so the reference synthesis map, graph cards, evidence and activity content are absent. No `MATCH`. |
| Light intelligence studio | `05-files.png` plus shared shell captures | Shared spacing/navigation principles were checked | Light theme is a concept reference only; no unsupported light capability was added. No `MATCH`. |
| Local memory | `02-knowledge.png` | Repository-backed list, real selected canonical detail and provenance on the shared dark shell | Product Knowledge uses review/list/detail semantics rather than the reference's synthetic workspace graph/activity composition. No `MATCH`. |

Review total: `11/11` originals inspected, `11/11` native product captures inspected,
`MATCH=0/11`. The committed Windows baseline is a regression lock for these approved truthful
states and must never be cited as original-reference parity.

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
- Previous state: earlier passes moved the composer to 88 px and a 44×44 send target; the
  first consolidated candidate accidentally widened that target to 48 px.
- Status: `CANDIDATE_REFINED`
- Candidate geometry: composer `80–92 px`, centered with `620–980 px` width bounds; prompt
  `48–56 px`; send target restored to exactly `44×44 px` through the shared shell token.
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

## UI-GAP-0010 — Knowledge capture did not prove persisted content

- Category: `PRODUCT TRUTH / VISUAL EVIDENCE`
- Severity: `P1`
- Status: `CANDIDATE_FIXED_PENDING_NATIVE_RENDER`
- Previous state: the sequential renderer could navigate to Knowledge, but an empty or
  still-loading surface did not prove the repository-backed list/detail path.
- Candidate behavior: the renderer creates three clearly labelled reference entries through
  `AthenaApplication` and `KnowledgeRepository` inside its disposable `ATHENA_LOCAL_ROOT`, then
  waits for the real `KnowledgeWorkspace` subprocess to load both the persisted list and a
  verified detail before capture.
- Isolation contract: no production profile, user database or backend response is modified;
  repeated seeding is idempotent and confined to the disposable visual-test runtime.
- Parser contract: Knowledge/Obsidian subprocesses run with routine Core logging suppressed so
  their machine-readable stdout cannot be prefixed by application lifecycle logs.
- Evidence boundary: the focused repository-to-QProcess-to-widget regression is green locally;
  native Windows pixels from the exact committed SHA are still required.

## UI-GAP-0011 — PALLAS semantics collapsed into one legacy accent

- Category: `COLOR / SEMANTIC HIERARCHY`
- Severity: `P1`
- Status: `CANDIDATE_FIXED_PENDING_NATIVE_RENDER`
- Reference evidence: Sources are cobalt, Claim/Knowledge/Related nodes are green, Questions are
  violet, Conflicts are red and uncertain state remains amber.
- Candidate behavior: the real PALLAS renderer resolves every existing `PallasNodeKind` through
  the canonical design tokens; the living graph and provenance model are unchanged.

## UI-GAP-0012 — PALLAS and Sources were inconsistent in command discovery

- Category: `DISCOVERABILITY / TERMINOLOGY`
- Severity: `P1`
- Status: `CANDIDATE_FIXED_PENDING_NATIVE_RENDER`
- Candidate behavior: the existing shell-hosted synchronized PALLAS controller is exposed through
  one idempotent `Open PALLAS` command. Workspace row four is presented consistently as `Sources`
  in commands, help metadata and navigation guidance while internal file-ingestion class names stay
  unchanged.
- Truth boundary: the command opens the existing graph; it does not advertise universal search or
  create a second graph/dialog state.

## UI-GAP-0013 — Settings labels did not match their real reference roles

- Category: `COPY / ACCESSIBILITY`
- Severity: `P2`
- Status: `CANDIDATE_FIXED_PENDING_NATIVE_RENDER`
- Candidate behavior: the only implemented Settings destinations are now labelled
  `Models & inference` and `System status`, with corresponding accessible descriptions and no
  fabricated General, Privacy, Network, Appearance, Knowledge or Advanced routes.

## Exact native visual comparison — completed, gaps retained

The candidate was reviewed under the required boundary:

1. exact SHA `0a9f92f8351500f07812857e374a5860884c3029` passed canonical Quality and focused UI tests;
2. its native Windows build rendered all eleven product surfaces;
3. every capture was opened side-by-side with the closest original;
4. remaining geometry, typography, density and state differences are recorded above rather than hidden by synthetic data or unsupported routes.

Repository snapshot tests and the accepted Windows baseline remain regression evidence, not proof of fidelity to the user-provided references. `MATCH` remains unavailable for all eleven slots.
