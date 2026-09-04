# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `c3c8a6f908b65bbfa4df88c366a901ccc7439e4f`, parents `f66a1cc2c80cf0cadc89ba1a4771345af79df934` + `33c4a9657bb9aca24c6e85c0a2b4a7c0132c3358`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0016 — unreadable local settings presentation

Status: `FIXED / INTEGRATOR_READY`, P2.

Verified implementation:

- product `b0bac270a461afdef3322550e6ddf3e49314653a` uses selected-model `display_name` for the visible unreadable-settings error while retaining `backend_model_id` solely as the storage identity;
- focused test `5d819895dfbfecc6c7a24f46251d0e3a07791409` separates backend identity from display name, simulates QSettings AccessError, and verifies `error/unavailable` fail-closed presentation with synchronized accessibility;
- exact UI head `f66a1cc2c80cf0cadc89ba1a4771345af79df934` passed ATHENA Quality Gate `33912482820` with conclusion `success`;
- no QSettings format, lookup semantics, persistence representation, provider, backend, network or security behavior changed.

## UI-GAP-0017 — fresh non-ready provider detail semantic state

Status: `IMPLEMENTED_PENDING_VERIFY`, P2.

Candidate:

- evidence: for a fresh snapshot with a provider status other than `ready`, `settingsProviderState` already carries `pathenaUiState=error` while the provider-supplied `settingsRuntimeDetail` remained `idle` whenever `model_error` was absent;
- product `a0c8ea842e6dfb4c029b7a722eeb4b43189941e5` aligns only the detail presentation state with the already-established fresh non-ready provider error state;
- focused test `f668520bef1d2789b70cb7561b8e0f5dd4fd6041` uses a fresh `LM Studio · error` snapshot with provider detail and verifies provider/detail both report `error`, retain `fresh`, and keep accessibility synchronized;
- ready, stale, explicit model-error, connection, persistence, provider contract, backend, storage, network and security semantics are unchanged;
- local checkout remains blocked by transient DNS resolution of github.com; no local PASS is claimed.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Develop changes consumed in the synchronization were current Integrator/progress plus Storage Health product/test files and were disjoint from the Settings product/test slice.
- Core owns Search/Research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Historical `ERR-0004` remains closed unless its exact signature recurs.

## Integrator handoff

- READY: UI-GAP-0016 bounded lineage `b0bac270a461afdef3322550e6ddf3e49314653a` -> `5d819895dfbfecc6c7a24f46251d0e3a07791409`, backed by exact green UI head `f66a1cc2c80cf0cadc89ba1a4771345af79df934` / Quality `33912482820`.
- NOT READY: UI-GAP-0017 until canonical Quality succeeds on the exact final documented UI head containing product `a0c8ea842e6dfb4c029b7a722eeb4b43189941e5` and focused test `f668520bef1d2789b70cb7561b8e0f5dd4fd6041`.

## Next UI step

Consume canonical Quality for the exact final UI-GAP-0017 head. If green, mark UI-GAP-0017 `FIXED`, return Screen 07 to `IMPLEMENTED_PENDING_VISUAL_REVIEW`, hand the bounded product/test lineage to Integrator, then select the next highest evidence-backed UI interaction/accessibility gap. Until the original reference images are directly available, make no screenshot-level `MATCH` claim.
