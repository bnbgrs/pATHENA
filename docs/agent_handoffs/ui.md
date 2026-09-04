# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@2520224ebe3143368b3e5f13c091479d5e7b8d35`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `0328405eb0c8db793e78f83885b4eda4235e4a23`, parents `3d3ac638ce35c2bd149cea2358ef726f243244f0` + `2520224ebe3143368b3e5f13c091479d5e7b8d35`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0014 — no-model persistence freshness

Status: `FIXED / INTEGRATOR_READY`, P2.

Verified implementation:

- product lineage culminates at `e1218685577230fa6ad190291ad0f626912853ac`; `Per-model settings · choose a model` uses `pathenaRuntimeFreshness=unavailable` instead of `fresh` when `_selected_model()` returns `None`;
- focused test `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24` clears the real model selector and asserts unchanged visible copy, `idle`, `unavailable`, and synchronized accessible description;
- exact final documented UI head `3d3ac638ce35c2bd149cea2358ef726f243244f0` passed ATHENA Quality Gate `33897120327` with conclusion `success`;
- no persistence implementation, storage format, provider behavior, backend contract or security semantics changed.

## UI-GAP-0015 — unsaved selected-model defaults freshness

Status: `OPEN`, P2.

Evidence:

- `SettingsRuntimeController.hydrate_selected_model()` renders `<model> · defaults not yet saved` when a real model is selected but no local persisted record exists;
- that state is `idle` but currently carries `pathenaRuntimeFreshness=fresh`, despite the visible copy explicitly stating that no model-specific settings have been saved;
- the next bounded correction is presentation-only: retain the copy and idle state, fail closed to `unavailable`, keep accessibility synchronized, and add focused Qt coverage using a selected model plus empty QSettings store.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Core owns Search/research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Error worker should allocate new ERR identities only from exact current-lineage failures; historical `ERR-0004` remains closed unless its signature recurs.

## Integrator handoff

- READY: UI-GAP-0014 bounded product/test lineage culminating at product normalization `e1218685577230fa6ad190291ad0f626912853ac` plus focused test `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24`, backed by exact green UI head `3d3ac638ce35c2bd149cea2358ef726f243244f0` / Quality `33897120327`.
- The worker has been NON-FORCE synchronized with current Develop through `0328405eb0c8db793e78f83885b4eda4235e4a23`.
- UI-GAP-0015 is not ready and has no product mutation yet.

## Next UI step

Implement UI-GAP-0015 in `src/athena/desktop/pathena_settings_runtime.py`, add focused Qt coverage for a selected model with an empty settings store, run canonical Quality on the exact candidate, and only then promote it to Integrator-ready. Until the original reference images are directly available, keep Screen 07 at `IMPLEMENTED_PENDING_VISUAL_REVIEW` and make no screenshot-level `MATCH` claim.
