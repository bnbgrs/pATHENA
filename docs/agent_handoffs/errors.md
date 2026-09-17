# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `02c10dad73e5856e3b503efa7cc1d10ac350bdcc` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `629fcb0aaf523a73da6a6f379d2ff97dcf8f6aef`; Backend Focused `35194752034 = SUCCESS`; canonical `35194752046 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Backend successor consumed
Backend advanced from `cc7cfc82...` to `629fcb0a...` with `Backend: restore Ruff import sections`. The commit is bounded to `tests/unit/test_backup_verify_durable_service.py` (2 additions, 1 deletion), moving `import pytest` before `athena.*` and restoring a blank section boundary.

## ITERATION-2 — exact canonical consumed
Backend Focused is SUCCESS. Canonical `35194752046` is terminal FAILURE. Python quality shows Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS and full pytest SUCCESS. Windows path safety, Linux storage regressions and Local-install smoke are SUCCESS.

## ITERATION-3 — manual import-permutation path exhausted
The current conventional-looking structure (`unittest.mock`; blank; `pytest`; blank; `athena.*`) still fails Ruff. Earlier exact candidates rejected contiguous and opposite-order variants. Therefore the prior narrow hypothesis that only pytest/athena ordering or a single section boundary remains is no longer authoritative. Do not spend another slice on a guessed permutation. Obtain the exact Ruff 0.15.22 fixer transformation on this SHA and inspect the entire generated diff.

## ITERATION-4 — cascade and guards held closed
ERR-0074 remains `OPEN` and is the sole current Backend Python-quality root cause. ERR-0075 remains `FIXED` because canonical full pytest is green. Current Windows release guards, Linux storage and Local-install remain green and must not be reopened or relaxed.

## ITERATION-5 — visual/manifest ownership preserved
ERR-0059 = `FIXED`; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. ERR-0054 = `OPEN` / UI-Visual-Review-owned; Error worker must not create or accept a baseline. No current Error-worker evidence proves eleven pairwise visual reviews complete.

## Next root cause
1. Backend owns ERR-0074. On exact `629fcb0a...`, execute repository-pinned Ruff 0.15.22 `check --fix` for the failing module and inspect the complete generated diff rather than predicting it.
2. Apply only the bounded generated fix; focused Ruff + durable-service pytest.
3. Start/consume one canonical candidate only if no run for that exact SHA is queued/in-progress; close ERR-0074 only on terminal canonical Ruff success.
4. Keep ERR-0075, ERR-0059 and all currently green release guards closed absent new exact signatures.
