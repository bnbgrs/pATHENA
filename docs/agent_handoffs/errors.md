# Error worker handoff

## Exact source of truth

- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `982645be2fe74a8f137a869c2e60539ef3339f7b` after ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `7e6274d05b431356b5d0b99175b6105a6ebd4220`; Backend Focused `35087092246 = SUCCESS`; canonical `35087092238 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — terminal exact Backend result consumed

Canonical `35087092238` is terminal FAILURE on exact Backend `7e6274d0...`; focused is SUCCESS. No competing canonical run was started.

## ITERATION-2 — canonical cascade reclassified

Python 3.12 quality has Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS and full pytest FAILURE. Therefore the previous Ruff-only classification is stale. ERR-0074 remains OPEN and a separate current full-pytest cluster is tracked as ERR-0075 IN_PROGRESS until exact diagnostics identify its failing node/assertion.

## ITERATION-3 — bounded commit verified

Commit `7e6274d0...` itself changes only the import sections of `tests/unit/test_backup_verify_durable_service.py`: `pytest` is moved between stdlib and `athena.*`. Unlike earlier broad candidates, this successor does not alter test semantics. Because canonical Ruff still fails, Backend must use the pinned Ruff 0.15.22 fixer/check output rather than another manual import-order guess.

## ITERATION-4 — release guards held closed

Linux storage, Local-install smoke and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS on exact `7e6274d0...`. Do not reopen or relax them.

## ITERATION-5 — visual/manifest ownership preserved

ERR-0059 = FIXED; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. ERR-0054 = OPEN / UI-Visual-Review-owned; Error worker must not create or accept a baseline.

## Next root cause

1. Extract `canonical-quality-diagnostics-7e6274d05b431356b5d0b99175b6105a6ebd4220` and identify ERR-0075's exact failing pytest node/assertion before mutation.
2. Backend: generate ERR-0074's import patch with pinned Ruff 0.15.22; do not change test semantics.
3. Error worker: consume next exact Backend successor and close only with terminal matching evidence.
4. Keep all currently green release guards closed; do not reopen ERR-0072/0073 unless ERR-0075 diagnostics exactly reproduce those historical signatures.