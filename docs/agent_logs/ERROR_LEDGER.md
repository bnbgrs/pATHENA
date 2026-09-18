# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@a5ab9f4ecdd35b899dba9676a8c5574621e64604`; this is Merge PR #236 for the 11-screen UI reference-parity bundle. Its canonical Quality run `35358305891` is currently `IN_PROGRESS`, so no terminal Develop PASS/FAIL is claimed yet.
- `postmerge/errors@21d005ad71c300416a167ced377fb99031207f91` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@6538aef5ad8c5b2b1e1814e5f77af4da221ef050`; Backend Focused `35356534233 = SUCCESS`; canonical Quality `35356534227 = FAILURE`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; Develop now contains the independently integrated 11-screen bundle, but native review remains `MATCH=0/11`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
Develop merge `a5ab9f4e...` records exact pre-merge Visual 11/11, UI Focused and Quality successes for the integrated regression-baseline bundle, but explicitly states native review remains `MATCH=0/11`. This is not screenshot-parity closure. Error worker must not create or accept a baseline. UI/Visual Review must open and truthfully review the eleven original-reference + exact-render pairs.

### ERR-0074 — P1 — Backend canonical Ruff failure
Status: `OPEN`
Owner: Backend.
Exact reproduction: `postmerge/backend@6538aef5ad8c5b2b1e1814e5f77af4da221ef050`, canonical Quality `35356534227`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails. Backend Focused `35356534233` is SUCCESS. Linux storage regressions, Local-install smoke and Windows path safety are SUCCESS.

Canonical diagnostics artifact `canonical-quality-diagnostics-6538aef5...` contains exactly one Ruff failure: fixable `I001` at `tests/unit/test_backup_verify_durable_service.py:1:1`. Exact source currently places all `athena.*` imports before `import pytest`; the diagnostic explicitly says `Organize imports` and `1 fixable with --fix`. Repeated hand-authored import permutations remain non-closure evidence. Backend owns this file; Error worker must not mutate it in parallel. Required action remains actual repository-pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, complete generated diff, focused Ruff PASS, then exact canonical verify.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
Canonical `35356534227` full pytest is SUCCESS on exact Backend `6538aef5...`; no new durable-service contract failure is reproduced. Do not reopen absent a new exact-SHA failure signature.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No new exact-SHA manifest-truth regression is reproduced on Backend `6538aef5...`; full canonical pytest is green. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics. The new Develop UI bundle does not supply a new ERR-0059 failure signature.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `6538aef5ad8c5b2b1e1814e5f77af4da221ef050`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074`: Backend must execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` and consume the complete generated transformation; focused Ruff PASS required.
2. Do not start a competing canonical run while Develop `35358305891` is in progress. Consume its terminal exact-SHA result next.
3. `ERR-0075` and `ERR-0059` remain FIXED; do not touch without new exact reproduction.
4. `ERR-0054` remains UI/Visual-Review-owned and OPEN because native review is still `MATCH=0/11`; Error worker only verifies evidence/closure status.
