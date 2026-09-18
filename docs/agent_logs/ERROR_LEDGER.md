# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@c9f8d916605a0e838f1a5aaebd036339704f0de6` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@bd5c73fc62daebe7f8c3ba4ac23a75b6ff539201`; Backend Focused `35350399944 = SUCCESS`; canonical Quality `35350400021 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
UI remains on `e1495158...`; no new Error-worker evidence closes the required truthful review of all eleven original-reference + exact-render pairs. Error worker must not create or accept a baseline.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@bd5c73fc62daebe7f8c3ba4ac23a75b6ff539201`, canonical Quality `35350400021`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails. Backend Focused `35350399944` is SUCCESS. Linux storage regressions, Local-install smoke and Windows path safety are SUCCESS.

Current exact source import block is future import, `unittest.mock.Mock`, blank line, `pytest` immediately followed by `athena.*`. This successor therefore supplies a new exact import-grouping candidate, but canonical Ruff still rejects it. Repeated hand-authored import permutations are non-closure evidence. Backend owns this file; Error worker must not mutate it in parallel. Required action remains actual repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, complete generated diff, focused Ruff PASS, then exact canonical verify.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
Canonical `35350400021` full pytest is SUCCESS on exact `bd5c73fc...`; no new durable-service contract failure is reproduced. Do not reopen absent a new exact-SHA failure signature.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No new exact-SHA manifest-truth regression is reproduced on Backend `bd5c73fc...`; full canonical pytest is green. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `bd5c73fc62daebe7f8c3ba4ac23a75b6ff539201`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074` only: Backend must execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` and consume the complete generated transformation; focused Ruff PASS required.
2. `ERR-0075` and `ERR-0059` remain FIXED on exact `bd5c73fc...`; do not touch without new reproduction.
3. Close `ERR-0074` only from terminal exact-SHA canonical Ruff success.
4. `ERR-0054` remains UI/Visual-Review-owned; Error worker only verifies evidence/closure status.
