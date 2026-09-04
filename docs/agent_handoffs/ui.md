# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@14adeb8949f680dc16a3067e586b3950132e0375`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `5ba20b04136ee3e843f388b4aa40dec0143c974c`, parents `3a1be68c48dab4176e9258170147cf127c4b3d2a` + `14adeb8949f680dc16a3067e586b3950132e0375`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0012 — initial persistence-state freshness metadata

Status: `FIXED / INTEGRATOR_READY`, P2.

Verified implementation:

- product `d9797b5ff665b2c94ad7a9c34a6843d06f7cda4d` initializes the existing `Per-model settings · not saved yet` label through `_set_state()` as `idle` with `pathenaRuntimeFreshness=unavailable`, preserving visible copy;
- focused test `5c9b49773ea16dfa6db341da37ab33d12f9ee7c5` asserts the initial persistence state before model hydration or save;
- exact UI head `3a1be68c48dab4176e9258170147cf127c4b3d2a` passed ATHENA Quality Gate `33879947654` with conclusion `success`;
- no persistence implementation, storage format, provider behavior, backend contract or security semantics changed.

## UI-GAP-0013 — runtime detail freshness/accessibility transitions

Status: `OPEN`, P2.

Evidence: `settingsRuntimeDetail` changes between initial explanatory copy, snapshot-backed provider detail/model error, and connection-failure error text, but unlike the adjacent runtime indicators it does not consistently carry `pathenaRuntimeFreshness` or transition its accessible description. After `apply_connection_failure()` only `pathenaUiState=error` is set.

Acceptance: preserve all visible copy and real runtime behavior while making the detail label fail-closed and self-describing across initial, fresh/stale/unavailable snapshot, and connection-failure states. Add focused Qt coverage and require canonical Quality on the exact candidate.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Core owns Search/research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Error worker should allocate new ERR identities only from exact current-lineage failures; historical `ERR-0004` remains closed unless its signature recurs.

## Integrator handoff

- READY: UI-GAP-0012 product `d9797b5ff665b2c94ad7a9c34a6843d06f7cda4d` + focused test `5c9b49773ea16dfa6db341da37ab33d12f9ee7c5`, backed by exact green UI head `3a1be68c48dab4176e9258170147cf127c4b3d2a` / Quality `33879947654`.
- UI-GAP-0011 remains READY through exact green head `45e2b84d14bfc11b4878d9b945065063fdc40e6d` / Quality `33874283635`.
- NOT READY: UI-GAP-0013 until implementation, focused tests, and exact canonical Quality succeed.

## Next UI step

Implement UI-GAP-0013 minimally in `src/athena/desktop/pathena_settings_runtime.py`, add focused coverage in `tests/unit/test_pathena_settings_runtime.py`, then start/evaluate canonical Quality on the exact candidate. Screen 07 remains `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot parity is claimed.
