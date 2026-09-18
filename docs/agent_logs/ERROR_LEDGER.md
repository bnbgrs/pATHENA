# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs/runs are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth
- `develop/pathena-next@a5ab9f4ecdd35b899dba9676a8c5574621e64604`; latest known exact-SHA canonical Quality evidence remains SUCCESS.
- `postmerge/errors@3b64e08ffd742e92ed36873e31147d78c0645d04` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; no new current-SHA failure evidence.
- `postmerge/backend@93c4734582f18b3376b613187f4e6a237af7e708`; Backend Focused `35395605590 = SUCCESS`; canonical Quality `35395605359 = SUCCESS` on this exact SHA.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; Develop contains the integrated 11-screen regression-baseline bundle, but native review remains unclosed.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN
### ERR-0054 — P2 — Windows visual baseline review incomplete
Status: `OPEN`
Owner: UI / Visual Review.
Develop merge evidence explicitly states native review remains `MATCH=0/11`. The UI handoff likewise does not provide eleven reviewed current reference+render pairs. Error worker must not create or accept a baseline. UI/Visual Review must truthfully review all eleven pairs.

## STALE
### ERR-0074 — former Backend canonical Ruff failure
Status: `STALE`
Former reproduction was on `postmerge/backend@72a3437dc756a42f85e049ecd575706c1a6ca9d1`. Current Backend exact SHA `93c4734582f18b3376b613187f4e6a237af7e708` has Backend Focused `35395605590 = SUCCESS` and canonical Quality `35395605359 = SUCCESS`. Do not reopen absent a new current exact-SHA Ruff failure signature.

### ERR-0075 — former Backend durable-service contract test regression
Status: `STALE`
Former reproduction was on `postmerge/backend@72a3437dc756a42f85e049ecd575706c1a6ca9d1`. Current Backend exact SHA `93c4734582f18b3376b613187f4e6a237af7e708` is canonical Quality green and explicitly drops the obsolete durable-verify regression test. Do not reopen absent a new current exact-SHA failure signature.

## FIXED / HELD CLOSED
### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No new exact-SHA manifest-truth regression is reproduced. Preserve capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics. Do not reopen absent a new exact-SHA failure signature.

Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards
Current Backend exact SHA `93c4734582f18b3376b613187f4e6a237af7e708` is canonical Quality SUCCESS. No current exact-SHA release-guard failure signature is reproduced. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause
1. Consume only newly reproduced current exact-SHA failures; current Backend is canonical green.
2. Keep `ERR-0074` and `ERR-0075` `STALE` absent new exact reproduction.
3. Keep `ERR-0059 = FIXED` absent new exact manifest-truth evidence.
4. `ERR-0054` remains UI/Visual-Review-owned and `OPEN`; Error worker only verifies evidence/closure status.
