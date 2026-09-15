# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@7b1a1c1dc045f54a74e4ed005abf434f2e2d313c`; exact canonical Quality `34910867498 = IN_PROGRESS`.
- `postmerge/errors@d081508a572556852099cb8d91c30e05cbd9dc66` before this refresh.
- `postmerge/spec-core@52c4592efeeebec7c1ed3d70949a084b3d8c205f`; exact Core Focused `34908178408 = SUCCESS`; exact canonical Quality `34908178528 = SUCCESS`.
- `postmerge/backend@2e42476fdbb276741eed38fbe829e2ad3bbd56a5`; exact Backend Focused `34909172871 = SUCCESS`; exact canonical Quality `34909172865 = SUCCESS`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; no new current-SHA canonical/focused product assertion evidence; latest exact UI evidence remains the fail-closed visual-review path.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

No new closure evidence. Error worker must not create or accept a baseline. Closure still requires truthful review of all eleven original-reference + exact-render pairs.

## IN_PROGRESS

### ERR-0067 — P2 — prior typography-token contract mismatch

Status: `IN_PROGRESS`

Owner: UI.

Reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only if current exact canonical/focused evidence reproduces it.

### ERR-0068 — P2 — prior offline-readiness copy mismatch

Status: `IN_PROGRESS`

Owner: UI.

Reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only from current exact canonical/focused evidence.

### ERR-0069 — P2 — prior shell-density composer geometry mismatch

Status: `IN_PROGRESS`

Owner: UI.

Reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Do not infer it from the visual-verdict failure.

## FIXED / HELD CLOSED

### ERR-0070 — P2 — Core focused selector contract drift after Research expansion

Status: `FIXED`

Exact successor `postmerge/spec-core@52c4592e...` is green in both Core Focused `34908178408` and canonical Quality `34908178528`. The Research qualification regression is closed on the same exact SHA.

### ERR-0071 — P2 — focused mypy/package-resolution candidate

Status: `FIXED`

Exact successor `52c4592e...` is green in Core Focused and canonical Quality. No current failure signature remains; the prior focused typing/package-resolution candidate is closed.

### Backend current successor

Status: `FIXED`

Current Backend `2e42476f...` has exact Backend Focused `34909172871 = SUCCESS` and canonical Quality `34909172865 = SUCCESS`. No Backend/Storage/Recovery root cause is current.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

No current exact evidence reproduces the manifest-truth defect. Capture-derived manifest truth, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS semantics remain unchanged.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

No new exact current-SHA technical capture/route regression is reproduced.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

The Research selector expansion is intentional Core ownership, not recurrence of the old cross-ownership defect.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `STALE`

A generic enforcement conclusion is not itself a root cause; the successor is now exact green.

- `ERR-0066` — `FIXED`.
- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## Persistent release guards

Spec/Core and Backend are current exact focused + canonical green. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Consume terminal canonical Quality `34910867498` for `develop/pathena-next@7b1a1c1d...`; do not supersede while it is running.
2. Consume any new current-SHA UI canonical/focused evidence for `e1495158...`; reclassify `ERR-0067/0068/0069` independently from direct assertions only.
3. Keep `ERR-0054` UI/Visual-Review-owned; no Error-worker baseline acceptance.
4. Keep `ERR-0059`, `ERR-0070`, `ERR-0071`, Spec/Core and Backend closed absent a new exact regression.
