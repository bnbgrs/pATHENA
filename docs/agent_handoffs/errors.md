# Error worker handoff

## Exact source of truth
- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: ledger refresh `164171db5c07c1a14c58f32cccaf6bcc681b7dd1` before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `0f312cce81d7c64c3b09da42c505d86baa73a8ee`; Backend Focused `35311052004 = SUCCESS`; canonical `35311052020 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — new Backend successor consumed
Backend advanced to `0f312cce...` (`Backend: apply canonical straight-import ordering`). The commit changes only the import block of `tests/unit/test_backup_verify_durable_service.py`.

## ITERATION-2 — exact canonical cascade deduplicated
Canonical `35311052020` is terminal FAILURE only in Python Ruff. Specification validator, mypy and full pytest are SUCCESS. Linux storage, Local-install and Windows path/release-guard jobs are SUCCESS. Backend Focused `35311052004` is SUCCESS.

## ITERATION-3 — ERR-0074 remains reproduced; manual-order hypothesis retired
Exact `0f312cce...` moves `import pytest` directly after the straight `import athena.jobs.backup_verify_durable_service as durable_service` and before the `from athena...` imports. Canonical Ruff still fails. This invalidates the previous remaining manual-order combination as a closure path. Repeated manual import permutations are no longer acceptable root-cause work. Backend must execute repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, preserve the complete generated diff, and demonstrate focused Ruff PASS before another canonical candidate.

## ITERATION-4 — held closures and release guards
`ERR-0075 = FIXED`: Backend Focused and canonical full pytest are green on exact `0f312cce...`. `ERR-0059 = FIXED`: no exact manifest-truth regression is reproduced; preserve capture-derived fields, `assigned_reference_count = 11`, and fail-closed exact-eleven semantics. Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf, Linux storage and Local-install remain green and must not be weakened.

## ITERATION-5 — visual ownership held
`ERR-0054 = OPEN`, UI/Visual-Review-owned. UI remains at `e1495158...`; no current evidence establishes completed truthful review of all eleven original-reference + exact-render pairs. Error worker neither creates nor accepts a baseline.

## Next root cause
1. Backend: `ERR-0074` only — execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` on exact `0f312cce...` and consume the complete generated transformation.
2. Do not submit another hand-authored import permutation as a fix candidate.
3. Require focused Ruff and focused durable-service pytest PASS before any further canonical candidate.
4. Close `ERR-0074` only from terminal exact-SHA canonical Ruff success.
5. Error worker consumes the next Backend successor immediately, then moves to the next independent current failure cluster.
