# Error worker handoff

## Exact source of truth

- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`; last exact Develop canonical Quality remains green.
- Error worker: `b8e1fb0f0f91e7323448a06b5f3240b8dff6ecee` after current ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `ab3cc6ba34de285dff3cc8d5e3581045a8cf9677`; Backend Focused `35055735369 = SUCCESS`; canonical `35055735368 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — current Backend successor consumed

Backend advanced from `4156e57d...` to `ab3cc6ba...` with `Backend: apply Ruff import ordering`. Focused verification is terminal green. Canonical remains terminal red.

## ITERATION-2 — exact Ruff diagnostic isolated

Canonical diagnostics on exact `ab3cc6ba...` contain exactly one Ruff failure: `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`. Current imports place `import athena.jobs.backup_verify_durable_service as backup_verify_durable_service` before `import pytest`. `ERR-0074 = OPEN / Backend-owned`. Apply Ruff canonical organization to this import block only.

## ITERATION-3 — cascade deduplicated

On exact `ab3cc6ba...`, specification validator, mypy and full pytest are green. Therefore prior `ERR-0072` and `ERR-0073` are not current failures and are `FIXED`; do not reopen them from historical ledger state. The canonical failure is solely Ruff I001.

## ITERATION-4 — release guards held closed

Linux storage, Local-install Core/API restart + pypdf and Windows storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are green on exact `ab3cc6ba...`. Do not reopen or relax them.

## ITERATION-5 — visual/manifest ownership preserved

`ERR-0059 = FIXED`; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. `ERR-0054 = OPEN / UI-Visual-Review-owned`; Error worker must not create or accept a baseline and should only consume evidence for the eleven real reference+render pairs.

## Next root cause

1. Backend: fix only Ruff I001 in `tests/unit/test_backup_verify_durable_service.py` using canonical import organization; focused verify then exact canonical Quality.
2. Error worker: consume that successor exact SHA. Close `ERR-0074` only on terminal canonical green; otherwise isolate only the new concrete signature.
3. Keep pytest/mypy/specification and all persistent release guards closed absent new exact reproduction.
