# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@80fd2febfd2a2d8b23e17d902763b7dced52e69d` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@71e551364c5355e8d030b0964c39d9ed53e502bb`; Backend Focused `35324506141 = SUCCESS`; canonical Quality `35324506070 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Worker handoffs outside this ledger are historical when their embedded heads differ from the current branch heads above.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
UI remains on `e1495158...`; current UI handoff explicitly reports `PAIRS_VERIFIED_0_OF_11` and `MATCH_0_OF_11`. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@71e551364c5355e8d030b0964c39d9ed53e502bb`, canonical Quality `35324506070`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails with one fixable `I001` in `tests/unit/test_backup_verify_durable_service.py:1:1`. Backend Focused `35324506141` is SUCCESS. Windows path safety, Linux storage regressions and Local-install smoke are SUCCESS.

Exact canonical diagnostics show the current block as `from __future__`, `from unittest.mock import Mock`, `import athena.jobs.backup_verify_durable_service as durable_service`, `import pytest`, then `from athena...`; Ruff reports `help: Organize imports` and `1 fixable with --fix`. Repeated hand-authored import permutations are non-closure evidence. Backend owns this file; Error worker must not mutate it in parallel. Required action: execute repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, preserve the complete generated diff, and require focused Ruff PASS before another canonical candidate.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
Exact closure: Backend `71e551364c5355e8d030b0964c39d9ed53e502bb` restores the production string pipeline contract and wrong-string invalid-input fixture. Canonical `35324506070` full pytest is SUCCESS with `5331 passed, 17 skipped, 2 warnings`; the bounded durable-service tests are therefore closed on this exact SHA. Do not reopen absent a new exact-SHA failure signature.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No new exact-SHA manifest-truth regression is reproduced on Backend `71e551364c5355e8d030b0964c39d9ed53e502bb`; full canonical pytest is green. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `71e551364c5355e8d030b0964c39d9ed53e502bb`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074` only: Backend must execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` on exact current source and consume the complete generated import transformation; focused Ruff PASS required.
2. `ERR-0075` is FIXED on exact `71e551...`; do not touch it again without a new reproduction.
3. Only after focused Ruff passes should Backend produce another canonical candidate. Close `ERR-0074` only from terminal exact-SHA canonical Ruff success.
4. Keep `ERR-0059` and current release guards closed. `ERR-0054` remains UI/Visual-Review-owned.