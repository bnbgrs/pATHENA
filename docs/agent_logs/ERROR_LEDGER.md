# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@2cef12125a3bb6bc9815c79a76c24f946a452ab6` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@629fcb0aaf523a73da6a6f379d2ff97dcf8f6aef`; Backend Focused `35194752034 = SUCCESS`; canonical Quality `35194752046 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no current Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
No Error-worker closure evidence. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@629fcb0aaf523a73da6a6f379d2ff97dcf8f6aef`, canonical Quality `35194752046`, Python 3.12 quality: Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS, full pytest SUCCESS. Backend Focused `35194752034` is SUCCESS. The current Backend commit `Backend: restore Ruff import sections` changes only `tests/unit/test_backup_verify_durable_service.py` (2 additions, 1 deletion): it moves `import pytest` before the `athena.*` imports and restores a blank section boundary. Canonical still rejects the candidate. This disproves that restored conventional section separation alone closes the defect. Previous exact candidates also rejected the opposite `athena.*` then `pytest` ordering and contiguous variants. Stop manual permutation. The authoritative next diagnostic is the actual pinned Ruff 0.15.22 `check --fix` transformation on this exact SHA, including any change outside the assumed pytest/athena boundary.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend full-pytest regression
Status: `FIXED`
Exact `629fcb0aaf523a73da6a6f379d2ff97dcf8f6aef` canonical full pytest is SUCCESS; no new pytest failure signature exists. Do not reopen absent a new exact-SHA pytest failure signature.

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
On exact Backend `629fcb0aaf523a73da6a6f379d2ff97dcf8f6aef`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. ERR-0074 is the sole current Backend Python-quality failure. Do not try another hand-written import permutation. Run the repository-pinned Ruff 0.15.22 fixer against exact `629fcb0a...` and inspect the complete generated diff.
2. Apply only that bounded generated fix, focused-verify Ruff plus the durable-service test, then consume one terminal exact-SHA canonical run.
3. Close ERR-0074 only on canonical Ruff SUCCESS.
4. Keep ERR-0075 and ERR-0059 closed absent new exact signatures; keep ERR-0054 UI/Visual-Review-owned.
5. Keep all currently green release guards closed.
