# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@c23cece104e2849a428e2e97fed5399199f9c539` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@b1922d7b907861312356dc07bf8e8d86ad72d108`; Backend Focused `35152504280 = SUCCESS`; canonical Quality `35152504291 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
No Error-worker closure evidence. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@b1922d7b907861312356dc07bf8e8d86ad72d108`, canonical Quality `35152504291`, Python 3.12 quality: Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS, full pytest SUCCESS. Backend Focused `35152504280` is SUCCESS. The bounded successor changed only `tests/unit/test_backup_verify_durable_service.py` (2 additions / 3 deletions), removed an import-section blank line and replaced invalid `JobPriority.LOW` with existing `JobPriority.MAINTENANCE`. Ruff remains the sole Python-quality failure; do not infer closure from focused/full-pytest success.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend full-pytest regression
Status: `FIXED`
Exact successor `b1922d7b907861312356dc07bf8e8d86ad72d108` has canonical full pytest SUCCESS. The predecessor failure was the durable-service harness use of nonexistent `JobPriority.LOW`; the bounded successor uses `JobPriority.MAINTENANCE`. Do not reopen absent a new exact-SHA pytest failure signature.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No current exact evidence reproduces the manifest-truth defect. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

- `ERR-0072` — `FIXED`; no current reproduction.
- `ERR-0073` — `FIXED`; no current reproduction.
- `ERR-0070` — `FIXED`.
- `ERR-0071` — `FIXED`.
- `ERR-0063` — `FIXED`.
- `ERR-0064` — `FIXED`.
- `ERR-0065` — `STALE`.
- `ERR-0066` — `FIXED`.
- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `b1922d7b...`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. ERR-0074 is now the sole current Backend Python-quality failure; Backend owns its exact Ruff I001 closure. Consume only a terminal exact-SHA canonical successor.
2. Keep ERR-0075 closed unless a new exact full-pytest signature reproduces.
3. Keep ERR-0059 closed absent a new exact manifest regression and ERR-0054 UI/Visual-Review-owned.
4. Keep all currently green release guards closed.