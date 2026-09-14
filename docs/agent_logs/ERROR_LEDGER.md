# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@42614da4d235c2613b7a683d357a5af17a271817`; exact canonical Quality `34876523610 = IN_PROGRESS`. Do not mutate or supersede while active.
- `postmerge/errors@6eb07f7aec9a109f6f3875540a013c01afc9e7fa` before this refresh; no workflow exists on that exact Error-worker SHA.
- `postmerge/spec-core@63457beb6e96fb4dc48b3b1b217bcefab90c4a22`; exact Core Focused `34867476719 = SUCCESS`, exact canonical Quality `34867476727 = SUCCESS`.
- `postmerge/backend@379b968f63e42e293ded342fa65bac557f1ef993`; exact Backend Focused `34875026423 = SUCCESS`, exact canonical Quality `34875026503 = SUCCESS`.
- `postmerge/ui@a6298adb68af02537b87b26433003d830adb569d`; exact Core Focused `34864146634 = SUCCESS`, exact UI Focused `34864146677 = FAILURE`, exact canonical Quality `34864146660 = FAILURE`.
- Current UI canonical diagnostics artifact `canonical-quality-diagnostics-a6298adb68af02537b87b26433003d830adb569d` reproduces exactly three failures: typography `(15, 11, 30) != (15, 12, 42)`; offline-readiness placeholder `Ask anything… != pATHENA reconnecting`; shell-density composer height `118 != 94`. Full result: `3 failed, 5089 passed, 17 skipped`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

No trustworthy current exact UI Visual 11/11 review closes this item. Error worker must not create or accept a baseline. Closure requires opened original references and real exact-SHA render pairs reviewed truthfully by UI. The technical capture/route cluster remains separate and closed absent a new exact Visual reproduction.

### ERR-0067 — P2 — typography-token contract mismatch

Status: `OPEN`

Owner: UI.

Exact current-SHA canonical diagnostics on `a6298adb...` reproduce `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales`: actual `(TYPE.body_px, TYPE.metadata_px, TYPE.title_px) = (15, 11, 30)`, required `(15, 12, 42)`. This is current evidence, not a historical carry-forward. Error worker must not patch UI product code in parallel while UI owns the same root cause.

### ERR-0068 — P2 — offline-readiness copy mismatch

Status: `OPEN`

Owner: UI.

Exact current-SHA canonical diagnostics on `a6298adb...` reproduce `tests/unit/test_pathena_offline_comprehension.py::test_readiness_copy_tracks_real_local_state`: actual placeholder `Ask anything…`, required `pATHENA reconnecting`. Static/storage/install/release-guard lanes remain green, so this is isolated to UI/readiness behavior rather than a release-guard cascade.

### ERR-0069 — P2 — shell-density composer geometry mismatch

Status: `OPEN`

Owner: UI.

Exact current-SHA canonical diagnostics on `a6298adb...` reproduce `tests/unit/test_pathena_shell_density.py::test_shell_density_converges_real_shell_to_reference_geometry`: composer height `118`, required `94`. This signature also explains the currently red UI-focused lineage; deduplicate it as one root cause rather than opening a second cascade ID.

## IN_PROGRESS

### Develop exact canonical qualification

Status: `IN_PROGRESS`

Current Develop `42614da4...` canonical Quality `34876523610` is active. No Error-owned classification until terminal exact-SHA evidence exists.

## FIXED / HELD CLOSED

### ERR-0059 — P2 — manifest capture truth

Status: `FIXED`

Capture-derived manifest fields, `assigned_reference_count = 11`, and exact-eleven fail-closed PASS contract remain held. No current exact evidence reproduces the manifest-truth defect.

### ERR-0066 — P2 — supersession registry contract regression

Status: `FIXED`

Current Spec/Core exact focused and canonical evidence remains green. No matching current regression.

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

Current Spec/Core and Backend exact focused/canonical evidence is green. Current Develop canonical is still running. Current UI canonical diagnostics isolate only the three UI assertions above after storage, Windows release guards, Local install/pypdf, validator, Ruff and mypy passed. No current exact evidence reopens pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup or storage-bootstrap failures. Keep all guards unchanged.

## Next root cause

1. Consume terminal Develop canonical `34876523610`; only exact current-SHA failure evidence may open a new Error-owned cluster.
2. Consume the next UI successor and verify `ERR-0067`, `ERR-0068`, `ERR-0069` independently; do not parallel-patch UI-owned product code while UI owns those root causes.
3. Consume the next current UI Visual candidate when one exists; UI owns truthful 11/11 review for `ERR-0054`.
4. Keep Spec/Core and Backend closed while current exact evidence stays green.
5. Keep `ERR-0059`, `ERR-0063`, `ERR-0064`, `ERR-0065` and `ERR-0066` closed absent new exact regression.
