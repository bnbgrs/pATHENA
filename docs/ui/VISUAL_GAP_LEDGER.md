# pATHENA Visual Gap Ledger

Baseline: `2520224ebe3143368b3e5f13c091479d5e7b8d35`
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

## UI-GAP-0011 — Pre-first-snapshot Settings runtime state lacks explicit fail-closed metadata

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P1`
- Status: `FIXED`
- Evidence: `SettingsRuntimeController.__init__()` created visible `Model provider · awaiting Core` and `Local Core · awaiting connection` labels without the explicit fail-closed state metadata used by later snapshot/failure transitions.
- Product commit: `44ae9513ec5b77586d98a45c02afe0fe171af932`.
- Focused test commit: `b307a771860c455b1630c2885ca1295e08a900d0`.
- Acceptance: before any snapshot, provider/Core labels expose explicit non-success `idle` UI state with `pathenaRuntimeFreshness=unavailable`; Local Core exposes `pathenaNetworkScope=unavailable`, `pathenaInternetStateInferred=False`, and self-contained accessibility text stating that Internet access is not inferred. Existing visible awaiting copy remains unchanged; no backend/network/security/provider behavior changes.
- Verification evidence: exact final documented candidate `45e2b84d14bfc11b4878d9b945065063fdc40e6d` passed ATHENA Quality Gate `33874283635` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0012 — Initial Settings persistence state lacked explicit non-success freshness metadata

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P2`
- Status: `FIXED`
- Evidence: before a model is selected, hydrated or saved, `Per-model settings · not saved yet` was visible but did not carry the same explicit `pathenaUiState` / `pathenaRuntimeFreshness` contract used by later persistence transitions.
- Product commit: `d9797b5ff665b2c94ad7a9c34a6843d06f7cda4d`.
- Focused test commit: `5c9b49773ea16dfa6db341da37ab33d12f9ee7c5`.
- Acceptance: the initial persistence indicator keeps its existing copy but starts as `pathenaUiState=idle` and `pathenaRuntimeFreshness=unavailable`, preventing an untyped initial state from being mistaken for fresh/successful persistence. No storage/persistence behavior changes.
- Verification evidence: exact UI head `3a1be68c48dab4176e9258170147cf127c4b3d2a` passed ATHENA Quality Gate `33879947654` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0013 — Runtime detail state lacks explicit freshness/accessibility transition metadata

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P2`
- Status: `FIXED`
- Evidence: `settingsRuntimeDetail` changes between initial explanatory copy, snapshot-backed provider detail/model error, and connection-failure error text, but unlike the adjacent Provider/Connection/Persistence indicators it did not consistently carry `pathenaRuntimeFreshness` or transition its accessible description through the same state changes.
- Product commit: `046414551ad85bc418af0c7bdfdc2d8be7befd7d`.
- Focused test commit: `7de1ccb040083375fb31242f54b9515b18403113`.
- Acceptance: existing visible detail copy is preserved; initial state is `idle/unavailable`; snapshot transitions use the snapshot's resolved model freshness and synchronize the accessible description to the displayed detail; model errors are explicit `error`; Core connection failure is `error/unavailable` and self-describing. No backend/network/provider capability is invented.
- Verification evidence: exact final UI head `622f85338613b7d59ef5b1bd0fd05eae3d488c47` passed ATHENA Quality Gate `33891068183` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0014 — No-model persistence state incorrectly claims fresh model persistence

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P2`
- Status: `FIXED`
- Evidence: `SettingsRuntimeController.hydrate_selected_model()` rendered `Per-model settings · choose a model` with `pathenaRuntimeFreshness=fresh` when `_selected_model()` returned `None`, even though no model-specific persistence fact exists in that state.
- Product lineage culminates at: `e1218685577230fa6ad190291ad0f626912853ac`.
- Focused test commit: `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24`.
- Acceptance: when no model is selected, the existing visible copy remains unchanged, UI state remains `idle`, freshness fails closed to `unavailable`, and the accessible description remains synchronized to the visible state. No persistence/storage/backend semantics change.
- Verification evidence: exact final documented UI head `3d3ac638ce35c2bd149cea2358ef726f243244f0` passed ATHENA Quality Gate `33897120327` with conclusion `success`.
- Visual status: `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` claim.

## UI-GAP-0015 — Unsaved per-model defaults incorrectly present persistence freshness as fresh

- Category: `STATE / ACCESSIBILITY`
- Screen: `07 — Settings`
- Severity: `P2`
- Status: `IMPLEMENTED_PENDING_VERIFY`
- Evidence: in `SettingsRuntimeController.hydrate_selected_model()`, a selected model with no persisted local record rendered `<model> · defaults not yet saved` with `pathenaUiState=idle` but `pathenaRuntimeFreshness=fresh`. The visible copy explicitly says there is no saved model-specific persistence fact, so `fresh` overstated the persistence state.
- Product commit: `e175de079fd30dc2fb1bc3c64065ebd40127cd0b`.
- Focused test commit: `0b0303e89c4fd358291e0fb180062212debdeff7`.
- Acceptance: existing visible copy and idle state remain unchanged; freshness fails closed to `unavailable`; accessible description remains synchronized. QSettings storage, model controls, provider behavior and backend semantics are unchanged.
- Verification required: canonical Quality on the final documented exact candidate head before promotion to `FIXED`.

## Evidence blocker

`VISUAL_REFERENCE_PENDING`: until an original reference image and a real rendered current build can both be opened and inspected, spacing, exact proportions, pixel colors and screenshot-level `MATCH` claims remain prohibited.
