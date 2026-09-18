# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@a5ab9f4ecdd35b899dba9676a8c5574621e64604`; canonical Quality `35358305891 = SUCCESS` on this exact SHA.
- `postmerge/errors@bb1681625819f1dfc2065c7b1d999e5d40624dde` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@c8563285b2e27e774b5d7974650f9e8e0f084710`; Backend Focused `35391832466 = SUCCESS`; canonical Quality `35391832471 = SUCCESS`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; Develop contains the independently integrated 11-screen regression-baseline bundle, but native review remains `MATCH=0/11`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
Develop `a5ab9f4e...` is canonical Quality green, but its merge evidence explicitly states native review remains `MATCH=0/11`. This is not screenshot-parity closure. Error worker must not create or accept a baseline. UI/Visual Review must truthfully review the eleven original-reference + exact-render pairs.

## STALE
### ERR-0074 — former Backend canonical Ruff failure
Status: `STALE`
Former exact reproduction was on `postmerge/backend@72a3437dc756a42f85e049ecd575706c1a6ca9d1`. Current Backend exact SHA `c8563285b2e27e774b5d7974650f9e8e0f084710` has Backend Focused `35391832466 = SUCCESS` and canonical Quality `35391832471 = SUCCESS`. The former failing file `tests/unit/test_backup_verify_durable_service.py` no longer exists on the current Backend lineage. Do not reopen absent a new current exact-SHA Ruff failure signature.

### ERR-0075 — former Backend durable-service contract test regression
Status: `STALE`
Former exact reproduction was on `postmerge/backend@72a3437dc756a42f85e049ecd575706c1a6ca9d1`. Current Backend exact SHA `c8563285b2e27e774b5d7974650f9e8e0f084710` is canonical Quality green, and comparison from the former failing SHA shows `src/athena/jobs/backup_verify_durable_service.py`, `tests/unit/test_backup_verify_control_capability.py`, and `tests/unit/test_backup_verify_durable_service.py` removed on the current lineage. The historical constructor/test failures therefore are not current failures. Do not reopen absent a new current exact-SHA failure signature.

## FIXED / HELD CLOSED
### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No new exact-SHA manifest-truth regression is reproduced. Develop `a5ab9f4e...` canonical Quality is SUCCESS. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics. Do not reopen absent a new exact-SHA failure signature.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
Current Backend exact SHA `c8563285b2e27e774b5d7974650f9e8e0f084710` is canonical Quality SUCCESS. No current exact-SHA release-guard failure signature is reproduced. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. `ERR-0074` and `ERR-0075` are `STALE`; do not spend further work on their removed historical file unless a current exact-SHA regression reappears.
2. Inspect only newly reproduced current exact-SHA failures. Current Backend canonical is green, so do not reopen canonical-green Backend clusters.
3. `ERR-0059` remains `FIXED`; do not touch without new exact reproduction.
4. `ERR-0054` remains UI/Visual-Review-owned and `OPEN` because native review is still `MATCH=0/11`; Error worker only verifies evidence/closure status.
