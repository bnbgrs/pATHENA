# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`; last exact Develop canonical Quality remains green.
- `postmerge/errors@678c941d6de2d73c0e1d34596dad7992a0b4f3b2` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@ab3cc6ba34de285dff3cc8d5e3581045a8cf9677`; Backend Focused `35055735369 = SUCCESS`; exact canonical Quality `35055735368 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no new current-SHA closure evidence established by Error worker.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
No Error-worker closure evidence. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff import-order failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@ab3cc6ba34de285dff3cc8d5e3581045a8cf9677`, canonical Quality `35055735368`, Python 3.12 quality. Specification validator, mypy and full pytest are green; Ruff alone fails. Canonical diagnostics contain exactly one Ruff error: `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`. The current import block places `import athena.jobs.backup_verify_durable_service as backup_verify_durable_service` before `import pytest`; Ruff requires canonical import ordering. This is the sole current canonical failure cluster. Minimal owner fix: apply Ruff's canonical import organization to that block only; no test, validation, guard, storage, recovery or security relaxation.

## IN_PROGRESS

### ERR-0067 — P2 — prior typography-token contract mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; reopen as current only if current exact canonical/focused evidence reproduces it.

### ERR-0068 — P2 — prior offline-readiness copy mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; reopen as current only from current exact evidence.

### ERR-0069 — P2 — prior shell-density composer geometry mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; do not infer it from a visual-verdict failure.

## FIXED / HELD CLOSED

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No current exact evidence reproduces the manifest-truth defect. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

### ERR-0072 — P1 — prior nonexistent-priority test contract
Status: `FIXED`
Not reproduced on current exact Backend SHA. Full canonical pytest is green on `ab3cc6ba...`; do not reopen from historical evidence.

### ERR-0073 — P1 — prior invalid backup.create delegation fixture
Status: `FIXED`
Not reproduced on current exact Backend SHA. Full canonical pytest is green on `ab3cc6ba...`; do not reopen from historical evidence.

- `ERR-0070` — `FIXED`.
- `ERR-0071` — `FIXED`.
- `ERR-0063` — `FIXED`.
- `ERR-0064` — `FIXED`.
- `ERR-0065` — `STALE`.
- `ERR-0066` — `FIXED`.
- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards

On exact Backend `ab3cc6ba...`, Linux storage regressions, Local-install Core/API restart + pypdf packaging, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are green. The canonical failure is isolated to Ruff I001 in one Backend unit-test import block. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Backend owns `ERR-0074`: canonicalize the import block in `tests/unit/test_backup_verify_durable_service.py`, run focused verification, then canonical Quality on the resulting exact SHA.
2. Error worker consumes the next exact-SHA result; close `ERR-0074` only when Ruff and canonical Quality are terminal green, otherwise classify only the new concrete exact-SHA signature.
3. Keep `ERR-0059` closed absent a new exact manifest regression and keep `ERR-0054` UI/Visual-Review-owned.
4. Keep all currently green release guards and canonical pytest/mypy/specification clusters closed.
