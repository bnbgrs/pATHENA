# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`.
- `postmerge/errors@63eb81f3d8710e91816af21a5474b301a5837b59` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@d8238749500ac13b8072564bf05437ea9025af9b`; Backend Focused `35299441096 = SUCCESS`; canonical Quality `35299441030 = FAILURE`.
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
Exact reproduction: `postmerge/backend@d8238749500ac13b8072564bf05437ea9025af9b`, canonical Quality `35299441030`, Python 3.12 quality. Specification validator, mypy and full pytest are SUCCESS; Ruff alone fails. Backend Focused `35299441096` is SUCCESS. Current commit `d823874...` is titled `apply exact Ruff import fix`, but canonical Ruff still fails, so the title is not closure evidence.

New bounded root-cause evidence from the exact source and predecessor: `d823874...` places `import pytest` before `athena.*` but inserts a blank line between them. Its predecessor `732bcbee...` had `athena.*` followed by `import pytest` with no blank line and also failed Ruff. Therefore two dimensions were changed separately and neither candidate tested the remaining combined state: `import pytest` followed immediately by the `athena.*` imports in the same import section, with no blank separator. This is the only bounded import-section combination not excluded by the current exact candidates. Backend owns the file; Error worker must not mutate it in parallel. Required action: execute pinned Ruff 0.15.22 locally on the exact file and consume its complete generated diff; if direct execution remains unavailable, test only the remaining combined state above. Require focused Ruff PASS before another canonical candidate.

## FIXED / HELD CLOSED
### ERR-0075 — P1 — Backend durable-service contract regression
Status: `FIXED`
On exact Backend `d823874...`, Backend Focused and canonical full pytest are SUCCESS. The durable-service test module has no new exact-SHA contract regression.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
On exact Backend `d823874...`, canonical full pytest is SUCCESS and no manifest-truth regression is reproduced. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
On exact Backend `d823874...`, Linux storage regressions, Local-install smoke, and Windows path/storage/durable-filesystem/API-boundary/ownership/packaged-runtime/adaptive-chat/restart/pypdf guards are SUCCESS. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074` remains the only current Backend Python-quality failure cluster on exact `d823874...`.
2. Backend owns the bounded test file; Error worker will not mutate it in parallel.
3. Preferred closure: execute pinned Ruff 0.15.22 `check --fix tests/unit/test_backup_verify_durable_service.py` and consume the complete generated transformation.
4. If direct fixer execution is unavailable, the only current bounded combination not excluded by exact candidates is `import pytest` immediately followed by `athena.*` imports with no blank separator.
5. Require focused Ruff + focused durable-service pytest PASS before canonical; close only on terminal exact-SHA canonical Ruff success.
6. Keep `ERR-0075`, `ERR-0059` and current release guards closed; `ERR-0054` remains UI/Visual-Review-owned.
