# pATHENA Visual Gap Ledger

Baseline: `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`
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
- Acceptance: transient missing binding is an unhandled/no-op lifecycle state; existing ChildAdded resynchronization, action ordering, disabled-state preservation and composer return target remain unchanged.

## UI-GAP-0004 — Icon-only global rail does not expose human page names to assistive technology

- Category: `ACCESSIBILITY`
- Screen: `01 — Workspace / Chat` and global navigation shared by all screens
- Severity: `P1`
- Evidence: rail `QListWidgetItem` visible text intentionally remains symbol glyphs while the existing tooltips contain the real human page names.
- Product commit: `319a0d7660bf7dc03e1a6c3550efd0e15b76e94b`
- Focused test commit: `19924adc2881b3eff06a6c4c343abba7e635ecbc`
- Status: `FIXED`
- Verification evidence: exact UI head `4d128a864ecbb9463e54273d7f0d527910384591` passed ATHENA Quality Gate `34270643737`; the run includes the rail accessibility product/test lineage.
- Integration evidence: Integrator transplanted only the rail product/test blobs onto Develop as `bf25017d37e88438a9644445b9f5da47c11098d0`, then recorded the bounded integration in `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6`.
- Acceptance: visible glyphs, tooltips, page routing, geometry and page identity remain unchanged; existing human tooltip text is exposed via `Qt.ItemDataRole.AccessibleTextRole`.

## UI-GAP-0005 — Quiet message-action controller can dereference a transiently absent document during Qt lifecycle churn

- Category: `INTERACTION`
- Screen: `08 — PALLAS` / shared chat-message action lifecycle
- Severity: `P1`
- Evidence: canonical Quality `34264917412` failed exactly at `tests/unit/test_pathena_pallas_full_view.py::test_open_workspace_reuses_one_synchronized_full_surface` through `MessageActionQuietController.eventFilter()` because `document` was transiently absent.
- Product fix commit: `4d128a864ecbb9463e54273d7f0d527910384591`
- Status: `FIXED_VERIFIED_PENDING_INTEGRATION`
- Verification evidence: exact UI head `4d128a864ecbb9463e54273d7f0d527910384591` passed ATHENA Quality Gate `34270643737` with conclusion `success`.
- Current synchronization: NON-FORCE two-parent merge `fc174c80f03c54fb23a68d18a281f5b4c80bacbf` carries the verified quiet-action blob on current Develop `cdc9e8e0064db659f9eabbfdb5f3720a76114fd6` without importing unrelated worker tree state.
- Acceptance: a temporarily unavailable document binding is a no-op lifecycle state; action visibility, opacity policy, callbacks, focus behavior, layout and backend/runtime semantics remain unchanged.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
