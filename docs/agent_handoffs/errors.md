# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `6feda1729ffb86b62fa55d7b149ad8d207aae829` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `b1922d7b907861312356dc07bf8e8d86ad72d108`; Backend Focused `35152504280 = SUCCESS`; canonical `35152504291 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — bounded Backend successor consumed
Backend advanced from `868f0892...` to `b1922d7b...` with `Backend: fix durable verify canonical regressions`. The commit changes only `tests/unit/test_backup_verify_durable_service.py` (2 additions / 3 deletions): invalid `JobPriority.LOW` becomes `JobPriority.MAINTENANCE`, and one import-section blank line is removed.

## ITERATION-2 — ERR-0075 closed on exact canonical evidence
Canonical `35152504291` has full pytest SUCCESS. Therefore ERR-0075 is `FIXED` on exact `b1922d7b...`; do not reopen absent a new exact-SHA pytest failure signature.

## ITERATION-3 — ERR-0074 remains sole Backend Python-quality failure
On the same exact SHA, Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS, pytest SUCCESS. ERR-0074 remains `OPEN` and Backend-owned. Focused `35152504280` is SUCCESS but does not close canonical Ruff.

## ITERATION-4 — release guards held closed
Linux storage, Local-install smoke and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS on exact `b1922d7b...`. Do not reopen or relax them.

## ITERATION-5 — visual/manifest ownership preserved
ERR-0059 = `FIXED`; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. ERR-0054 = `OPEN` / UI-Visual-Review-owned; Error worker must not create or accept a baseline.

## Next root cause
1. Consume the next Backend exact-SHA canonical successor for ERR-0074; close only if Ruff and canonical are terminal green.
2. Do not touch ERR-0075 again absent a new exact pytest regression.
3. Keep all currently green release guards closed.