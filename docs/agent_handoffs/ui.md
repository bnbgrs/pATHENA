# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@0b7f428f8679db9391c00b4b9638d85550332c43`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `eeb9c8816a81495769c83d0acb51646f44bed6a3`, parents `622f85338613b7d59ef5b1bd0fd05eae3d488c47` + `0b7f428f8679db9391c00b4b9638d85550332c43`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0013 — runtime detail freshness/accessibility transitions

Status: `FIXED / INTEGRATOR_READY`, P2.

Verified implementation:

- product `046414551ad85bc418af0c7bdfdc2d8be7befd7d` initializes `settingsRuntimeDetail` as `idle/unavailable`, routes snapshot-backed detail through `_set_state()` using the snapshot's resolved model freshness, keeps model-error detail explicitly `error`, and makes Core connection failure `error/unavailable` with synchronized accessible description;
- focused test `7de1ccb040083375fb31242f54b9515b18403113` asserts initial, fresh, stale, unavailable and connection-failure transitions without changing visible copy or runtime/provider behavior;
- exact final UI head `622f85338613b7d59ef5b1bd0fd05eae3d488c47` passed ATHENA Quality Gate `33891068183` with conclusion `success`.

## UI-GAP-0014 — no-model persistence freshness

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Implementation:

- product lineage culminates at `e1218685577230fa6ad190291ad0f626912853ac`; the cumulative product diff against synchronized baseline is exactly one semantic line: `Per-model settings · choose a model` now uses `pathenaRuntimeFreshness=unavailable` instead of `fresh` when `_selected_model()` returns `None`;
- focused test `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24` clears the real model selector, calls `hydrate_selected_model()`, and asserts unchanged visible copy, `idle`, `unavailable`, and synchronized accessible description;
- no persistence implementation, storage format, provider behavior, backend contract or security semantics changed;
- exact-head canonical Quality is required before Integrator promotion.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Core owns Search/research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Error worker should allocate new ERR identities only from exact current-lineage failures; historical `ERR-0004` remains closed unless its signature recurs.

## Integrator handoff

- READY: UI-GAP-0013 product `046414551ad85bc418af0c7bdfdc2d8be7befd7d` + focused test `7de1ccb040083375fb31242f54b9515b18403113`, backed by exact green UI head `622f85338613b7d59ef5b1bd0fd05eae3d488c47` / Quality `33891068183`.
- NOT READY: UI-GAP-0014 until canonical Quality on the final documented exact worker head succeeds.

## Next UI step

Consume canonical Quality for the final documented UI-GAP-0014 candidate. If green, mark UI-GAP-0014 `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, hand the bounded product/test lineage to Integrator, then select the next highest evidence-backed Settings interaction/accessibility gap without claiming screenshot parity.
