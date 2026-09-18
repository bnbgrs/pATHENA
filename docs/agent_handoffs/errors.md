# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: ledger refresh `215f5ad0486a69da320d2be081652c3bf209a037` before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `d8238749500ac13b8072564bf05437ea9025af9b`; Backend Focused `35299441096 = SUCCESS`; canonical `35299441030 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — new Backend successor consumed
Backend advanced from `732bcbee...` to `d823874...`. The new commit is titled `Backend: apply exact Ruff import fix` and changes only the import block of `tests/unit/test_backup_verify_durable_service.py`.

## ITERATION-2 — exact canonical cascade deduplicated
Canonical `35299441030` is terminal FAILURE only in Python Ruff. Specification validator, mypy and full pytest are SUCCESS. Linux storage, Local-install and Windows path/release-guard jobs are SUCCESS. Backend Focused `35299441096` is SUCCESS.

## ITERATION-3 — ERR-0074 remains reproduced; candidate claim rejected
Canonical Ruff still fails on exact `d823874...`; therefore the commit title is not closure evidence. Exact source places `import pytest` before `athena.*` but separates them with a blank line. The predecessor `732bcbee...` instead placed `athena.*` before `pytest` without a blank line and also failed. These exact candidates isolate the remaining untested combined import-section state: `import pytest` immediately followed by the `athena.*` imports with no blank separator. Preferred action remains executing pinned Ruff 0.15.22 `--fix` and consuming the complete generated diff; the combined state is only the bounded fallback if direct fixer execution is unavailable.

## ITERATION-4 — held closures and release guards
`ERR-0075 = FIXED`: Backend Focused and canonical full pytest are green on exact `d823874...`. `ERR-0059 = FIXED`: no exact manifest-truth regression is reproduced; preserve capture-derived fields, `assigned_reference_count = 11`, and fail-closed exact-eleven semantics. Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf, Linux storage and Local-install remain green and must not be weakened.

## ITERATION-5 — visual ownership held
`ERR-0054 = OPEN`, UI/Visual-Review-owned. UI remains at `e1495158...`; no current evidence establishes completed truthful review of all eleven original-reference + exact-render pairs. Error worker neither creates nor accepts a baseline.

## Next root cause
1. Backend: `ERR-0074` only — execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` on the exact file and consume the complete generated diff.
2. If direct fixer execution is unavailable, test only `import pytest` immediately followed by the `athena.*` imports with no blank separator; do not revisit already failed permutations.
3. Require focused Ruff and focused durable-service pytest PASS before any further canonical candidate.
4. Close `ERR-0074` only from terminal exact-SHA canonical Ruff success.
5. Error worker consumes the next Backend successor immediately, then moves to the next independent current failure cluster.
