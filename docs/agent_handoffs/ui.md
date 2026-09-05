# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@d69fcc570bceac78536614f40b0ae3e1b867d791`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `c3d4c97743215378dc67f39b2cdbdd667f2c4955`, with parents `550943bd4515514ea9e87b863d1b16f22b60445a` + `d69fcc570bceac78536614f40b0ae3e1b867d791`; Develop delta was limited to current Integrator/progress plus local HTTP product/test files and was disjoint from the Settings product slice.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0020 — preserve known provider identity during model-list failure

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Evidence and implementation:

- `DesktopApiController._model_snapshot()` can return a valid provider-health object together with a model-list error; aggregate `resolved_model_freshness` then becomes non-fresh even though provider identity/status is still present.
- `SettingsRuntimeController.apply_snapshot()` previously collapsed any aggregate unavailable model freshness to `Model provider · unavailable`, discarding the provider identity supplied by the snapshot.
- product `64b9956601f2ec21ee3624d27323221dc2aba10c` now keeps true provider absence as `Model provider · unavailable`, but renders a present provider conservatively as `<provider> · last known <status>` whenever aggregate model freshness is not fresh; the state remains non-success and retains the existing aggregate freshness.
- focused test `7b4569dd55c93cb19b5dfe2d53ea0c2ccc34fe71` constructs a real `DesktopApiSnapshot` with `provider=LM Studio/ready`, `model_error=ATHENA model list refresh failed.`, and `model_freshness=unavailable`; it verifies provider identity, idle/unavailable metadata, synchronized accessibility, and preservation of the model error as error/unavailable detail.
- Provider/backend/storage/network/security semantics were not changed.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Current Develop Integrator/progress and local HTTP product/test changes were incorporated through the non-force synchronization merge and are disjoint from the Settings slice.
- Core/Backend own snapshot collection, transport, provider and model semantics. UI-GAP-0020 does not introduce a new provider-freshness contract; it only avoids presenting a present provider as absent.
- Historical `ERR-0004` remains closed unless its exact signature recurs.

## Integrator handoff

- UI-GAP-0019 remains independently READY on its previously exact-green bounded lineage.
- DO NOT INTEGRATE UI-GAP-0020 until a canonical Quality run succeeds on the exact documented product/test descendant.
- Screen 07 is `IMPLEMENTED_PENDING_VERIFY`; no screenshot-level `MATCH` is claimed.

## Next UI step

Consume exact-head canonical Quality for UI-GAP-0020. If green, promote UI-GAP-0020 to `FIXED / INTEGRATOR_READY`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, and hand bounded lineage `64b9956601f2ec21ee3624d27323221dc2aba10c` -> `7b4569dd55c93cb19b5dfe2d53ea0c2ccc34fe71` to Integrator. If red, read the exact diagnostic and minimally fix only the reported point before selecting another gap.