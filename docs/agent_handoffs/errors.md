# Error worker handoff

## Exact source of truth

- Develop: `fef85f3d53c9e3d13f20c515ed2bbb0558383f4c`; canonical `34847605826 = IN_PROGRESS`. Windows path safety, Linux storage, Local install/pypdf, validator, Ruff and mypy are green; full pytest is still running.
- Error worker before this refresh: `22d7a2534ff7c256bcf95f9caeb386de4d9c5a61`; no workflow run exists on that SHA.
- Spec/Core: `7719c3f18de715fe1343980bdc466a2d12cdb286`; Core Focused `34843539383 = SUCCESS`; canonical `34843539369 = SUCCESS`.
- Backend: `8d2b07d4015f34328541ef035a155fd65d13dbf8`; Storage Focused `34844716718 = SUCCESS`; canonical `34844716724 = SUCCESS`.
- UI: `575b8de0a4f25f512e423c78623bfa5b398c379d`; Core Focused `34845670246 = SUCCESS`; UI Focused `34845670143 = FAILURE`; canonical `34845670362 = FAILURE`; Visual `34845664472 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ERR-0066 — FIXED

The current Spec/Core successor repairs the stale relation-registry contract while preserving the actual anti-ontology-growth invariant and unknown-relation fallback. Exact Core Focused and canonical Quality are both green on `7719c3f18de715fe1343980bdc466a2d12cdb286`. Do not reopen absent a new exact matching regression.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS contract remain held.

## ERR-0063 / ERR-0064 / ERR-0065 — FIXED

No new exact matching capture-route, Core-selector contamination, or prior focused-enforcement regression.

## Backend — held closed

Current Backend SHA `8d2b07d4...` is exact Storage Focused and canonical green. The WAL scheduler control-housekeeping slice is already independently qualified. Do not reopen a Backend/Storage cluster without a new matching exact failure.

## Current Develop — IN_PROGRESS

Develop `fef85f3d...` bundles the exact-green Spec/Core supersession and Backend WAL-housekeeping slices. Canonical `34847605826` is still in progress. Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy are green; full pytest is the only currently running quality step. Do not start a competing run or mutate this Develop candidate.

## Current UI failures — OPEN / UI-owned

Exact UI SHA `575b8de0...` has Core Focused green, but UI Focused, canonical Quality and 11-Surface Visual are red. This is a current UI-owned candidate. Error worker must not patch UI product code in parallel; consume the next exact UI successor and classify only its new evidence.

## ERR-0054 — OPEN — UI/Visual Review

No baseline creation or acceptance by Error worker. The current UI handoff remains fail-closed for exact candidate review; closure still requires truthful UI-owned 11/11 reference/render review and final visual-verdict success.

## Persistent guards

No current exact evidence reopens pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap clusters. Keep all guards unchanged.

## Next root cause

1. Consume terminal Develop canonical `34847605826`; only a newly reproduced exact-SHA failure may open a new Error cluster.
2. Keep ERR-0066, ERR-0065, ERR-0064, ERR-0059 and ERR-0063 closed absent exact regression.
3. Keep Backend closed while exact Focused and canonical remain green.
4. Consume the next exact UI successor; current UI failures remain UI-owned.
5. ERR-0054 remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
