# Error worker handoff

## Exact source of truth

- Develop: `03157f15246c8acb0f51a30631bf45c4d2a72416`.
- Error worker: `ad6ac7eb196b95141b77759bb924c5b02c0c89b8` after current ledger refresh, before this handoff update.
- Spec/Core: `6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- Backend: `e850e7c423c689e0165952161aafb04ab35ee431`; Backend Focused `35068715724 = SUCCESS`; canonical `35068715548 = FAILURE`.
- UI: `e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## ITERATION-1 — current Backend successor consumed

Backend advanced from `9467134a...` to `e850e7c4...` with `Backend: match Ruff canonical import group`. Focused verification is terminal green. Canonical is terminal red.

## ITERATION-2 — exact Ruff diagnostic remains one bounded failure

Canonical diagnostics on exact `e850e7c4...` contain exactly one Ruff failure: `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`. The exact file has stdlib imports, then the `athena.*` imports, then `import pytest`. Ruff 0.15.22 still rejects that block and reports the issue as auto-fixable. `ERR-0074 = OPEN / Backend-owned`. The next owner action should use the repository-pinned Ruff fixer/check to derive the canonical import block instead of another manual ordering guess.

## ITERATION-3 — canonical cascade deduplicated

On exact `e850e7c4...`, specification validator, mypy and full pytest are green. Therefore `ERR-0072` and `ERR-0073` remain `FIXED`; no pytest, mypy or specification root cause is current. Canonical red is solely Ruff I001.

## ITERATION-4 — release guards held closed

Linux storage, Local-install smoke and Windows storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are green on exact `e850e7c4...`. Do not reopen or relax them.

## ITERATION-5 — visual/manifest ownership preserved

`ERR-0059 = FIXED`; preserve capture-derived fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS semantics. `ERR-0054 = OPEN / UI-Visual-Review-owned`; UI handoff still reports visual readiness `NO` and requires exact candidate artifacts to be opened and compared against original references. Error worker must not create or accept a baseline.

## Next root cause

1. Backend: run pinned Ruff against `tests/unit/test_backup_verify_durable_service.py`, apply only the exact canonical import organization it produces, focused verify, then exact canonical Quality.
2. Error worker: consume that successor exact SHA. Close `ERR-0074` only on terminal canonical green; otherwise isolate only the new concrete signature.
3. Keep pytest/mypy/specification and all persistent release guards closed absent new exact reproduction.
