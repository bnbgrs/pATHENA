# Error worker handoff

## Exact source of truth

- Develop: `90f5439bfdb4502bc689c51b06f83586c50c9d7c`; canonical `34828796469 = SUCCESS`.
- Error worker before this refresh: `09578df4a2a72547ee88036d2dc526d2b57517ff`.
- Spec/Core: `2a3db0442d5955bfb945e0d5376f93d205006abc`; canonical `34827461812 = IN_PROGRESS`. Validator, Ruff, mypy, Linux storage, Windows release guards and local install/pypdf are green; full pytest remains in progress.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; held closed absent a new exact matching failure.
- UI: `a88eac5f05db4128ae21b7c747e95c16a91191c4`; no newer exact successor in this run. Visual reaches eleven captures and route identity; canonical remains red only in the previously isolated UI-specific pytest slice.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ERR-0064 — FIXED

The Core-focused ownership selector repair remains integrated in Develop. Current Develop also restores intended type-change coverage for that selector boundary, and exact canonical `34828796469 = SUCCESS`. No guard was weakened.

## Current Spec/Core candidate — IN_PROGRESS / Core-owned

Exact canonical `34827461812` on `2a3db0442d5955bfb945e0d5376f93d205006abc` is not terminal. Validator, Ruff, mypy, Linux storage, Windows release guards and local install/pypdf are green; full pytest is still running. Do not classify a new Error root cause without terminal exact-SHA failure evidence.

## Current UI canonical regressions — OPEN / UI-owned

Latest exact UI SHA remains `a88eac5f...`; no newer UI successor exists. The canonical red remains UI-specific full-pytest evidence, not Error-owned. Do not patch those product files from `postmerge/errors`.

## ERR-0063 — FIXED

Current exact UI visual evidence captures all eleven canonical surfaces and passes workspace route identity.

## ERR-0059 — FIXED

Current exact UI artifact evidence verifies capture-derived manifest fields and preserves `assigned_reference_count=11` plus the exact-eleven fail-closed PASS contract. No new matching regression is reproduced.

## ERR-0054 — OPEN — UI/Visual Review

Technical capture is complete, but truthful 11/11 pair-review evidence is still absent. Error worker must not create or accept a baseline. UI owns pair review and final visual verdict.

## Green / held clusters

- Current Develop canonical is green on exact SHA `90f5439b...`.
- Backend remains held closed absent a new matching exact-SHA failure.
- Spec/Core is being exact-qualified and is not an Error-worker diagnosis target while its canonical is still running.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.
- Error-worker 48px Send geometry remains `STALE`, not a new product root cause.

## Next root cause

1. Consume terminal Spec/Core canonical `34827461812`; classify only a newly reproduced exact failure.
2. Consume the next exact UI successor and classify only newly reproduced signatures.
3. Keep `ERR-0064`, `ERR-0059` and `ERR-0063` closed absent exact regression.
4. `ERR-0054` remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
