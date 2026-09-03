# pATHENA Visual Gap Ledger

Baseline: `7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`
Worker: `postmerge/ui`

Only evidence-backed gaps belong here. The original 11 reference screenshots were not openable in this run; therefore no pixel-level mismatch or `MATCH` claim is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence before fix: `PathenaMainWindow._replace_visible_copy()` rewrote legacy `INSPECTOR` to `DETAILS`, while `_install_reference_shell()` assigned the right rail accessible name `Inspector`; the versioned UI contract calls for the right-side `Evidence & Activity` inspector.
- Current code: `src/athena/desktop/pathena_window.py`
- Affected widgets: right inspector heading/copy and accessibility naming
- Risk addressed: the right rail no longer reads as generic details; its visible and accessibility semantics identify the provenance/activity surface.
- Status: `FIXED_PENDING_VERIFY`
- Commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- Test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Verification evidence: prior exact UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate `33720745475`; current Develop-synchronized lineage is undergoing exact-head re-verification.
- Acceptance: visible inspector heading and accessible name use `Evidence & Activity` vocabulary without changing provenance, controller, visibility or persistence semantics; no screenshot-level `MATCH` is implied.

## UI-GAP-0002 — Inspector is forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence: `_install_reference_shell()` and `_install_progressive_disclosure()` call `inspector.show()`, and `_sync_progressive_chat_actions()` unconditionally calls it again. `_set_context_available()` already represents real grounded-context availability; grounded responses set it true, while new/loaded/ordinary sent chat paths clear it.
- Current code: `src/athena/desktop/pathena_window.py`
- Affected widgets: `inspector`, `detailsToggle`, grounded-context controls
- Risk: the inspector consumes permanent workspace width even when Chat has no useful grounded evidence/activity; a careless global hide could instead remove required details from non-chat surfaces.
- Status: `OPEN / CONTRACT_TRACED`
- Commit: `NONE`
- Acceptance: non-chat surfaces retain their required inspector/detail state; Chat inspector visibility is derived from truthful existing grounded-context state rather than unconditional show calls; focus and reduced-motion contracts remain unchanged; focused Qt tests cover new/loaded/plain chat, grounded chat and non-chat navigation.

## Current run note

`postmerge/ui` was history-preservingly synchronized with `develop/pathena-next@7c15b44818e9ac5c3484ee30d4a20d6f0d56087e` through two-parent merge `7952eedcda8cc889e60ced3170e72a762245d00c`. Develop changes since the previous UI base were disjoint from the UI-owned files. No product visibility mutation was made in this run; the call-chain for `UI-GAP-0002` was traced and narrowed to an existing truthful grounded-context state signal.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: the original reference pixels were not successfully opened in this run. Until the relevant reference image and a real rendered current build can both be inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
