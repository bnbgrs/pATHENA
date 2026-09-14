# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@3a8120805e41d0fe9d283fc948d6e52b327a8e58`; exact canonical Quality `34893392725 = SUCCESS`. Its parent `ca8a213932d59c4e90dc573c4a3a970f10cc3c51` also completed canonical Quality `34890132641 = SUCCESS`.
- `postmerge/errors@4d0dce9be0cde1c9d91343394f4f3d91da7512f1` before this refresh; no queued/in-progress Error-worker workflow exists on that exact SHA.
- `postmerge/spec-core@9fe5dd44473ae200941d40ba37d14bc8816fdcdf`; exact Core Focused `34886553609 = SUCCESS`, exact canonical Quality `34886553447 = SUCCESS`.
- `postmerge/backend@44057bf0d93104992a825b0b611f04c2161d57fb`; exact Backend Focused `34893078182 = SUCCESS`, exact canonical Quality `34893078134 = SUCCESS`.
- `postmerge/ui@e149515870b773548a164658775159f29de323af`; latest exact current-SHA evidence remains Visual run `34888542153 = FAILURE`, with all technical stages through exact-eleven capture, route identity, compare/proposal and artifact upload `SUCCESS`; only `Enforce visual verdict` is `FAILURE`.
- The prior UI parent `a6298adb68af02537b87b26433003d830adb569d` reproduced product assertions `ERR-0067/0068/0069`; no canonical/focused run on current UI SHA `e1495158...` has reproduced those assertions.
- No current exact evidence reproduces the persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

Current exact UI Visual run `34888542153` on `e1495158...` proves the technical pipeline is healthy through exact-eleven native capture, route identity, comparator/proposal and artifact upload, then fails only at the fail-closed visual verdict. Current UI handoff remains `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11` and Visual readiness `NO`. Error worker must not create or accept a baseline. Closure requires UI to open original references and exact-SHA render pairs and review all eleven truthfully.

## IN_PROGRESS

### ERR-0067 — P2 — prior typography-token contract mismatch

Status: `IN_PROGRESS`

Owner: UI.

The assertion was reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only if current exact canonical/focused evidence reproduces it.

### ERR-0068 — P2 — prior offline-readiness copy mismatch

Status: `IN_PROGRESS`

Owner: UI.

The assertion was reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only from current exact canonical/focused evidence.

### ERR-0069 — P2 — prior shell-density composer geometry mismatch

Status: `IN_PROGRESS`

Owner: UI.

The assertion was reproduced on prior UI SHA `a6298adb...`, not on current exact UI SHA `e1495158...`. Reopen only from current exact canonical/focused evidence; do not infer it from the current visual-verdict failure.

## FIXED / HELD CLOSED

### Develop canonical qualification

Status: `FIXED`

Current Develop `3a812080...` canonical Quality `34893392725 = SUCCESS`; the previously active parent candidate `ca8a2139...` also closed canonical green. No Develop-owned error cluster is current.

### Backend current successor

Status: `FIXED`

Current Backend `44057bf0...` has exact Backend Focused `34893078182 = SUCCESS` and canonical Quality `34893078134 = SUCCESS`. No Backend/Storage/Recovery root cause is current.

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Current exact UI Visual run `34888542153` successfully captures exactly eleven canonical surfaces and verifies workspace route identity before comparison/verdict. Capture-derived manifest fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS contract remain held. No current exact evidence reproduces the manifest-truth defect.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

Current exact UI Visual run explicitly passes exact-eleven capture and route identity on `e1495158...`; the later visual-verdict failure is review/baseline-owned and must not reopen this technical cluster.

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

Current Spec/Core exact focused and canonical evidence is green. No matching current regression.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `FIXED`

Current Spec/Core exact focused and canonical evidence is green.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

Bounded selector repair remains integrated; no current matching regression.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Prior UI canonical/focused aggregate failure

Status: `STALE`

The aggregate red state on `a6298adb...` was decomposed into `ERR-0067/0068/0069`. On current UI SHA `e1495158...`, current evidence is only the Visual review verdict failure. Do not create a new cascade ID from that verdict.

## Persistent release guards

Develop, Spec/Core and Backend are current exact canonical green. Current UI Visual evidence preserves exact-eleven capture and route identity. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Consume the next current-SHA UI canonical/focused evidence when produced for `e1495158...`; reclassify `ERR-0067/0068/0069` independently from direct exact assertions.
2. Keep `ERR-0054` UI/Visual-Review-owned; no Error-worker baseline acceptance.
3. Keep Develop, Spec/Core and Backend closed while their current exact evidence remains green.
4. Keep `ERR-0059`, `ERR-0063`, `ERR-0064`, `ERR-0065` and `ERR-0066` closed absent new exact regression.
5. If a new worker successor appears, qualify its exact focused/canonical state before using historical IDs or priorities.
