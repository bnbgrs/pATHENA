# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `7e5e1afba4812f6b0ea7384a7f43d043e2c309d1` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `d038de0f7790e017987e2ada53d97eff7b17cf1a`; Backend Focused `35166803020 = SUCCESS`; canonical `35166803040 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — Backend successor consumed
Backend advanced from `073cb77e...` to `d038de0f...` with `Backend: apply Ruff import section fix`. The commit is bounded to one deletion in `tests/unit/test_backup_verify_durable_service.py`: it removes the blank line between `pytest` and the `athena.*` imports.

## ITERATION-2 — exact diagnostics extracted
Canonical `35166803040` is terminal FAILURE. The canonical diagnostics artifact was downloaded and inspected. It proves exactly one Ruff failure: `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`, explicitly fixable with `--fix`. Specification Validator, mypy and full pytest are SUCCESS.

## ITERATION-3 — root cause narrowed
The current import section is now contiguous but ordered `pytest` before `athena.*`. Since removing the section break did not change the exact I001 signature, the remaining unresolved dimension is deterministic ordering inside the Ruff-classified third-party section, not another blank-line/grouping variant. Stop manual grouping guesses. Capture the exact pinned Ruff 0.15.22 `--fix` output and preserve its generated order.

## ITERATION-4 — cascade and guards held closed
ERR-0074 remains `OPEN` and is the sole current Backend Python-quality root cause. ERR-0075 remains `FIXED`: canonical full pytest is green. Local-install, Linux storage and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS on exact `d038de0f...`; do not reopen or relax them.

## ITERATION-5 — visual/manifest ownership preserved
ERR-0059 = `FIXED`; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. ERR-0054 = `OPEN` / UI-Visual-Review-owned; Error worker must not create or accept a baseline. No current Error-worker evidence proves eleven pairwise visual reviews complete.

## Next root cause
1. Backend owns ERR-0074. Obtain the exact Ruff 0.15.22 `--fix` diff for the current file and apply only that bounded generated import-order change.
2. Focused Ruff + durable-service pytest, then one canonical candidate if no exact-SHA run is queued/in-progress.
3. Close ERR-0074 only on terminal exact-SHA canonical Ruff success.
4. Keep ERR-0075, ERR-0059 and all currently green release guards closed absent new exact signatures.