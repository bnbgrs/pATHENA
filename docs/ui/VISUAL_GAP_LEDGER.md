# pATHENA Visual Gap Ledger

Integration target: `develop/pathena-next`
Reference-parity branch: `agent/ui-11-reference-parity-20260911`

All eleven originals in `pATHENA/Designreferenz – 11 Screenshots` were opened directly on 2026-09-11. This ledger therefore separates three things that had previously been mixed together: direct reference evidence, implementation status, and rendered parity proof.

No screenshot-level `MATCH` claim is asserted here. A code change can close a structural gap while still requiring an exact current-build render and human side-by-side review.

## UI-GAP-0001 — Inspector naming did not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Severity: `P1`
- Status: `FIXED / INTEGRATED BEFORE THIS RUN`
- Current contract: the right-hand generic pane is named `Evidence & Activity` and remains evidence-oriented.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION / LAYOUT`
- Severity: `P1`
- Status: `FIXED / STRENGTHENED IN THIS RUN`
- Direct reference evidence: evidence-heavy Workspace references contain a right inspector; Settings, Jobs and System references do not require the same generic evidence pane as a permanent fourth column.
- Current response: the final reference-parity layer hides the generic inspector outside Chat and shows it on Chat only when grounded context is available. Dedicated workspaces keep ownership of their own detail panes.
- Verification status: focused unit coverage added; exact branch Quality gate pending.

## UI-GAP-0003 — PALLAS full-view transition could hit a transient missing tab-order document binding

- Category: `INTERACTION`
- Severity: `P1`
- Status: `FIXED / INTEGRATED BEFORE THIS RUN`
- Current response: this run does not alter PALLAS semantic behavior; it only lets the existing PALLAS surfaces inherit the common screenshot-family visual foundation.

## UI-GAP-0004 — Workspace composer was materially underscaled relative to the reference family

- Category: `HIERARCHY / ACCESSIBILITY`
- Severity: `P1`
- Status: `FIXED / REFINED IN THIS RUN / PENDING RENDER COMPARE`
- Direct reference evidence: multiple Workspace references use a broad rounded lower work surface with a prominent circular send target.
- Current response: final composer geometry is constrained to 80–92 px high, centered up to 980 px wide, with 48 px message input height and a real 48×48 circular send target. The existing Sources action and submission route are retained.
- Verification status: runtime geometry unit coverage added; exact branch Quality gate pending.

## UI-GAP-0005 — Ten of eleven reference images were incorrectly treated as unavailable

- Category: `EVIDENCE / PROCESS`
- Severity: `P0` for visual work
- Status: `FIXED`
- Problem: the previous manifest permitted only one opened reference to influence concrete visual decisions and left the rest as `VISUAL_REFERENCE_PENDING`.
- Current response: all eleven originals were opened before this run's cross-screen design contract was written. The manifest now identifies the actual reference states and records implementation response per image.

## UI-GAP-0006 — Visible textual primary navigation was missing from the current shared shell

- Category: `STRUCTURE / NAVIGATION`
- Severity: `P0`
- Status: `FIXED IN CANDIDATE / PENDING QUALITY + RENDER`
- Direct reference evidence: the reference family repeatedly places textual primary routes across the top while retaining a separate narrow icon rail.
- Previous implementation: primary route names were collapsed into icon-only entries in the left rail; the top bar contained only wordmark, System/Settings utilities and local/private status.
- Current response: a functional `CHAT / KNOWLEDGE / RESEARCH / JOBS / SOURCES` top navigation is installed after all workspace refinements and routes through the existing navigation model. System and Settings remain utility buttons. A visible top search button opens the existing Ctrl+K command palette.
- Safety: no duplicate navigation state or new product destination is introduced.

## UI-GAP-0007 — Foundation color system was neutral black + global orange instead of the opened navy/cobalt family

- Category: `COLOR / HIERARCHY`
- Severity: `P1`
- Status: `FIXED IN CANDIDATE / PENDING RENDER`
- Direct reference evidence: the dark references use cool navy-black surfaces with blue-grey lift and cobalt primary interactions. Orange/gold appears better suited to semantic warning/highlight than global selection chrome.
- Current response: canonical shared tokens now use navy-black canvas/surfaces and cobalt primary accent. Warning remains gold/orange; success/error/information stay semantically distinct.
- Accessibility: the subtle metadata token retains WCAG AA contrast on all canonical dark surfaces; the existing token contract is updated accordingly.

## UI-GAP-0008 — Header hierarchy used an editorial serif treatment not present across the opened application references

- Category: `TYPOGRAPHY`
- Severity: `P1`
- Status: `FIXED IN CANDIDATE / PENDING RENDER`
- Current response: display hierarchy now uses Segoe UI Variable Display / Segoe UI and a 38 px page-title token, while monospaced typography remains reserved for technical metadata.

## UI-GAP-0009 — Shared geometry could be overwritten by later refinement controllers

- Category: `ARCHITECTURE / VISUAL CONSISTENCY`
- Severity: `P1`
- Status: `FIXED IN CANDIDATE / PENDING QUALITY`
- Problem: pATHENA's desktop is composed by many sequential workspace/refinement controllers, so early shell tuning can be silently superseded later in startup.
- Current response: `pathena_reference_parity.py` is installed after functional and progressive workspace refinements. It owns only shared screenshot-family chrome, geometry and state styling; product behavior remains in the existing controllers.

## Remaining proof gap

The repository's 11-surface snapshot workflow can prove regression relative to its committed historical baseline, but that baseline is not the same thing as the user's eleven design-reference images. Final `MATCH` requires a render of this exact candidate SHA and direct side-by-side review against the opened originals. Until then the correct status is `IMPLEMENTED_PENDING_RENDER_COMPARE`.
