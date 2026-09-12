# Manual UI 11-screen shell convergence handoff — 2026-09-10

## Purpose

Bounded visual-convergence slice for the approved eleven pATHENA design references.
This branch exists so the active `postmerge/ui` worker can continue independently.
Do not treat it as a new long-lived worker lane.

## Frozen base

- Repository: `bnbgrs/pATHENA`
- Base branch: `postmerge/ui`
- Frozen base SHA: `980729bc2d019b69169192ab3be76fb7b743e6f4`
- Integration target for this slice: `postmerge/ui` first, then normal Develop-first flow.
- `main` is not a target and was not mutated.

## Evidence consumed before mutation

The eleven actual user design references in
`/pATHENA/Designreferenz – 11 Screenshots` were all opened directly. The separate
native-Windows runtime artifact from UI workflow run `34528380154` was downloaded and
all eleven current runtime captures were opened directly as well.

Current exact runtime capture SHA used for the BEFORE comparison:
`191c9cecd6edebe1744d66f0eae6bf9e96e519fe`.

The design references consistently establish:

- a textual top navigation row plus utility controls;
- a narrow icon rail on the far left;
- contextual secondary navigation when the surface needs it;
- a strong central work surface with large editorial display hierarchy;
- a contextual right inspector rather than a globally reused Chat inspector;
- a substantial bottom composer on work surfaces;
- dense but restrained information architecture rather than large unused black areas.

The light reference was consumed for geometry only. The current approved pATHENA
black/orange design direction remains authoritative for palette and interaction state.
No blue/glow/cyberpunk styling was imported merely to imitate reference pixels.

## Direct BEFORE findings

The native screenshots show the same product-shell defect on multiple independent
surfaces:

1. Chat/Workspace, Knowledge, Research, Jobs, Sources, System and Settings have no
   textual top navigation even though `topNavButton` styling already exists.
2. Research, Jobs, Sources, Knowledge and Settings visibly reuse the generic Chat
   inspector, including `CHAT / NONE`, `No conversation selected`, `MESSAGES 0`, and
   `MODE DIRECT` while a non-Chat workspace is active.
3. The global page title hierarchy is much weaker than the reference family.
4. PALLAS, Help and ComfyUI remain functional but visually isolated utility/full-view
   surfaces. Their richer product framing is intentionally NOT fabricated in this
   slice; that remains the next larger integration slice.
5. Several reference states contain populated data that the current deterministic
   capture does not have. Missing data is not permission to create fake content.

These observations agree with `VISUAL-GAP-0001` in the active UI worker ledger.

## Owned paths

This slice owns exactly these paths while review/validation is active:

1. `src/athena/desktop/pathena_layout_refinement_2200.py`
2. `tests/unit/test_pathena_layout_refinement_2200.py`
3. `docs/agent_handoffs/manual-ui-11screen-shell-convergence-20260910.md`

Do not copy these changes into another worker branch while this candidate is being
validated. Do not edit `docs/agent_handoffs/ui.md` from this slice.

## Product changes

### 1. Reference-style textual top navigation

`PathenaLayoutRefinement` now installs real top-bar buttons for the existing routes:

- Workspace
- Library
- Research
- Jobs
- Sources

The buttons drive the existing `navigation` widget and therefore preserve the current
page-selection contract. System and Settings remain the existing utility buttons on
the right. No duplicate route/controller was introduced.

The selected top navigation button is synchronized with the existing icon rail. This
uses the pre-existing `topNavButton` stylesheet contract instead of creating a second
palette or navigation system.

### 2. Non-Chat contextual inspector

A separate `referenceContextInspector` is installed beside the central workspace for
non-Chat routes. It replaces the visually incorrect generic Chat inspector while those
routes are active. Chat keeps the original grounded/direct inspector behavior.

Page contexts are intentionally descriptive rather than synthetic:

- Library -> Knowledge
- Research -> Evidence & Activity
- Jobs -> Execution
- Sources -> Source details
- System -> Security posture
- Settings -> System status

The panel contains no invented counts, no invented Healthy/Ready values and no fake
selection. Copy explicitly states that unavailable status remains unavailable.

### 3. Display-title hierarchy

The existing real `pageTitle` is scaled by the adaptive layout controller:

- compact: 30 px
- comfortable: 36 px
- wide: 40 px

This makes the common workspace hierarchy materially closer to the reference family
without changing page semantics.

## Explicit non-work

This slice does NOT:

- modify Backend/Core/API/Storage/WAL/Security behavior;
- change persistence or network semantics;
- invent data so screenshots look populated;
- replace working PALLAS, Help or ComfyUI controllers with mock pages;
- change the approved black/orange palette;
- edit the active UI worker handoff or visual ledger;
- mutate `postmerge/ui`, `develop/pathena-next`, or `main` directly;
- claim pixel `MATCH`.

## Tests added

`tests/unit/test_pathena_layout_refinement_2200.py` now verifies:

- exactly five real top-navigation buttons are installed;
- their accessible names and labels are stable;
- clicking Research drives the existing navigation/pages state;
- top-navigation checked state follows the route;
- the reference-shell convergence marker is present;
- non-Chat navigation hides the generic Chat inspector;
- the contextual inspector exposes the correct Research and Settings context;
- the contextual copy explicitly refuses synthetic status;
- returning to Chat hides the contextual inspector;
- page-title sizing is 30/36/40 px across compact/comfortable/wide widths;
- the historical 100-task adaptive-layout accounting remains exactly 100.

## Validation rules

Before promoting this slice:

1. Run canonical Quality on the exact branch head.
2. Treat Ruff/mypy/pytest failures in either owned technical path as slice-owned and
   repair them here.
3. If a failure is outside these owned paths, classify it before widening scope.
4. Re-check `postmerge/ui` head before integration. If the worker has modified either
   owned technical path, do not blind-merge; reconcile deliberately.
5. Native-Windows visual evidence is still required before claiming visual improvement.
   The existing visual workflow only auto-runs on `postmerge/ui`/`bot/pathena-candidate`
   pushes or explicit workflow dispatch, so do not fake an AFTER verdict from Linux.
6. If integration changes the exact SHA, obtain new exact-SHA quality/visual evidence.

## Bot consumption rules

- UI bot: treat this as a candidate implementation for `VISUAL-GAP-0001`, not as proof
  that the gap is closed.
- UI bot: when safe, integrate/reconcile these three owned paths, run its native-Windows
  11-surface harness, open the generated screenshots, and compare BEFORE -> AFTER.
- UI bot: do not regress the truthful no-synthetic-status contract just to make a
  screenshot look populated.
- Other bots: no action required. Do not duplicate this slice into Backend, Errors,
  Spec/Core or unrelated Integrator branches.
- Integrator: require current-worker collision review before any Develop promotion.

## Next visual slice after this one

Once this shell slice is accepted and visually re-rendered, the highest-value next
work is `VISUAL-GAP-0002`: bring PALLAS, Help and ComfyUI into richer pATHENA product
framing while reusing their real controllers and data paths. The preferred order is
Help -> ComfyUI -> PALLAS because Help is mostly navigation/presentation, ComfyUI has a
real workflow controller, and PALLAS has the highest semantic/layout complexity.

No `MATCH` is claimed by this handoff.
