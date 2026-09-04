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

- product lineage culminates at `e1218685577230fa6ad190291ad0f626912853ac`; `Per-model settings · choose a model` uses `pathenaRuntimeFreshness=unavailable` when `_selected_model()` returns `None`;
- focused test `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24` asserts unchanged visible copy, `idle`, `unavailable`, and synchronized accessibility;
- exact final documented UI head `3d3ac638ce35c2bd149cea2358ef726f243244f0` passed ATHENA Quality Gate `33897120327` with conclusion `success`;
- no persistence implementation, storage format, provider behavior, backend contract or security semantics changed.

## UI-GAP-0015 — unsaved selected-model defaults freshness

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Candidate:

- product `e175de079fd30dc2fb1bc3c64065ebd40127cd0b` changes only the presentation freshness for `<model> · defaults not yet saved` from `fresh` to fail-closed `unavailable`; visible copy, idle state and persistence behavior are unchanged;
- focused test `0b0303e89c4fd358291e0fb180062212debdeff7` applies a real one-model snapshot with an empty QSettings store and asserts the unchanged visible copy, `idle`, `unavailable`, and synchronized accessible description;
- no QSettings format/write path, model control, provider, Core, storage, network or security semantics changed;
- local checkout/test execution remains blocked by DNS resolution of github.com, so no local PASS is claimed; canonical Quality on the exact final documented head is required.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Core owns Search/research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Error worker should allocate new ERR identities only from exact current-lineage failures; historical `ERR-0004` remains closed unless its signature recurs.

## Integrator handoff

- READY: UI-GAP-0014 bounded product/test lineage culminating at product normalization `e1218685577230fa6ad190291ad0f626912853ac` plus focused test `ce7ae251f5d7b8548a21abde6c67cbd2fafa9f24`, backed by exact green UI head `3d3ac638ce35c2bd149cea2358ef726f243244f0` / Quality `33897120327`.
- NOT READY: UI-GAP-0015 until canonical Quality succeeds on the exact final documented UI head containing product `e175de079fd30dc2fb1bc3c64065ebd40127cd0b` and focused test `0b0303e89c4fd358291e0fb180062212debdeff7`.

## Next UI step

Consume canonical Quality for the exact final UI-GAP-0015 head. If green, mark UI-GAP-0015 `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, hand the bounded product/test lineage to Integrator, then select the next highest evidence-backed UI interaction/accessibility gap. Until the original reference images are directly available, make no screenshot-level `MATCH` claim.
