# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@3ea908affd23f1d80e0b863a6af8cf366e2b8484`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `81d590c7653a7f62c623c0908981a2d99d466786`, parents `acd4bcbeb68d9578fef53b223ef98f8ee2c6f43e` + `3ea908affd23f1d80e0b863a6af8cf366e2b8484`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0010 — immediate fresh-snapshot accessibility boundary

Status: `FIXED / INTEGRATOR_READY`, P1.

Verified implementation:

- product `0722d780b94d8d297bd89e417ae09fab08cb4dcf` makes the runtime snapshot itself set `pathenaNetworkScope=loopback-only`, `pathenaInternetStateInferred=False`, and self-contained accessibility/tooltip copy stating that Local Core status does not indicate Internet access;
- focused test `a2d7030101a01415af99b5a8cba31ad10550e5de` asserts those semantics immediately after `_apply(...)`, before `comprehension.sync()`;
- exact documented UI head `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` passed ATHENA Quality Gate `33864721817` with conclusion `success`;
- no backend/network/security semantics, quality rules, assertions, provider commands or fake runtime capabilities changed.

## UI-GAP-0011 — pre-first-snapshot fail-closed Settings state

Status: `IMPLEMENTED_PENDING_VERIFY`, P1.

Evidence: prior to the first Core snapshot, visible Settings labels said `Model provider · awaiting Core` and `Local Core · awaiting connection`, but did not carry the explicit state/freshness/network-scope/Internet-inference metadata used after runtime transitions.

Current candidate:

- product `44ae9513ec5b77586d98a45c02afe0fe171af932` initializes Provider and Local Core through the existing `_set_state()` path with non-success `idle` UI state and `pathenaRuntimeFreshness=unavailable` while preserving the visible awaiting copy;
- the Local Core initial state additionally sets `pathenaNetworkScope=unavailable`, `pathenaInternetStateInferred=False`, and self-contained tooltip/accessibility copy stating that Internet access is not inferred before a Core snapshot;
- focused test `b307a771860c455b1630c2885ca1295e08a900d0` asserts those properties immediately after `install_settings_runtime(...)`, before any snapshot signal;
- no Core/provider/backend/network/storage/security behavior or capability is added or changed.

Canonical Quality must complete successfully on the exact final documented worker head before this gap is promoted to `FIXED` or handed to Integrator.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Core owns Search/research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb this presentation-only state contract.
- Error worker should treat any new canonical failure by exact signature; historical `ERR-0004` remains closed unless it recurs.

## Integrator handoff

- READY: UI-GAP-0010 product `0722d780b94d8d297bd89e417ae09fab08cb4dcf` + focused test `a2d7030101a01415af99b5a8cba31ad10550e5de`, backed by exact green UI head `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` / Quality `33864721817`.
- NOT READY: UI-GAP-0011 until canonical Quality on the exact final UI candidate succeeds.

## Next UI step

Consume the exact-head canonical Quality result for UI-GAP-0011. If green, mark UI-GAP-0011 `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, version the Integrator-ready product/test lineage, then select the next highest evidence-backed Settings/privacy/model-state UI gap without claiming screenshot parity.
