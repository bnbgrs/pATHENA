# pATHENA Visual Gap Ledger

Baseline: `96489c4c493992ff9d8c7efd57557a69aa578e56`
Worker: `postmerge/ui`

Only evidence-backed gaps belong here. The original 11 reference screenshots were not openable in this run; therefore no pixel-level mismatch or `MATCH` claim is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence before fix: `PathenaMainWindow._replace_visible_copy()` rewrote legacy `INSPECTOR` to `DETAILS`, while `_install_reference_shell()` assigned the right rail accessible name `Inspector`; the versioned UI contract calls for the right-side `Evidence & Activity` inspector.
- Current code: `src/athena/desktop/pathena_window.py`
- Affected widgets: right inspector heading/copy and accessibility naming
- Risk addressed: the right rail no longer reads as generic details; its visible and accessibility semantics now identify the provenance/activity surface.
- Status: `FIXED_PENDING_VERIFY`
- Commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- Test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Acceptance: visible inspector heading and accessible name use `Evidence & Activity` vocabulary without changing provenance, controller, visibility or persistence semantics; focused Qt contract is added and exact-head Quality verification is pending.

## UI-GAP-0002 — Inspector is forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence: `PathenaMainWindow._install_reference_shell()` calls `inspector.show()` and `_sync_progressive_chat_actions()` also unconditionally calls `inspector.show()`, while the current design contract specifies a contextual right inspector.
- Current code: `src/athena/desktop/pathena_window.py`
- Affected widgets: `inspector`, `detailsToggle`, grounded-context controls
- Risk: the inspector consumes permanent workspace width even when no useful contextual evidence/activity is available; changing this behavior may intersect existing progressive-disclosure, focus and reduced-motion contracts.
- Status: `OPEN / REQUIRES_FOCUSED_CONTRACT_REVIEW`
- Commit: `NONE`
- Acceptance: visibility follows an explicit product state contract, preserves focus return, reduced-motion behavior, grounded evidence availability and desktop tests, and does not hide required system/detail state on non-chat surfaces.

## Current run note

`postmerge/ui` was safely history-preservingly synchronized with `develop/pathena-next@96489c4c493992ff9d8c7efd57557a69aa578e56` via two-parent merge commit `9eb906c3f3c85f37e4c1c8dedfea407d09951fa5`. `UI-GAP-0001` then received a surgical presentation-only patch: the visible legacy `INSPECTOR` copy now resolves to `EVIDENCE & ACTIVITY`, and the right panel accessible name is `Evidence & Activity`. The focused Qt shell test now asserts both contracts. No inspector content, controller, persistence, provenance, focus, visibility or disclosure behavior changed.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: the original reference pixels were not successfully opened in this run. Until the relevant reference image and a real rendered current build can both be inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
