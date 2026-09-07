# pATHENA Visual Gap Ledger

Baseline: `78519f7c94df31b3c2374e5a1124fe799db28929`
Integration target: `develop/pathena-next`

Only evidence-backed gaps belong here. The original 11 reference screenshots remain unavailable for direct visual comparison; therefore no pixel-level mismatch or `MATCH` claim is asserted.

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

## UI-GAP-0060 — Context disclosure help was not exposed to accessibility

- Category: `ACCESSIBILITY`
- Screen: `10 — Grounded Chat / Evidence & Activity`
- Severity: `P2`
- Status: `FIXED`
- Product commit: `0565720d2d3b3349e6fc8556083dc035fa8c389f`
- Focused regression commit: `70f8867a2645cd2795853745f54844efe8c70d0c`
- Verification evidence: exact UI head `70f8867a2645cd2795853745f54844efe8c70d0c` passed ATHENA Quality Gate `34113040437` with conclusion `success`.
- Acceptance: the existing truthful context tooltip is mirrored into `accessibleDescription`; visibility, grounding, Evidence & Activity and backend semantics are unchanged.

## UI-GAP-0061 — Settings control help is visual-only instead of screen-reader available

- Category: `ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P2`
- Status: `FIXED`
- Product commit: `ffac0e737c3c3457a49ce4b830492f26ba7127d1`
- Focused regression commit: `930dc168f5700f03720601664caf23b08ecd7603`
- Verification evidence: exact UI head `8454d633810283e47d0b9bb9b93321536440cb45` passed ATHENA Quality Gate `34118404763` with conclusion `success`.
- Acceptance: existing tooltip help is mirrored into `accessibleDescription`; context/output/temperature/reasoning values, model/provider routing and persistence semantics are unchanged.

## UI-GAP-0062 — Cancellation-requested Jobs help leaks an internal persisted-state token

- Category: `COPY`
- Screen: `04 — Jobs`
- Severity: `P2`
- Status: `FIXED`
- Evidence: `JobActionAvailability.reason()` surfaced the literal `cancel_requested` persistence token in visible action-help text when cancellation had already been persisted.
- Product commit: `f82be0e672659ee74ce8aecae5a7b4f157cbe6a0`
- Focused regression commit: `c37c8b17a5b33a68068c04c5b5b0fe41b53e927c`
- Verification evidence: exact UI head `8bd74b266028ccfac5b06d286f84d805261ac9e6` passed ATHENA Quality Gate `34124133923` with conclusion `success`.
- Acceptance: keep the persisted lifecycle state and all enabled/disabled action semantics unchanged while presenting a human-readable cancellation-requested explanation without the underscore-delimited internal token.

## UI-GAP-0063 — Jobs action help exposes persistence/lifecycle implementation jargon

- Category: `COPY`
- Screen: `04 — Jobs`
- Severity: `P2`
- Status: `FIXED`
- Evidence: `JobActionAvailability.reason()` described ordinary action availability as `persisted state ...` and terminal states as having no `lifecycle mutation`.
- Product commit: `50eb723d18430735b5dcbb246563ae8e863c62a9`
- Focused regression commit: `1a92d020d565424da147909f137779f7ce1e35fc`
- Verification evidence: exact UI head `e4123e2085b9c7c20f5dffdc8faba19d14296c57` passed ATHENA Quality Gate `34129349248` with conclusion `success`.
- Acceptance: preserve the durable-state action matrix and transition semantics exactly while expressing enabled, disabled and terminal action help without `persisted state` or `lifecycle mutation` jargon.

## UI-GAP-0064 — Terminal Jobs help still uses lifecycle-domain jargon

- Category: `COPY`
- Screen: `04 — Jobs`
- Severity: `P2`
- Status: `FIXED`
- Evidence: after UI-GAP-0063, terminal-state help still used the visible phrase `no lifecycle action is available`, exposing the same internal lifecycle-domain vocabulary in a remaining branch of `JobActionAvailability.reason()`.
- Product commit: `717aee14e7a357bf1022dda5c4e5d9ac006ef0f8`
- Focused regression commit: `d294b7a0e96464d5700c00af3565895a526622f1`
- Verification evidence: exact UI head `b4297ae1e54e2bbf8b2f8d673018077590b029c8` passed ATHENA Quality Gate `34134425435` with conclusion `success`.
- Acceptance: terminal-state help says `no job action is available`; state normalization, enabled/disabled action matrix, transition receipts and backend/storage/scheduler semantics remain unchanged.

## UI-GAP-0065 — Empty Jobs action help exposes storage-domain terminology

- Category: `COPY`
- Screen: `04 — Jobs`
- Severity: `P2`
- Status: `FIXED`
- Evidence: the no-selection branch of `JobActionAvailability.reason()` visibly said `Select a durable job first.`, exposing persistence-oriented terminology that is unnecessary for the user action.
- Product commit: `0ac91c9f471bb14aa6094f78d017cd59d529d868`
- Focused regression commit: `25f8c53cfef2f9524ec3ce2b696809bc1159893c`
- Verification evidence: exact UI head `89cea7ecfaeb75a694a0682ff39feb5172ffbcfa` passed ATHENA Quality Gate `34139713588` with conclusion `success`.
- Acceptance: empty-selection help says `Select a job first.`; action availability, state normalization, transition receipts and backend/storage/scheduler semantics remain unchanged.

## UI-GAP-0066 — Unknown Jobs state leaves a visible destructive action fail-open

- Category: `STATE`
- Screen: `04 — Jobs`
- Severity: `P1`
- Status: `FIXED`
- Evidence: `action_availability()` treated every non-terminal, non-`cancel_requested` state as cancellable, so an unrecognized persisted/future state could enable the visible `CANCEL` control despite having no established UI transition contract.
- Product commit: `83c57b7898515085c7ba4f9441029165c3123890`
- Focused regression commit: `96891f1d68ee9e0242c41aa4b846fea39094ec54`
- Verification evidence: exact UI head `7fe5d44e4271dcbec6c0bfba92e0a01a0671b69f` passed ATHENA Quality Gate `34144645412` with conclusion `success`.
- Acceptance: unknown states disable pause/resume/wake/cancel and expose neutral `unrecognized state` help; known-state action availability, receipt parsing, scheduler/worker/storage and backend semantics remain unchanged.

## UI-GAP-0067 — Jobs action help is visual-only instead of screen-reader available

- Category: `ACCESSIBILITY`
- Screen: `04 — Jobs`
- Severity: `P2`
- Status: `IMPLEMENTED_PENDING_VERIFY`
- Evidence: `_sync_action_buttons()` placed the established action-availability explanation only in each PAUSE/RESUME/WAKE/CANCEL tooltip; the same dynamic help was absent from `accessibleDescription`.
- Product commit: `6543d82199f8f5360cc205f6303dc133f9468dd7`
- Focused regression commit: `f823fe99c9c7ce78b3d0d70aaf257966ae692364`
- Acceptance: mirror the existing truthful per-state action help into `accessibleDescription` without changing enabled/disabled state, lifecycle transitions, receipts, scheduler/worker/storage or backend semantics.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
