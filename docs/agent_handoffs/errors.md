# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `a034dc37af329802583124755b690b7baddaba10` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `ab3736bbdc73de3b07eb7062fa819273ee676bc2`; Backend Focused `35233727773 = SUCCESS`; canonical `35233727718 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — current backend exact candidate consumed
Backend exact head is `ab3736bb...`. No queued/in-progress canonical exists for this exact candidate; its focused and canonical runs are terminal.

## ITERATION-2 — ERR-0075 closed from exact evidence
Canonical full pytest is SUCCESS (`5331 passed, 17 skipped`), and `tests/unit/test_backup_verify_durable_service.py` contributes three passing tests. Backend Focused is also SUCCESS. The prior durable-service `actor_id/payload/version` contract drift is not reproduced, so ERR-0075 is FIXED and must stay closed absent a new exact-SHA regression.

## ITERATION-3 — ERR-0074 is now the sole Python-quality failure
Canonical specification validator, mypy and pytest are SUCCESS. Ruff alone fails with exactly one I001 at `tests/unit/test_backup_verify_durable_service.py:1:1`. The exact diagnostics artifact for `ab3736bb...` marks the complete lines 1-15 import block as fixable with `--fix`.

## ITERATION-4 — bounded root cause / next fix
Current source places `pytest` in its own blank-separated section before the wrapped `athena.*` imports. Repeated hand-authored ordering/section/wrapping variants have not closed canonical Ruff. Do not continue permutations. Execute repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, inspect and consume the complete generated diff, then require focused Ruff PASS plus focused durable-service pytest PASS before another canonical candidate.

## ITERATION-5 — held closures and guards
`tests/qa/test_visual_capture_manifest_truth.py` passes on exact `ab3736bb...`, so ERR-0059 remains FIXED with capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed semantics intact. Windows Path Safety, Linux Storage and Local-install are SUCCESS; persistent release guards remain closed. ERR-0054 remains OPEN/UI-Visual-Review-owned; UI evidence still does not establish review of all eleven reference/render pairs, and Error worker must not create or accept a baseline.

## Next root cause
1. Backend: ERR-0074 only — consume the complete pinned Ruff fixer output for the bounded durable-service test import block.
2. Focused Ruff and focused durable-service pytest must both pass before canonical.
3. Close ERR-0074 only from terminal exact-SHA canonical Ruff success.
4. Keep ERR-0075, ERR-0059 and green release guards closed; ERR-0054 remains UI-owned.
