# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@c5a255fe45b6c6984cb66f1251c0a9f8eb0c7f0c`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `29c9aae29f07810df57316f06d1c40a415820bfc`, parents `45e2b84d14bfc11b4878d9b945065063fdc40e6d` + `c5a255fe45b6c6984cb66f1251c0a9f8eb0c7f0c`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0011 — pre-first-snapshot fail-closed Settings state

Status: `FIXED / INTEGRATOR_READY`, P1.

Verified implementation:

- product `44ae9513ec5b77586d98a45c02afe0fe171af932` initializes Provider and Local Core through the existing `_set_state()` path with non-success `idle` UI state and `pathenaRuntimeFreshness=unavailable` while preserving the visible awaiting copy;
- Local Core additionally sets `pathenaNetworkScope=unavailable`, `pathenaInternetStateInferred=False`, and self-contained tooltip/accessibility copy stating that Internet access is not inferred before a Core snapshot;
- focused test `b307a771860c455b1630c2885ca1295e08a900d0` asserts those properties before any snapshot signal;
- exact documented UI head `45e2b84d14bfc11b4878d9b945065063fdc40e6d` passed ATHENA Quality Gate `33874283635` with conclusion `success`;
- no Core/provider/backend/network/storage/security behavior or capability changed.

## UI-GAP-0012 — initial persistence-state freshness metadata

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Evidence: the visible initial `Per-model settings · not saved yet` indicator had no explicit `pathenaUiState` or `pathenaRuntimeFreshness` until a later hydrate/save transition, unlike the rest of the Settings runtime-state surface.

Current candidate:

- product `d9797b5ff665b2c94ad7a9c34a6843d06f7cda4d` initializes that existing label through `_set_state()` as `idle` with `pathenaRuntimeFreshness=unavailable`, preserving its visible copy;
- focused test `5c9b49773ea16dfa6db341da37ab33d12f9ee7c5` asserts the initial persistence state before model hydration or save;
- no persistence implementation, storage format, provider behavior, backend contract or security semantics changed.

Canonical Quality must complete successfully on the exact final documented worker head before UI-GAP-0012 is promoted to `FIXED` or handed to Integrator.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Core owns Search/research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Error worker should allocate new ERR identities only from exact current-lineage failures; historical `ERR-0004` remains closed unless its signature recurs.

## Integrator handoff

- READY: UI-GAP-0011 product `44ae9513ec5b77586d98a45c02afe0fe171af932` + focused test `b307a771860c455b1630c2885ca1295e08a900d0`, backed by exact green UI head `45e2b84d14bfc11b4878d9b945065063fdc40e6d` / Quality `33874283635`.
- NOT READY: UI-GAP-0012 until canonical Quality on the exact final UI candidate succeeds.

## Next UI step

Consume exact-head canonical Quality for UI-GAP-0012. If green, mark UI-GAP-0012 `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, hand the bounded product/test lineage to Integrator, then select the next highest evidence-backed Settings/privacy/model-state UI gap without claiming screenshot parity.
