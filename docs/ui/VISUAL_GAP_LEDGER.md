# pATHENA Visual Gap Ledger

Baseline: `93a9344d3902c920da5ff283eb51bbb1f0d815b8`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. The original 11 reference screenshots remain unavailable for direct visual comparison; therefore no pixel-level mismatch or `MATCH` claim is asserted.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence before fix: `PathenaMainWindow._replace_visible_copy()` rewrote legacy inspector copy generically while the versioned UI contract calls for the right-side `Evidence & Activity` provenance/activity surface.
- Affected widgets/files: right inspector heading/copy/accessibility naming in `src/athena/desktop/pathena_window.py`
- Status: `FIXED`
- Product commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- Test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Verification evidence: exact UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate `33720745475`; lineage is integrated in Develop.
- Acceptance: visible inspector heading and accessible name use `Evidence & Activity` vocabulary without changing provenance, controller, visibility or persistence semantics; no screenshot-level `MATCH` is implied.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Evidence before fix: `_install_reference_shell()`, `_install_progressive_disclosure()` and `_sync_progressive_chat_actions()` forced the inspector visible even though `_set_context_available()` already represents truthful grounded-context availability.
- Affected widgets/files: `inspector`, grounded-context controls in `src/athena/desktop/pathena_window.py`; presentation contract in `tests/unit/test_pathena_ui_presentation.py`.
- Status: `FIXED`
- Product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`
- Test-contract commit: `1685221150c724deceb5d150a4d2dcff2bdd867b`
- Verification evidence: exact corrected worker head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426`. Integrator independently reviewed both bounded diffs and applied their exact file blobs to unchanged Develop product/test bases in `93a9344d3902c920da5ff283eb51bbb1f0d815b8`.
- Acceptance verified: initial ungrounded Chat hidden; grounded Chat visible; context-clear hidden; non-chat visible; return-to-ungrounded Chat hidden. No screenshot-level `MATCH` is implied.

## UI-GAP-0003 — PALLAS full-view transition can hit a transient missing tab-order document binding

- Category: `INTERACTION`
- Screen: `08 — PALLAS`
- Severity: `P1`
- Evidence: canonical Backend run `33744816398` exposed `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface` failing through `MessageActionTabOrderController.eventFilter()` when `document` was transiently absent during Qt lifecycle churn.
- UI candidate product commit: `689da6c1dc2221f89825fffde947f792c7b503e7`
- Focused regression commit: `034cb8d923d48bea708b48cac0ef0f6343511051`
- Status: `FIXED_PENDING_VERIFY`
- Integration state: not integrated; UI worker requires successful focused/canonical evidence on the corrected lineage before READY.
- Acceptance: transient missing binding is an unhandled/no-op lifecycle state; existing ChildAdded resynchronization, action ordering, disabled-state preservation and composer return target remain unchanged.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
