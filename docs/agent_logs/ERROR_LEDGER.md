# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`; unchanged.
- `postmerge/errors@0e3c717c6c64c80edce75e54a77213a8edc174ef` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@868f089215444e4292c7de50664e1d514eff2ac7`; Backend Focused `35115493099 = SUCCESS`; exact canonical Quality `35115492992 = FAILURE`.
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
Exact reproduction: `postmerge/backend@868f089215444e4292c7de50664e1d514eff2ac7`, canonical Quality `35115492992`, Python 3.12 quality. Specification validator and mypy are green; Ruff fails. Backend Focused is green. Do not infer closure from focused success. Use repository-pinned Ruff output and do not relax tests or guards.

### ERR-0075 — P1 — current full-pytest regression on Backend exact SHA
Status: `IN_PROGRESS`
Owner: Backend / exact diagnostics.
Exact reproduction: `postmerge/backend@868f089215444e4292c7de50664e1d514eff2ac7`, canonical Quality `35115492992`, `Quality — pytest = FAILURE`. Diagnostics artifact `canonical-quality-diagnostics-868f089215444e4292c7de50664e1d514eff2ac7` exists. The current Backend commit `Backend: repair durable service regression harness` changes only `tests/unit/test_backup_verify_durable_service.py`, but substantially: 47 additions / 32 deletions, replacing submit-occurrence contract tests with repository-backed create-contract tests. This is strong locality evidence, not sufficient to invent the failing node/assertion. Keep ERR-0075 independent until exact diagnostics identify the signature.

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
No current exact diagnostics identify this signature. Do not reopen merely because full pytest is red.

### ERR-0073 — P1 — prior invalid backup.create delegation fixture
Status: `FIXED`
No current exact diagnostics identify this signature. Do not reopen merely because full pytest is red.

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

On exact Backend `868f0892...`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are green. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Inspect exact canonical diagnostics for `868f0892...` and identify ERR-0075's failing pytest node/assertion before any Error-worker product/test mutation.
2. Backend owns ERR-0074; consume only a terminal exact-SHA canonical successor before closure.
3. Treat the 79-line durable-service harness rewrite as locality evidence for ERR-0075, not proof of its exact signature.
4. Keep ERR-0059 closed absent a new exact manifest regression and ERR-0054 UI/Visual-Review-owned.
5. Keep all currently green release guards closed.