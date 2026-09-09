# pATHENA Visual Gap Ledger

Baseline: `82aaef0caaa90599f530acc84d728b602dee6739`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. Slot 01 has direct pixel evidence in this run from the opened user-library reference `pATHENA: Dunkles KI-Dashboard mit Wissenspanel.png`. No screenshot-level `MATCH` claim is asserted because a real rendered current build from the exact candidate SHA has not yet been opened side-by-side with that reference.

## UI-GAP-0001 — Inspector naming does not express the Evidence & Activity contract

- Category: `HIERARCHY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED`
- Product commit: `1f0fd548431be122d13a403fe9e2387087edf8fa`
- Test commit: `d85d2a2e144abc9d3ef1008b80f74114c7fafe23`
- Verification evidence: exact UI head `f31be028652095b18b8a98dfacd65b73be9af763` passed ATHENA Quality Gate `33720745475`; lineage is integrated in Develop.

## UI-GAP-0002 — Inspector was forced permanently visible instead of remaining context-sensitive

- Category: `INTERACTION`
- Screen: `01 — Workspace / Chat`, `10 — Grounded Chat / Evidence & Activity`
- Severity: `P1`
- Status: `FIXED`
- Product commit: `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2`
- Test-contract commit: `1685221150c724deceb5d150a4d2dcff2bdd867b`
- Verification evidence: exact corrected worker head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426`; exact verified blobs were integrated into Develop in `93a9344d3902c920da5ff283eb51bbb1f0d815b8`.

## UI-GAP-0003 — PALLAS full-view transition can hit a transient missing tab-order document binding

- Category: `INTERACTION`
- Screen: `08 — PALLAS`
- Severity: `P1`
- Evidence: canonical Backend run `33744816398` exposed `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface` failing through `MessageActionTabOrderController.eventFilter()` when `document` was transiently absent during Qt lifecycle churn.
- UI candidate product commit: `689da6c1dc2221f89825fffde947f792c7b503e7`
- Focused regression commit: `034cb8d923d48bea708b48cac0ef0f6343511051`
- Status: `FIXED`
- Verification evidence: exact UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` passed ATHENA Quality Gate `33751403354` with conclusion `success`.
- Integration evidence: bounded equivalent product/test changes landed on Develop as `d149f6bbfd367f2999c8ee54e52326695aeb9f55` and `df60ad0e0b3084da05a8b55d94a227798296a1ac`; Backend changes were disjoint.
- Acceptance: transient missing binding is an unhandled/no-op lifecycle state; existing ChildAdded resynchronization, action ordering, disabled-state preservation and composer return target remain unchanged.

## UI-GAP-0004 — Workspace composer is materially underscaled relative to opened reference

- Category: `HIERARCHY / ACCESSIBILITY`
- Screen: `01 — Workspace / Chat`
- Severity: `P1`
- Status: `IMPLEMENTED_PENDING_VERIFY`
- Pixel evidence: the opened user reference shows the composer as a large, prominent work surface near the lower center of the workspace, with a clearly separated arrow send target. Current Develop inherited the legacy `composer.setFixedHeight(58)` and compact controls.
- Candidate behavior: keep the existing real chat input, grounding control and send route; enlarge the composer to 88 px, give the prompt a 44 px minimum interaction height, keep the real grounding control at 36 px minimum, and make the existing send control a 44×44 target with no new or decorative control.
- Product blob candidate: `951d42436388539e0aa1f90760f33c6ef9ebe6fc`.
- Focused Qt contract candidate: `8e29fcfc5e8ac0ba4a402ae07f1f593783588063`.
- Acceptance: no chat submission, grounding, model/provider, persistence, focus, shortcut, accessibility-name or backend semantics change; no fake Attach/Focus controls are introduced.
- Verification required: focused `tests/unit/test_pathena_window.py`, then canonical Quality on the exact candidate head. Screenshot-level parity remains unverified until a current render is opened against the reference.

## Evidence blocker

`VISUAL_REFERENCE_PENDING` still applies to any slot whose original image has not been opened and to all screenshot-level `MATCH` claims until a real rendered current build can also be inspected.
