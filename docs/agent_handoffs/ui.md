# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@a0e0a2bcf76b0e7f77bb3cd15b8c2ccf79d5c600`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `186e85f40a29b25cd1daa26ccf654ee6b3b477c3`, parents `6d6869d4927a52e98158238f396b8d5855b771b9` + `a0e0a2bcf76b0e7f77bb3cd15b8c2ccf79d5c600`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0009 — stale connection metadata after Core failure

Status: `FIXED / INTEGRATOR_READY`, P1.

Evidence: the existing `SettingsRuntimeController.apply_snapshot()` assigns loopback presentation metadata. Previously `apply_connection_failure()` changed visible text to `Local Core · unavailable` but retained connected metadata across a ready→failure transition.

Verified implementation:

- product `ad416f76cd52eadd42aa7f2b09a96ce43bf737c7` sets failure scope to `unavailable`, keeps `pathenaInternetStateInferred=False`, replaces stale tooltip/accessibility text and leaves runtime freshness/error state unavailable;
- focused test `d7e85654db03eb21da35a5fa06d3bdf94cb4a1a5` covers the real ready/provider-unavailable/Core-failure transition and asserts that no loopback metadata survives the Core failure;
- exact documented UI head `6d6869d4927a52e98158238f396b8d5855b771b9` passed ATHENA Quality Gate `33860150646` with conclusion `success`;
- no backend command, network capability, Security/Storage behavior, provider action or test rule changed.

Integrator may independently review/import the bounded UI-GAP-0009 product/test lineage. This is technical state/accessibility evidence only; Screen 07 remains pending original visual review.

## UI-GAP-0010 — immediate fresh-snapshot accessibility boundary

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

Evidence: before this slice `SettingsRuntimeController.apply_snapshot()` set the immediate accessible description to the generic visible text and relied on the separate `SettingsComprehensionController` sync/timer to add the explicit local-loopback / no-Internet-inference boundary. That creates a short-lived accessibility-state mismatch after a fresh snapshot.

Candidate implementation:

- product `0722d780b94d8d297bd89e417ae09fab08cb4dcf` makes the runtime snapshot itself set `pathenaNetworkScope=loopback-only`, `pathenaInternetStateInferred=False`, and self-contained accessibility/tooltip copy stating that Local Core status does not indicate Internet access;
- focused test `a2d7030101a01415af99b5a8cba31ad10550e5de` asserts those semantics immediately after `_apply(...)`, before `comprehension.sync()` is called;
- the later comprehension sync remains compatible and still supplies the accessible name; no backend/network/security semantics changed.

Canonical Quality must pass on the final documented worker head before UI-GAP-0010 becomes `FIXED` or Integrator-ready.

## Collision / ownership guidance

- UI owns only the Settings presentation/accessibility state in these slices.
- Core owns Search/facade composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb this presentation-only state contract.
- Error worker should treat any new canonical failure by exact signature; historical `ERR-0004` remains closed unless it recurs.

## Integrator handoff

- READY: UI-GAP-0009 product `ad416f76cd52eadd42aa7f2b09a96ce43bf737c7` + focused test `d7e85654db03eb21da35a5fa06d3bdf94cb4a1a5`, backed by exact green UI head `6d6869d4927a52e98158238f396b8d5855b771b9` / Quality `33860150646`.
- NOT READY: UI-GAP-0010 until canonical Quality succeeds on the final current UI candidate containing `0722d780b94d8d297bd89e417ae09fab08cb4dcf` + `a2d7030101a01415af99b5a8cba31ad10550e5de` and this handoff/ledger/manifest state.

## Next UI step

Consume the exact-head canonical Quality result for UI-GAP-0010. If green, mark it `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, hand the bounded product/test lineage to Integrator, then select the next highest evidence-backed Settings/privacy/model-state gap. If red, read and fix only the exact diagnostic without weakening assertions or quality rules.
