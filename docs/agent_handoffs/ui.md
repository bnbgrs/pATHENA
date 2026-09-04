# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@c91e76804e74595f92c8eb624ce7c5d83b66bad2`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `47ffcfd68bffb93026042b4133410f8c915560b9`, parents `98700b0c657ba8cc488d0d9698b54fd6bce18718` + `c91e76804e74595f92c8eb624ce7c5d83b66bad2`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0015 — unsaved selected-model defaults freshness

Status: `FIXED / INTEGRATOR_READY`, P2.

Verified implementation:

- product `e175de079fd30dc2fb1bc3c64065ebd40127cd0b` changes only the presentation freshness for `<model> · defaults not yet saved` from `fresh` to fail-closed `unavailable`;
- focused test `0b0303e89c4fd358291e0fb180062212debdeff7` uses a real selected-model snapshot with an empty QSettings store and verifies unchanged visible copy, `idle`, `unavailable`, and synchronized accessibility;
- exact UI head `be55343dcaab9eb2afe80fe869000c139e6e2de1` passed ATHENA Quality Gate `33902213148` with conclusion `success`;
- no QSettings format/write path, model control, provider, Core, storage, network or security semantics changed.

## UI-GAP-0016 — unreadable local settings presentation

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Candidate:

- evidence: `_read_model()` used the opaque provider `backend_model_id` in the visible `local settings unreadable` error while all adjacent persistence states use the selected model `display_name`;
- product `b0bac270a461afdef3322550e6ddf3e49314653a` passes the selected display name into `_read_model()` for presentation only and keeps `backend_model_id` as the storage-group and persisted identity key;
- focused test `5d819895dfbfecc6c7a24f46251d0e3a07791409` deliberately separates `backend_model_id=qwen-local-backend-id` from `display_name=Local Qwen`, simulates QSettings AccessError, and verifies the visible/accessibility error uses only `Local Qwen`, remains `error`, and fails closed to `unavailable`;
- no storage lookup, persistence representation, provider behavior, backend contract, network or security semantics changed;
- local checkout remains blocked by transient DNS resolution of github.com; no local PASS is claimed.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Develop changes consumed by synchronization were limited to current Integrator/progress Research formula-identity files and are disjoint from the Settings product/test slice.
- Core owns Search/Research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Error worker currently tracks `ERR-0009`; historical `ERR-0004` remains closed unless its exact signature recurs.

## Integrator handoff

- READY: UI-GAP-0015 bounded lineage `e175de079fd30dc2fb1bc3c64065ebd40127cd0b` -> `0b0303e89c4fd358291e0fb180062212debdeff7`, backed by exact green UI head `be55343dcaab9eb2afe80fe869000c139e6e2de1` / Quality `33902213148`.
- NOT READY: UI-GAP-0016 until canonical Quality succeeds on the exact final documented UI head containing product `b0bac270a461afdef3322550e6ddf3e49314653a` and focused test `5d819895dfbfecc6c7a24f46251d0e3a07791409`.

## Next UI step

Consume canonical Quality for the exact final UI-GAP-0016 head. If green, mark UI-GAP-0016 `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, hand the bounded product/test lineage to Integrator, then select the next highest evidence-backed Settings interaction/accessibility gap. Until the original reference images are directly available, make no screenshot-level `MATCH` claim.
