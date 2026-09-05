# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@f9938b0f3c3a016b1cc7837441caaec72974e1cf`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `fd7c215ec3da63524ab5f6977ecc281a5aca1a82`, with parents `9ca1cb04031d618bd6d34d2df4a46d331d110a82` + `f9938b0f3c3a016b1cc7837441caaec72974e1cf`; Develop delta was limited to current Integrator/progress plus local HTTP product/test files and was disjoint from the Settings product slice.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0020 — preserve known provider identity during model-list failure

Status: `FIXED / INTEGRATOR_READY`, P2.

Evidence and implementation:

- `DesktopApiController._model_snapshot()` can return a valid provider-health object together with a model-list error; aggregate `resolved_model_freshness` then becomes non-fresh even though provider identity/status is still present.
- `SettingsRuntimeController.apply_snapshot()` previously collapsed any aggregate unavailable model freshness to `Model provider · unavailable`, discarding the provider identity supplied by the snapshot.
- product `64b9956601f2ec21ee3624d27323221dc2aba10c` keeps true provider absence as `Model provider · unavailable`, but renders a present provider conservatively as `<provider> · last known <status>` whenever aggregate model freshness is not fresh; the state remains non-success and retains the existing aggregate freshness.
- focused test `7b4569dd55c93cb19b5dfe2d53ea0c2ccc34fe71` constructs a real `DesktopApiSnapshot` with `provider=LM Studio/ready`, `model_error=ATHENA model list refresh failed.`, and `model_freshness=unavailable`; it verifies provider identity, idle/unavailable metadata, synchronized accessibility, and preservation of the model error as error/unavailable detail.
- Exact documented UI head `9ca1cb04031d618bd6d34d2df4a46d331d110a82` passed ATHENA Quality Gate `33942660590` with conclusion `success`.
- Provider/backend/storage/network/security semantics were not changed.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Current Develop Integrator/progress and local HTTP product/test changes were incorporated through the non-force synchronization merge and are disjoint from the Settings slice.
- Core/Backend own snapshot collection, transport, provider and model semantics. UI-GAP-0020 does not introduce a new provider-freshness contract; it only avoids presenting a present provider as absent.
- Historical `ERR-0004` remains closed unless its exact signature recurs.

## Integrator handoff

- UI-GAP-0020 is READY for independent review/import on bounded lineage `64b9956601f2ec21ee3624d27323221dc2aba10c` -> `7b4569dd55c93cb19b5dfe2d53ea0c2ccc34fe71`, backed by exact green descendant `9ca1cb04031d618bd6d34d2df4a46d331d110a82` / Quality `33942660590`.
- The subsequent synchronization merge `fd7c215ec3da63524ab5f6977ecc281a5aca1a82` carries only disjoint current-Develop changes in addition to the verified UI lineage.
- Screen 07 returns to `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` is claimed.

## Next UI step

Inspect the synchronized Settings runtime for the next concrete presentation/accessibility inconsistency. A current candidate is the Core connection-failure detail path: an empty/whitespace failure message would render an empty `settingsRuntimeDetail` despite the explicit error/unavailable state. Confirm the exact signal/runtime path before assigning the next stable UI-GAP id; if confirmed, add a self-describing presentation-only fallback plus focused Qt coverage without changing Core/network semantics, then run canonical Quality on the exact candidate.
