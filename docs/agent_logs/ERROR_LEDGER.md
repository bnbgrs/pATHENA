# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`; unchanged.
- `postmerge/errors@12953c718fe69ffa835eb7f39ad6d10d18bd83b9` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@7e6274d05b431356b5d0b99175b6105a6ebd4220`; Backend Focused `35087092246 = SUCCESS`; exact canonical Quality `35087092238 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no new Error-worker closure evidence.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
No Error-worker closure evidence. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff import-order failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@7e6274d05b431356b5d0b99175b6105a6ebd4220`, canonical Quality `35087092238`, Python 3.12 quality. Specification validator and mypy are green; Ruff fails. The bounded candidate commit changes only `tests/unit/test_backup_verify_durable_service.py` import sections, placing `pytest` between stdlib and `athena.*`, but canonical Ruff still fails. Repository pins Ruff `0.15.22` and enables `I` rules. Do not guess another manual ordering; derive the exact patch from the pinned Ruff fixer/check. No test, validation, guard, storage, recovery or security relaxation.

### ERR-0075 — P1 — current full-pytest regression on Backend exact SHA
Status: `IN_PROGRESS`
Owner: Backend / exact diagnostics.
Exact reproduction: `postmerge/backend@7e6274d05b431356b5d0b99175b6105a6ebd4220`, canonical Quality `35087092238`, Python 3.12 quality `Quality — pytest = FAILURE`. This is current exact-SHA evidence and therefore supersedes the older ledger statement that full pytest was green. The available GitHub Actions job metadata proves the failure but does not expose the failing test name/assertion; canonical diagnostics artifact `canonical-quality-diagnostics-7e6274d05b431356b5d0b99175b6105a6ebd4220` exists and must be inspected before assigning a narrower root cause. Do not infer that this is a Ruff cascade.

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
Historical closure retained only because no current exact evidence identifies this signature. The current full-pytest failure is tracked separately as ERR-0075 until exact diagnostics identify its signature.

### ERR-0073 — P1 — prior invalid backup.create delegation fixture
Status: `FIXED`
Historical closure retained only because no current exact evidence identifies this signature. Do not reopen it merely because full pytest is red; require exact matching diagnostics.

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

On exact Backend `7e6274d0...`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are green. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Inspect the exact canonical diagnostics artifact for `7e6274d0...` and identify ERR-0075's failing pytest node/assertion before any product or test mutation.
2. Backend owns ERR-0074: use repository-pinned Ruff 0.15.22 to generate the exact canonical import organization; do not alter test semantics while fixing I001.
3. Consume the next exact Backend SHA; close each cluster only on matching terminal evidence.
4. Keep ERR-0059 closed absent a new exact manifest regression and keep ERR-0054 UI/Visual-Review-owned.
5. Keep all currently green release guards closed.