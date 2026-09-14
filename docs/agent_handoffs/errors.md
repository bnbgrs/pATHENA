# Error worker handoff

## Exact source of truth

- Develop: `0ea74a990f8375039769c7726a327fd9142d5985`; canonical `34839249527 = SUCCESS`.
- Error worker before this refresh: `c12664dd5cb8393bf65f782a9e89637f5f16a336`; no exact workflow run exists on that documentation-only SHA.
- Spec/Core: `f5013995078ce355e64fe4dd7bd7c2a549a30ef9`; Core Focused `34838026579 = SUCCESS`; canonical `34838026561 = FAILURE`.
- Backend: `ef5a00fb79ebbbcbae0f77c826975068e7ec629f`; Storage Focused `34839202950 = SUCCESS`; canonical `34839202948 = SUCCESS`.
- UI: `a88eac5f05db4128ae21b7c747e95c16a91191c4`; no newer exact UI successor exists.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ERR-0066 — OPEN — Spec/Core-owned canonical supersession registry-contract regression

Exact diagnostics for canonical run `34838026561` were opened. Full pytest reports `1 failed, 5164 passed, 17 skipped`; the sole failure is `tests/unit/test_relation_registry_contract.py::test_unknown_relation_type_falls_back_without_ontology_growth`.

The candidate intentionally adds directed Knowledge-to-Knowledge `superseded_by` to the default relation registry. The failing test still expects only `related_to`, `same_as`, `different_from`, and `belongs_to_project`. Unknown relation resolution still falls back to `related_to`; the stale assertion is only the default-definition tuple. Exact Core Focused on the same SHA is green.

Spec/Core owns this supersession slice. Make the smallest candidate-owned contract correction, do not weaken fallback semantics or enforcement, and require exact Core Focused plus canonical success on the successor. Error worker must not patch the same Core-owned product/test slice in parallel.

## ERR-0065 — FIXED

Current Spec/Core successor has exact Core Focused `34838026579 = SUCCESS`, so the previous candidate-specific focused enforcement failure is closed. Do not conflate it with ERR-0066.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived fields, `assigned_reference_count=11`, and fail-closed exact-eleven PASS contract remain held.

## ERR-0063 / ERR-0064 — FIXED

No new exact matching capture-route or Core-focused selector-contamination regression.

## Backend — held closed

Current Backend SHA `ef5a00fb...` is exact Storage Focused and canonical green. Do not reopen a Backend/Storage cluster without a new matching exact failure.

## Current UI failures — OPEN / UI-owned

Latest exact UI SHA remains `a88eac5f...`; no newer UI successor exists. Do not patch UI product code from `postmerge/errors`; consume the next successor and classify only new exact evidence.

## ERR-0054 — OPEN — UI/Visual Review

No baseline creation or acceptance by Error worker. Closure still requires truthful UI-owned 11/11 reference/render review and final visual-verdict success.

## Persistent guards

Current Develop canonical is green. Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.

## Next root cause

1. Consume the Spec/Core successor for ERR-0066; require exact Core Focused and canonical success on the same candidate lineage.
2. Keep ERR-0065, ERR-0064, ERR-0059 and ERR-0063 closed absent exact regression.
3. Keep Backend closed while exact Focused and canonical remain green.
4. Consume the next exact UI successor; ERR-0054 remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
