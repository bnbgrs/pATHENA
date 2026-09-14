# Error worker handoff

## Exact source of truth

- Develop: `b3766e0c690aac4db0567c63a3e2886f8fbce368`; canonical `34823250897 = SUCCESS`.
- Error worker before this refresh: `206cd50938da4da3f19f7eda6e870718b94f7226`; carries the bounded `ERR-0064` selector repair in its ancestry.
- Spec/Core: `6c7f417a53428f496d7b31e330917d4a53c85189`; held closed absent a new exact matching failure.
- Backend: `52eb61de9ecfde4074778a1bab2966e18aab526d`; held closed absent a new exact matching failure.
- UI: `a88eac5f05db4128ae21b7c747e95c16a91191c4`; Visual reaches final verdict after 11 captures and route identity; canonical remains red only in the isolated UI pytest slice.

## ERR-0064 — FIXED

Current Develop contains the bounded Core-focused selector repair. Ruff, mypy and Ruff remediation now use the same Core-owned test-family boundary as focused pytest rather than all `tests/unit/*.py`. Current Develop canonical `34823250897 = SUCCESS`. No test or canonical guard was weakened.

## Current UI canonical regressions — OPEN / UI-owned

The latest exact UI SHA remains `a88eac5f...`; its canonical red is UI-specific full-pytest evidence, not Error-owned. Do not patch those product files from `postmerge/errors`. Reclassify only from a newer exact UI successor.

## ERR-0063 — FIXED

Exact current UI visual evidence captures all eleven canonical surfaces and passes workspace route identity.

## ERR-0059 — FIXED

Exact current UI artifact evidence verifies capture-derived manifest fields and preserves `assigned_reference_count=11` plus the exact-eleven fail-closed PASS contract.

## ERR-0054 — OPEN — UI/Visual Review

Technical capture is complete, but truthful 11/11 pair-review evidence is still absent. Error worker must not create or accept a baseline. UI owns pair review and final visual verdict.

## Green / held clusters

- Current Develop canonical is green.
- Spec/Core and Backend remain held closed absent a new matching exact-SHA failure.
- Persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards remain unchanged.
- Error-worker 48px Send geometry remains `STALE`, not a new product root cause.

## Next root cause

1. Consume the next exact UI successor and classify only newly reproduced signatures.
2. Keep `ERR-0064`, `ERR-0059` and `ERR-0063` closed absent exact regression.
3. `ERR-0054` remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
