# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@aabca70e98d5fed5b47bf80d1ef1d691c9252c66` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@732bcbee50fc504aa8e80d5444f57f554a469f8f`; Backend Focused `35295570706 = SUCCESS`; canonical Quality `35295570667 = FAILURE`.
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
Exact reproduction: `postmerge/backend@732bcbee50fc504aa8e80d5444f57f554a469f8f`, canonical Quality `35295570667`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails with exactly one fixable `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_backup_verify_durable_service.py:1:1`. Exact diagnostics artifact `canonical-quality-diagnostics-732bcbee...` reproduces the same single failure. Current source has `athena.*` imports followed by `import pytest`; the Backend commit titled `apply Ruff canonical import ordering` therefore did not implement Ruff's actual canonical result. Backend owns the bounded file. No Error-worker parallel product mutation. Required action: run pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py`, consume the complete generated diff, and prove focused Ruff PASS before another canonical candidate.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
On exact Backend `732bcbee...`, Backend Focused and canonical full pytest are SUCCESS. The durable-service test module is green; no new exact-SHA contract regression is reproduced.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
On exact Backend `732bcbee...`, canonical full pytest is SUCCESS and no manifest-truth regression is reproduced. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `732bcbee...`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074` is the only current Backend Python-quality failure cluster on exact `732bcbee...`.
2. Backend owns the bounded test file; Error worker will not mutate it in parallel.
3. Backend must execute pinned Ruff 0.15.22 `check --fix` on the exact file and consume the complete generated transformation; hand-authored import permutations are no longer accepted as closure evidence.
4. Require focused Ruff + focused durable-service pytest PASS before canonical; close only on terminal exact-SHA canonical Ruff success.
5. Keep `ERR-0075`, `ERR-0059` and current release guards closed; `ERR-0054` remains UI/Visual-Review-owned.
