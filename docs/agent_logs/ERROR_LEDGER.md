# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@587f6a1cca676a92af696ccb2ee1194a63aba41a` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@b88399f2a7121f54a071dd770a28419621ff428d`; Backend Focused `35215567439 = SUCCESS`; canonical Quality `35215567394 = FAILURE`.
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
Exact reproduction: `postmerge/backend@b88399f2a7121f54a071dd770a28419621ff428d`, canonical Quality `35215567394`, Python 3.12 quality: Specification Validator SUCCESS, Ruff FAILURE, mypy SUCCESS, full pytest SUCCESS. Backend Focused `35215567439` is SUCCESS. Fresh canonical diagnostics contain exactly one `I001 [*] Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`, covering lines 1-14. The current candidate already has the long `BackupDeepVerifyDurableJobService` import wrapped, but places `import pytest` after all `athena.*` from-imports. This proves the prior partial formatting slice was insufficient. Earlier candidates separately exercised pytest-before-athena, blank-section, contiguous, opposite-order, and pre-wrap variants; no one exact candidate combined the current wrapped import with the likely same-section Ruff ordering. Do not reopen unrelated product/runtime code. Backend must obtain/apply the complete pinned Ruff 0.15.22 fixer result in one shot; if reproducing manually is unavoidable, the only still-untried bounded combination supported by current evidence is `import pytest` immediately before the wrapped `athena.*` imports with no blank separator, then focused Ruff must prove it before canonical.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend full-pytest regression
Status: `FIXED`
Exact `b88399f2a7121f54a071dd770a28419621ff428d` canonical full pytest is SUCCESS; no new pytest failure signature exists. Do not reopen absent a new exact-SHA pytest failure signature.

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
On exact Backend `b88399f2a7121f54a071dd770a28419621ff428d`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. ERR-0074 is the sole current Backend Python-quality failure. Consume/apply the complete repository-pinned Ruff 0.15.22 fixer transformation for exact `b88399f2...`; do not make another partial permutation.
2. Focused-verify Ruff plus the durable-service test. Only a focused Ruff PASS justifies a new canonical candidate.
3. Close ERR-0074 only on terminal exact-SHA canonical Ruff SUCCESS.
4. Keep ERR-0075 and ERR-0059 closed absent new exact signatures; keep ERR-0054 UI/Visual-Review-owned.
5. Keep all currently green release guards closed.
