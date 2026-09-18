# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@1a418788ed7f6cec547f4209aa3d3d2f3b49c9a1` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@1ab371ba7e3198acca019b4975c5d2f22e4ce537`; Backend Focused `35329720681 = SUCCESS`; canonical Quality `35329720830 = FAILURE`.
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
Exact reproduction: `postmerge/backend@1ab371ba7e3198acca019b4975c5d2f22e4ce537`, canonical Quality `35329720830`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails. Backend Focused `35329720681` is SUCCESS. Linux storage regressions, Local-install smoke and Windows path safety are SUCCESS.

Canonical diagnostics artifact `canonical-quality-diagnostics-1ab371ba7e3198acca019b4975c5d2f22e4ce537` reproduces exactly one fixable `I001` at `tests/unit/test_backup_verify_durable_service.py:1:1`: current import block is future import, `unittest.mock.Mock`, `pytest`, blank line, then `athena.*`; Ruff says `Organize imports` and `1 fixable with --fix`. The repository pins Ruff `==0.15.22`. Repeated hand-authored import permutations are non-closure evidence. Backend owns this file; Error worker must not mutate it in parallel. Required action remains actual pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, complete generated diff, focused Ruff PASS, then exact canonical verify.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
Canonical `35329720830` full pytest is SUCCESS on exact `1ab371ba...`; no new durable-service contract failure is reproduced. Do not reopen absent a new exact-SHA failure signature.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No new exact-SHA manifest-truth regression is reproduced on Backend `1ab371ba...`; full canonical pytest is green. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `1ab371ba7e3198acca019b4975c5d2f22e4ce537`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074` only: Backend must execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` and consume the complete generated transformation; focused Ruff PASS required.
2. `ERR-0075` and `ERR-0059` remain FIXED on exact `1ab371ba...`; do not touch without new reproduction.
3. Close `ERR-0074` only from terminal exact-SHA canonical Ruff success.
4. `ERR-0054` remains UI/Visual-Review-owned; Error worker only verifies evidence/closure status.