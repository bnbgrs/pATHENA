# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@678615fc7fbf0ff92958b234ad747dc6798e2353` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@0f312cce81d7c64c3b09da42c505d86baa73a8ee`; Backend Focused `35311052004 = SUCCESS`; canonical Quality `35311052020 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- Worker handoffs outside this ledger are historical when their embedded heads differ from the current branch heads above.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
UI remains on `e1495158...`; no current Error-worker evidence establishes truthful review of all eleven original-reference + exact-render pairs. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@0f312cce81d7c64c3b09da42c505d86baa73a8ee`, canonical Quality `35311052020`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails. Backend Focused `35311052004` is SUCCESS. Windows path safety, Linux storage regressions and Local-install smoke are SUCCESS.

The exact commit `0f312cce...` changes only `tests/unit/test_backup_verify_durable_service.py` and moves `import pytest` immediately after the straight `import athena.jobs.backup_verify_durable_service as durable_service`, before the `from athena...` imports. Canonical Ruff still fails, so `Backend: apply canonical straight-import ordering` is not closure evidence. This supersedes the prior bounded manual-ordering hypothesis. Repeated hand-authored import permutations have now produced multiple exact-SHA Ruff failures and must not be treated as root-cause fixes. Backend owns this file; Error worker must not mutate it in parallel. Required action: run repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` on the exact source, preserve the complete generated diff, and require focused Ruff PASS before another canonical candidate.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
On exact Backend `0f312cce...`, Backend Focused and canonical full pytest are SUCCESS. The durable-service test module has no new exact-SHA contract regression.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
On exact Backend `0f312cce...`, canonical full pytest is SUCCESS and no manifest-truth regression is reproduced. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `0f312cce...`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074` remains the only current Backend Python-quality failure cluster on exact `0f312cce...`.
2. Backend owns the bounded test file; Error worker will not mutate it in parallel.
3. Do not continue manual import-order guessing. Execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` on the exact file and consume the complete generated transformation.
4. Require focused Ruff + focused durable-service pytest PASS before canonical; close only on terminal exact-SHA canonical Ruff success.
5. Keep `ERR-0075`, `ERR-0059` and current release guards closed; `ERR-0054` remains UI/Visual-Review-owned.
