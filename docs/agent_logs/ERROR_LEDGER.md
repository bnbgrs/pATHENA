# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@b2063a274984448d5f0db5d1c917c7ee93ae80be`; exact canonical Quality `34862330981 = SUCCESS`.
- `postmerge/errors@9511f2eea99264c6bca84fa1fd46558c7da041c8` before this refresh; no workflow run exists on that exact SHA.
- `postmerge/spec-core@1d1334d82af52f8055d7da06b2afa3db575eac4b`; exact Core Focused `34861762468 = SUCCESS`, exact canonical Quality `34861762425 = SUCCESS`.
- `postmerge/backend@b6cc4cf5a91816d946ca24f8f911a0470a13c280`; exact Backend Focused `34857759374 = SUCCESS`, exact canonical Quality `34857759296 = SUCCESS`.
- `postmerge/ui@a6298adb68af02537b87b26433003d830adb569d`; exact Core Focused `34864146634 = SUCCESS`, exact UI Focused `34864146677 = FAILURE`, exact canonical Quality `34864146660 = IN_PROGRESS`.
- On current UI canonical, Linux storage, Windows release guards including pypdf packaging, Local install/pypdf, specification validator, Ruff and mypy are already `SUCCESS`; full pytest remains active.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

No new Visual run exists yet on current UI SHA `a6298adb...`. The last exact reviewed UI Visual lineage proved the technical eleven-capture and route-identity pipeline but failed closed at the final visual verdict with `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`. Error worker must not create or accept a baseline. Closure still requires truthful UI-owned 11/11 reference/render review on a current exact candidate.

## IN_PROGRESS

### Current UI exact candidate qualification

Status: `IN_PROGRESS`

Owner: UI.

Current UI SHA `a6298adb...` is a successor of the prior red UI lineage. Exact Core Focused is green, UI Focused is red at `Run exact changed UI tests plus navigation invariant`, and canonical Quality is still running full pytest after all static/storage/install/release-guard lanes passed. Do not infer the old `ERR-0067`, `ERR-0068` or `ERR-0069` signatures onto this new SHA until exact current-SHA failure evidence identifies them.

### ERR-0067 — prior typography-token mismatch

Status: `IN_PROGRESS`

The prior UI SHA reproduced the `(15, 11, 30)` versus `(15, 12, 42)` typography-contract mismatch. Current UI `pathena_design_tokens.py` still contains `body_px=15`, `metadata_px=11`, `title_px=30`, but the current canonical pytest result is not terminal. Per exact-SHA policy, retain this only as a candidate signature pending current-run reproduction; do not call it current `OPEN` yet.

### ERR-0068 — prior offline-readiness copy mismatch

Status: `IN_PROGRESS`

The prior UI SHA reproduced `core-offline` with stale `Ask anything…` copy instead of `pATHENA reconnecting`. Current contract test still requires `pATHENA reconnecting`; current canonical pytest is still active. Await exact current-SHA failure/pass evidence before reclassifying.

### ERR-0069 — prior shell-density geometry mismatch

Status: `IN_PROGRESS`

The prior UI SHA reproduced composer height `118` against required `94`. Current UI Focused is exact red, but the available workflow job evidence only identifies the failing aggregate step, not the assertion. The current UI successor changes the adaptive layout refinement and its tests, so do not equate the red focused run with `ERR-0069` without exact assertion evidence.

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

### Error-worker inherited 48px UI geometry divergence

Status: `STALE`

Older Error-worker canonical red is inherited UI geometry against the authoritative 44px guard, not a new Error-owned root cause.

## Persistent release guards

Current Develop canonical is fully green. Current Spec/Core focused and canonical are fully green. Current Backend focused and canonical are fully green. On current UI, Linux storage, Windows release guards, Local install/pypdf, validator, Ruff and mypy are green while full pytest remains active. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Consume terminal current UI canonical `34864146660`; identify exact failing assertion(s) before reopening `ERR-0067`, `ERR-0068`, `ERR-0069` or creating a new UI cluster.
2. Consume the next current UI Visual candidate when one exists; UI owns truthful 11/11 review for `ERR-0054`.
3. Keep Develop, Spec/Core and Backend closed while their current exact evidence stays green.
4. Keep `ERR-0059`, `ERR-0063`, `ERR-0064`, `ERR-0065` and `ERR-0066` closed absent new exact regression.
