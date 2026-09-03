# pATHENA Visual Gap Ledger

Baseline: `7e23616b79b65f759980ad98a27640b6c29bcea0`
Worker: `postmerge/ui`

Only evidence-backed gaps belong here. File Library search can discover several historical pATHENA design images, but the actual image payloads could not be opened in this run; therefore no pixel-level mismatch is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence: `PathenaMainWindow._replace_visible_copy()` currently rewrites legacy `INSPECTOR` to `DETAILS`, while `_install_reference_shell()` assigns the right rail accessible name `Inspector`; the current UI contract calls for a contextual right-side `Evidence & Activity` inspector.
- Current code: `src/athena/desktop/pathena_window.py`
- Affected widgets: right inspector heading/copy and accessibility naming
- Risk: the right rail reads as generic details rather than a provenance/activity surface, weakening information hierarchy and making grounded-state semantics less obvious.
- Status: `OPEN`
- Commit: `NONE`
- Acceptance: visible inspector heading and accessible name use a concise Evidence & Activity vocabulary without changing provenance, controller or persistence semantics; relevant UI tests remain green.

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

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: historical pATHENA image records were discoverable in File Library during this run, including workspace/knowledge/PALLAS-oriented designs, but opening the actual image payloads failed. Until the relevant reference pixels can be inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
