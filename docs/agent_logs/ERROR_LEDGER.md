# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@ba5e541f780c3b650060f8ac65085032873088a3`; exact canonical Quality `34871137412 = IN_PROGRESS`. This is the integrated UI PALLAS/ComfyUI shell candidate; do not mutate or supersede it while the run is active.
- `postmerge/errors@f06a13c3538143a80c1a7d58396bc71f6289a34a` before this refresh; no queued/in-progress workflow exists on that exact Error-worker SHA.
- `postmerge/spec-core@63457beb6e96fb4dc48b3b1b217bcefab90c4a22`; exact Core Focused `34867476719 = SUCCESS`, exact canonical Quality `34867476727 = SUCCESS`.
- `postmerge/backend@b6cc4cf5a91816d946ca24f8f911a0470a13c280`; exact Backend Focused `34857759374 = SUCCESS`, exact canonical Quality `34857759296 = SUCCESS`.
- `postmerge/ui@a6298adb68af02537b87b26433003d830adb569d`; exact Core Focused `34864146634 = SUCCESS`, exact UI Focused `34864146677 = FAILURE`, exact canonical Quality `34864146660 = FAILURE`.
- On current UI canonical, Linux storage, Windows release guards including pypdf packaging, Local install/pypdf, specification validator, Ruff and mypy are `SUCCESS`; failure is confined to canonical pytest/enforcement.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

No trustworthy current exact UI Visual 11/11 review closes this item. Error worker must not create or accept a baseline. Closure requires opened original references and real exact-SHA render pairs reviewed truthfully by UI. The technical capture/route cluster remains separate and closed absent a new exact Visual reproduction.

## IN_PROGRESS

### Current UI exact pytest qualification

Status: `IN_PROGRESS`

Owner: UI.

Current UI SHA `a6298adb...` is terminal red in UI Focused and canonical Quality. Exact job evidence proves UI Focused fails in `Run exact changed UI tests plus navigation invariant`; canonical proves only pytest/enforcement is red after all static/storage/install/release-guard lanes passed. Available exact job evidence does not expose the failing assertion text. Do not infer historical assertion signatures onto this SHA without direct exact-SHA evidence.

### ERR-0067 — prior typography-token mismatch

Status: `IN_PROGRESS`

The prior exact UI lineage reproduced the `(15, 11, 30)` versus `(15, 12, 42)` typography-contract mismatch. Current canonical is now terminal red, but the exact assertion has not been retrieved from current-SHA evidence in this run. Do not call this current `OPEN` until that assertion is directly reproduced.

### ERR-0068 — prior offline-readiness copy mismatch

Status: `IN_PROGRESS`

The prior exact UI lineage reproduced `core-offline` with stale `Ask anything…` copy instead of `pATHENA reconnecting`. Current canonical is terminal red, but current-SHA evidence available here does not identify that assertion. Retain as candidate signature only.

### ERR-0069 — prior shell-density geometry mismatch

Status: `IN_PROGRESS`

The prior exact UI lineage reproduced composer height `118` against required `94`. Current UI Focused is exact red, but the focused job exposes only the aggregate failing step. Current candidate's only tip commit adds a Ground-label stability test, while product refinement already sets `groundButton` text to `Ground`; no exact assertion output is available to equate the focused failure with ERR-0069. Retain as candidate signature only.

## FIXED / HELD CLOSED

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Capture-derived manifest fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS contract remain held. No current exact evidence reproduces the manifest-truth defect.

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

Current Spec/Core successor is exact Core Focused and canonical green. No matching current regression.

### ERR-0065 — P2 — prior Core Focused enforcement failure

Status: `FIXED`

Current Spec/Core exact focused and canonical evidence is green.

### ERR-0064 — P2 — Core Focused selector crossed ownership boundary

Status: `FIXED`

Bounded selector repair remains integrated; no current matching regression.

### ERR-0063 — P2 — UI capture/route failure

Status: `FIXED`

No current exact evidence reopens the prior capture/route failure. Do not reopen until a current Visual run reproduces it.

- `ERR-0062` — `FIXED`.
- `ERR-0060` — `FIXED`.
- `ERR-0061` — `FIXED`.
- Historical closed errors remain closed absent new exact reproduction.

## STALE / DEDUPLICATED CASCADES

### Error-worker inherited UI geometry divergence

Status: `STALE`

Older Error-worker canonical red belongs to UI geometry and is not a new Error-owned root cause.

## Persistent release guards

Current Spec/Core and Backend exact focused/canonical evidence is green. Current Develop canonical is still running. Current UI keeps Linux storage, Windows release guards, Local install/pypdf, validator, Ruff and mypy green while pytest is red. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Consume terminal Develop canonical `34871137412`; only exact current-SHA failure evidence may open a new Error-owned cluster.
2. On UI `a6298adb...`, obtain direct exact pytest assertion evidence before reopening `ERR-0067`, `ERR-0068`, `ERR-0069` or creating a new UI cluster.
3. Consume the next current UI Visual candidate when one exists; UI owns truthful 11/11 review for `ERR-0054`.
4. Keep Spec/Core and Backend closed while current exact evidence stays green.
5. Keep `ERR-0059`, `ERR-0063`, `ERR-0064`, `ERR-0065` and `ERR-0066` closed absent new exact regression.
