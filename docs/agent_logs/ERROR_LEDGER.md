# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@03157f15246c8acb0f51a30631bf45c4d2a72416`; exact canonical Quality `34954990041 = SUCCESS`.
- `postmerge/errors@20b380eaed63a2654e7d99d71fd630b2647fd121` before this refresh.
- `postmerge/spec-core@6dddda87919cc5363ccf664863f6b4dca83784ed`; previously exact green; no new current-SHA failure evidence.
- `postmerge/backend@fba3cc935dc85e89af993995a17b542db5500ee9`; exact Backend Focused `34963193093 = SUCCESS`; exact canonical Quality `34963193081 = SUCCESS`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no new current-SHA canonical/focused product assertion evidence established by the Error worker.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

No Error-worker closure evidence. Error worker must not create or accept a baseline. Closure requires truthful review of all eleven original-reference + exact-render pairs.

## IN_PROGRESS

### ERR-0067 — P2 — prior typography-token contract mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; reopen only if current exact canonical/focused evidence reproduces it.

### ERR-0068 — P2 — prior offline-readiness copy mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; reopen only from current exact canonical/focused evidence.

### ERR-0069 — P2 — prior shell-density composer geometry mismatch
Status: `IN_PROGRESS`
Owner: UI.
Reproduced on prior UI SHA only; do not infer it from a visual-verdict failure.

## FIXED / HELD CLOSED

### Develop current successor
Status: `FIXED`
Current Develop `03157f15...` completed exact canonical Quality `34954990041 = SUCCESS`. The integrated deep-verify CONTROL route introduces no current exact-SHA failure cluster.

### Backend current successor
Status: `FIXED`
Current Backend `fba3cc93...` completed Backend Focused `34963193093 = SUCCESS` and canonical Quality `34963193081 = SUCCESS`. The durable deep-verify service adapter introduces no current Backend/Storage/Recovery root cause.

### ERR-0059 — P2 — manifest capture truth
Status: `FIXED`
No current exact evidence reproduces the manifest-truth defect. Capture-derived manifest truth, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics remain unchanged.

### ERR-0070 — P2 — Core focused selector contract drift after Research expansion
Status: `FIXED`
No current exact Spec/Core regression evidence.

### ERR-0071 — P2 — focused mypy/package-resolution candidate
Status: `FIXED`
No current exact Spec/Core regression evidence.

- `ERR-0063` — `FIXED`.
- `ERR-0064` — `FIXED`.
- `ERR-0065` — `STALE`.
- `ERR-0066` — `FIXED`.
- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards

Develop and Backend are current exact canonical green; Spec/Core has no new current-SHA failure evidence. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Consume any new current-SHA UI canonical/focused evidence; reclassify `ERR-0067/0068/0069` independently from direct assertions only.
2. Keep `ERR-0054` UI/Visual-Review-owned; no Error-worker baseline acceptance.
3. Keep `ERR-0059`, `ERR-0070`, `ERR-0071`, Develop and Backend closed absent a new exact regression.
4. On any new worker/develop successor, consume exact-SHA canonical/focused evidence before reopening historical IDs.
