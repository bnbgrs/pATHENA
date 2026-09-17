# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `cf5b4ebb56580c968e2394ab889df5546addbf54` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `b88399f2a7121f54a071dd770a28419621ff428d`; Backend Focused `35215567439 = SUCCESS`; canonical `35215567394 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Backend successor consumed
Backend advanced from `10130d00...` to `b88399f2...` with `Backend: apply exact Ruff import order`. The commit is bounded to `tests/unit/test_backup_verify_durable_service.py` and leaves the long service import wrapped while moving `import pytest` after all `athena.*` imports.

## ITERATION-2 — exact canonical consumed
Backend Focused is SUCCESS. Canonical `35215567394` is terminal FAILURE. Python quality shows Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS and full pytest SUCCESS. Windows path safety, Linux storage regressions and Local-install smoke are SUCCESS.

## ITERATION-3 — fresh diagnostics extracted
The canonical diagnostics artifact for exact `b88399f2...` was downloaded and inspected. Ruff reports exactly one failure: `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`, covering the full import block through line 14. The exact current block is `__future__`, `unittest.mock`, wrapped `athena.*` imports, then `import pytest`. Therefore the current claimed exact ordering is not Ruff's accepted complete transformation.

## ITERATION-4 — cascade and guards held closed
ERR-0074 remains `OPEN` and is the sole current Backend Python-quality root cause. ERR-0075 remains `FIXED` because canonical full pytest is green. Current Windows release guards, Linux storage and Local-install remain green and must not be reopened or relaxed. ERR-0059 remains `FIXED`; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics.

## ITERATION-5 — ownership and next bounded hypothesis
ERR-0054 remains `OPEN` / UI-Visual-Review-owned; Error worker must not create or accept a baseline. For ERR-0074, previous candidates separately tried pytest-before-athena, blank-section, contiguous, opposite-order and pre-wrap forms, while the current candidate supplies the wrapped long import. The still-untried bounded combination suggested by Ruff/isort ordering semantics is `import pytest` immediately before the wrapped `athena.*` imports with no blank separator. This is a diagnostic hypothesis only, not PASS evidence: Backend should preferably execute pinned Ruff 0.15.22 `check --fix` directly and copy its complete output. Focused Ruff must pass before another canonical run.

## Next root cause
1. Backend owns ERR-0074. Apply the complete pinned Ruff 0.15.22 fixer output on exact `b88399f2...`; do not make another partial formatting/order slice.
2. Focused Ruff + durable-service pytest first. If Ruff remains red, do not start canonical; inspect the exact generated fixer diff.
3. Only after focused Ruff PASS, ensure no queued/in-progress canonical exists for that candidate and consume one canonical run.
4. Close ERR-0074 only on terminal canonical Ruff SUCCESS.
5. Keep ERR-0075, ERR-0059 and all green release guards closed; ERR-0054 remains UI-owned.
