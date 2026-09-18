# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@8422e225c0922c52c7c9a3f141d7830bd2551de8` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@f6d90e5070027357b19bf78647db7725e26d0dd2`; Backend Focused `35314812669 = SUCCESS`; canonical Quality `35314812695 = FAILURE`.
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
Exact reproduction: `postmerge/backend@f6d90e5070027357b19bf78647db7725e26d0dd2`, canonical Quality `35314812695`, Python 3.12 quality. Specification validator and mypy are SUCCESS; Ruff still fails with one fixable `I001` in `tests/unit/test_backup_verify_durable_service.py`. Backend Focused `35314812669` is SUCCESS. Windows path safety, Linux storage regressions and Local-install smoke are SUCCESS.

The exact commit inserts a blank first-party boundary between `import pytest` and `import athena.jobs.backup_verify_durable_service as durable_service`; canonical Ruff still rejects the import block. Repeated hand-authored import permutations remain non-closure evidence. Backend owns this file; Error worker must not mutate it in parallel. Required action: run repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` on the exact source, preserve the complete generated diff, and require focused Ruff PASS before another canonical candidate.

### ERR-0075 — P1 — Backend durable-service contract regression
Status: `OPEN`
Owner: Backend.
Reopened only because it is newly reproduced on exact Backend `f6d90e5070027357b19bf78647db7725e26d0dd2`, canonical `35314812695`: full pytest reports `2 failed, 5329 passed, 17 skipped`. Both failures are in `tests/unit/test_backup_verify_durable_service.py` and were introduced by the current Backend commit while editing the same bounded file.

Exact root-cause evidence: production persists `pinned_configuration_json` as `{"pipeline_version":"backup-deep-verify-v1"}`, while the test was changed to expect `{"pipeline_version":1}`. The same commit changed the invalid-version test to `BACKUP_VERIFY_DEEP_PIPELINE_VERSION + 1`, but the constant is a string, producing `TypeError: can only concatenate str (not "int") to str` before the intended service validation. Restore the production-contract assertions/invalid string value; do not change production semantics, guards, or validation to satisfy these erroneous test expectations. Require focused durable-service pytest PASS and full canonical pytest PASS for closure.

## FIXED / HELD CLOSED
### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
On exact Backend `f6d90e5070027357b19bf78647db7725e26d0dd2`, `tests/qa/test_visual_capture_manifest_truth.py` passes in canonical full pytest. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `f6d90e5070027357b19bf78647db7725e26d0dd2`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0075`: Backend must first revert the two newly introduced test-contract errors on exact `f6d90e...`: expect the string pipeline version and use a wrong string pipeline version for the invalid-input case. Focused durable-service pytest must PASS.
2. `ERR-0074`: in the same bounded file, execute pinned Ruff 0.15.22 `check --fix` and consume its exact import transformation; focused Ruff must PASS.
3. Only after both focused checks pass should Backend produce another canonical candidate. Close each error only from terminal exact-SHA canonical evidence.
4. Keep `ERR-0059` and current release guards closed. `ERR-0054` remains UI/Visual-Review-owned.