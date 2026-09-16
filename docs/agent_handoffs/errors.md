# Error worker handoff

## Exact source of truth

- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `0d600cd268ab524fe3d7c057d241eef5bf2d85bb` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `868f089215444e4292c7de50664e1d514eff2ac7`; Backend Focused `35115493099 = SUCCESS`; canonical `35115492992 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — current Backend successor consumed

Backend advanced from `fb25d5d6...` to `868f0892...` with `Backend: repair durable service regression harness`. No concurrent canonical run is active for this exact SHA; its focused and canonical runs are terminal.

## ITERATION-2 — canonical failure remains two-cluster

Exact canonical `35115492992` is FAILURE. Python 3.12 quality has Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS, full pytest FAILURE. ERR-0074 remains OPEN and ERR-0075 remains IN_PROGRESS. Focused success does not close either canonical cluster.

## ITERATION-3 — durable-service harness locality established

Commit `868f0892...` modifies only `tests/unit/test_backup_verify_durable_service.py`, but substantially: 47 additions / 32 deletions. It replaces submit-occurrence tests with repository-backed `create` contract tests and changes the fixture shape. This is current exact locality evidence for investigating ERR-0075, but not proof of the exact failing pytest node/assertion.

## ITERATION-4 — release guards held closed

Linux storage, Local-install smoke and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS on exact `868f0892...`. Do not reopen or relax them.

## ITERATION-5 — visual/manifest ownership preserved

ERR-0059 = FIXED; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. ERR-0054 = OPEN / UI-Visual-Review-owned; Error worker must not create or accept a baseline.

## Next root cause

1. Extract `canonical-quality-diagnostics-868f089215444e4292c7de50664e1d514eff2ac7` and identify ERR-0075's exact failing pytest node/assertion before mutation.
2. Backend owns ERR-0074; consume its next terminal exact-SHA canonical successor before closure.
3. Do not reopen ERR-0072/0073 unless exact ERR-0075 diagnostics match those historical signatures.
4. Keep all currently green release guards closed.