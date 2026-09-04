# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@f886a63ea190cb8d8df202bfd6528a6ef22df317`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `47c3491d0b17c7e57786a952d41c243054a51d20`, parents `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` + `f886a63ea190cb8d8df202bfd6528a6ef22df317`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0008 — Settings Local Core vs Internet state

Status: `FIXED / INTEGRATOR_READY`, P1.

The Settings Local Core indicator now explicitly describes only the existing local loopback Core connection and never treats readiness as Internet-access evidence. It exposes `pathenaInternetStateInferred=False`; unknown scope fails closed.

- Product commit: `9dd1836154a190fdcb9f9a690b46035f9dcacda6`.
- Focused harness lineage culminates at exact verified UI head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- Canonical Quality: `33854660676 = success` on exact head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39`.
- Synchronization onto current Develop preserved the verified Settings product/test blobs unchanged in merge `47c3491d0b17c7e57786a952d41c243054a51d20`.

Integrator may independently review/import the bounded UI-GAP-0008 Settings lineage. This is technical state/accessibility evidence only; Screen 07 remains pending original visual review.

## UI-GAP-0009 — stale connection metadata after Core failure

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

Evidence: the existing `SettingsRuntimeController.apply_snapshot()` assigns `pathenaNetworkScope=loopback-only` and a connected-state tooltip. Previously `apply_connection_failure()` changed visible text to `Local Core · unavailable` but retained those connected metadata values across a ready→failure transition.

Candidate implementation:

- product `ad416f76cd52eadd42aa7f2b09a96ce43bf737c7` sets failure scope to `unavailable`, keeps `pathenaInternetStateInferred=False`, replaces stale tooltip/accessibility text and leaves runtime freshness/error state unavailable;
- focused test `d7e85654db03eb21da35a5fa06d3bdf94cb4a1a5` covers the real ready/provider-unavailable/Core-failure transition and asserts that no loopback metadata survives the Core failure;
- no backend command, network capability, Security/Storage behavior, provider action or test rule was changed.

Canonical Quality must pass on the final documented worker head before UI-GAP-0009 becomes `FIXED` or Integrator-ready.

## Collision / ownership guidance

- UI owns only the Settings presentation/accessibility state in this slice.
- Core owns Search/facade composition and must not infer Internet state from this UI metadata.
- Backend owns durable runtime/storage work and must not absorb this presentation-only gap.
- Error handoff currently has no open confirmed defect that requires UI mutation.

## Integrator handoff

- READY: UI-GAP-0008 product `9dd1836154a190fdcb9f9a690b46035f9dcacda6` with exact green UI head `afa319f0ab1b12edccc4b649d4a1ca36bcd7ac39` / Quality `33854660676`.
- NOT READY: UI-GAP-0009 until canonical Quality succeeds on the final current UI candidate containing `ad416f76cd52eadd42aa7f2b09a96ce43bf737c7` + `d7e85654db03eb21da35a5fa06d3bdf94cb4a1a5` and this handoff/ledger state.

## Next UI step

Consume the exact-head canonical Quality result for UI-GAP-0009. If green, mark it `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, hand the bounded product/test lineage to Integrator, then select the next highest evidence-backed Settings/privacy/model-state gap. If red, read and fix only the exact diagnostic without weakening assertions or quality rules.
