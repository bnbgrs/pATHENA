# Error worker handoff

## Exact source of truth

- Develop: `5048e8f2e88c1ac0553d3052db48c9c3be22bff1`; canonical `34851187301 = SUCCESS`. Validator, Ruff, mypy, full pytest, Linux storage, Windows release guards and Local install/pypdf are all green.
- Error worker before this refresh: `3ced885839bea8f25e0d90bce22c8e0bb90a499d`; no workflow run existed on that SHA.
- Spec/Core: `7719c3f18de715fe1343980bdc466a2d12cdb286`; Core Focused `34843539383 = SUCCESS`; canonical `34843539369 = SUCCESS`.
- Backend: `d0da4ca3677ebcda1e65e1637fd0d447810fb7fb`; Backend Focused `34851416776 = SUCCESS`; canonical `34851416765 = SUCCESS`.
- UI: `575b8de0a4f25f512e423c78623bfa5b398c379d`; Core Focused `34845670246 = SUCCESS`; UI Focused `34845670143 = FAILURE`; canonical `34845670362 = FAILURE`; Visual remains red.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Current Develop — held closed

The newest Develop candidate is exact canonical green. The integrated structured-log privacy slice introduces no current Error-owned regression. Do not reopen or mutate Develop from Error worker without a new exact matching failure.

## Spec/Core — held closed

Current Spec/Core exact focused and canonical evidence is green. `ERR-0066`, `ERR-0065` and prior Core clusters stay closed absent new exact reproduction.

## Backend — held closed

Current Backend successor `d0da4ca3...` is exact Backend Focused and canonical green. The current slice hardens ExternalAccessGateway/runtime boundaries and plans periodic deep backup verification without producing a new backend/storage/recovery failure. Do not reopen while the exact candidate remains green.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS contract remain held.

## ERR-0063 / ERR-0064 / ERR-0065 / ERR-0066 — FIXED

No current exact matching capture-route, Core-selector, focused-enforcement or supersession-registry regression.

## Current UI failures — OPEN / UI-owned

Exact UI SHA `575b8de0...` has Core Focused green but UI Focused and canonical Quality red. UI Focused fails in `Run exact changed UI tests plus navigation invariant`. Canonical is isolated to full pytest: Local install/pypdf, Linux storage, Windows release guards, validator, Ruff and mypy all pass. The latest UI commit itself changes only the real grounding button label from `Sources` to `Ground`, while the branch carries a broader UI lineage. Error worker must not patch that product slice in parallel; consume the next exact UI successor and classify only new evidence.

## ERR-0054 — OPEN — UI/Visual Review

No baseline creation or acceptance by Error worker. The current UI handoff remains fail-closed at `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`; closure requires truthful UI-owned 11/11 reference/render review and final visual-verdict success.

## Persistent guards

Current Develop is canonical green; current Backend focused/canonical are green. On current UI, pypdf/local-install, Linux storage, Windows release guards, validator, Ruff and mypy are green. No current exact evidence reopens pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap clusters. Keep all guards unchanged.

## Next root cause

1. Consume the next exact UI successor and split the UI-owned regression cluster only if new exact failure evidence identifies independent root causes.
2. Keep Develop, Spec/Core and Backend closed while their current exact canonical/focused evidence stays green.
3. Keep ERR-0059, ERR-0063, ERR-0064, ERR-0065 and ERR-0066 closed absent exact regression.
4. ERR-0054 remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
