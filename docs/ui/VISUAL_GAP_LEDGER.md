# pATHENA Visual Gap Ledger

Baseline: `a7c1d8cd1530a3003690292a9bf4c660472d59ce`
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

## UI-GAP-0008 — Local Core readiness could be mistaken for Internet-access state

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P1`
- Status: `FIXED`
- Product commit: `9dd1836154a190fdcb9f9a690b46035f9dcacda6`
- Focused test lineage culminates at exact UI head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- Verification evidence: ATHENA Quality Gate `33854660676` completed `success` on exact UI head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- Acceptance: the Settings `Local Core` indicator explicitly represents local loopback Core readiness only, sets `pathenaInternetStateInferred=False`, and never claims Internet reachability from Core/provider readiness.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0009 — Core connection failure can retain stale loopback-only presentation metadata

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P1`
- Status: `FIXED`
- Evidence: `SettingsRuntimeController.apply_snapshot()` assigns `pathenaNetworkScope=loopback-only` and a connected-state tooltip, while the previous `apply_connection_failure()` changed visible text/state to unavailable without clearing that scope/tooltip. A ready→connection-failure transition could therefore retain stale connected metadata on the visible Settings connection indicator.
- Product commit: `ad416f76cd52eadd42aa7f2b09a96ce43bf737c7`.
- Focused test commit: `d7e85654db03eb21da35a5fa06d3bdf94cb4a1a5`.
- Acceptance: connection failure sets `pathenaNetworkScope=unavailable`, keeps `pathenaInternetStateInferred=False`, replaces stale tooltip/accessibility text, and preserves unavailable/error freshness semantics. No backend/network capability is added.
- Verification evidence: exact documented UI head `6d6869d4927a52e98158238f396b8d5855b771b9` passed ATHENA Quality Gate `33860150646` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0010 — Fresh Core snapshot accessibility depended on delayed comprehension sync

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P1`
- Status: `FIXED`
- Evidence: `SettingsRuntimeController.apply_snapshot()` previously left the immediate accessible description at the generic visible text (`Local Core · connected`) and did not directly set `pathenaInternetStateInferred=False`; the separate `SettingsComprehensionController` corrected that metadata only on its own sync/timer cycle.
- Product commit: `0722d780b94d8d297bd89e417ae09fab08cb4dcf`.
- Focused test commit: `a2d7030101a01415af99b5a8cba31ad10550e5de`.
- Acceptance: every fresh Core snapshot immediately carries self-contained local-loopback accessibility text, `pathenaNetworkScope=loopback-only`, and `pathenaInternetStateInferred=False` before any later comprehension sync. Backend/network/security semantics remain unchanged.
- Verification evidence: exact documented UI head `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` passed ATHENA Quality Gate `33864721817` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
