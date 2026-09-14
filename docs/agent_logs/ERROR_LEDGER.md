# pATHENA Error Ledger

Evidence-first ledger for current exact-SHA failures. Historical IDs, old runs and priorities are non-authoritative unless reproduced on a current exact SHA.

## Current source of truth

- `develop/pathena-next@f8a25be7fd7df9f2a8ca281a1567f79ddaabcfb6`; exact canonical Quality `34883442620 = IN_PROGRESS`. Windows release guards, Linux storage regressions, Local install/pypdf, specification validator, Ruff and mypy are already `SUCCESS`; only canonical pytest remains active. Do not mutate or supersede this Develop candidate while active.
- `postmerge/errors@5b9788db2c3375c90967bf9633b82c5891827c78` before this refresh; no workflow exists on that exact Error-worker SHA.
- `postmerge/spec-core@63457beb6e96fb4dc48b3b1b217bcefab90c4a22`; exact Core Focused `34867476719 = SUCCESS`, exact canonical Quality `34867476727 = SUCCESS`.
- `postmerge/backend@bef909bf9097000142822e210cec5407e5f4f77b`; exact Backend Focused `34881627018 = SUCCESS`, exact canonical Quality `34881627010 = SUCCESS`.
- `postmerge/ui@a6298adb68af02537b87b26433003d830adb569d`; exact Core Focused `34864146634 = SUCCESS`, exact UI Focused remains `FAILURE`, exact canonical Quality `34864146660 = FAILURE`.
- Current UI canonical diagnostics on `a6298adb...` reproduce exactly three UI failures: typography `(15, 11, 30) != (15, 12, 42)`; offline-readiness placeholder `Ask anything… != pATHENA reconnecting`; shell-density composer height `118 != 94`. Full result: `3 failed, 5089 passed, 17 skipped`.
- No current exact evidence reproduces the persistent pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap guards.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## OPEN

### ERR-0054 — P2 — Windows visual baseline review incomplete

Status: `OPEN`

Owner: UI / Visual Review.

No trustworthy current exact UI Visual 11/11 review closes this item. Error worker must not create or accept a baseline. Closure requires opened original references and real exact-SHA render pairs reviewed truthfully by UI. No new UI Visual successor exists on the current UI head, so the technical capture/route cluster remains separately closed absent new exact reproduction.

### ERR-0067 — P2 — typography-token contract mismatch

Status: `OPEN`

Owner: UI.

Exact current-SHA canonical diagnostics on `a6298adb...` reproduce `tests/unit/test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales`: actual `(TYPE.body_px, TYPE.metadata_px, TYPE.title_px) = (15, 11, 30)`, required `(15, 12, 42)`. UI still owns the product correction; Error worker must not parallel-patch it.

### ERR-0068 — P2 — offline-readiness copy mismatch

Status: `OPEN`

Owner: UI.

Exact current-SHA canonical diagnostics on `a6298adb...` reproduce `tests/unit/test_pathena_offline_comprehension.py::test_readiness_copy_tracks_real_local_state`: actual placeholder `Ask anything…`, required `pATHENA reconnecting`. Static/storage/install/release-guard lanes are not implicated.

### ERR-0069 — P2 — shell-density composer geometry mismatch

Status: `OPEN`

Owner: UI.

Exact current-SHA canonical diagnostics on `a6298adb...` reproduce `tests/unit/test_pathena_shell_density.py::test_shell_density_converges_real_shell_to_reference_geometry`: composer height `118`, required `94`. This signature also explains the red UI-focused lineage; keep it deduplicated as one root cause.

## IN_PROGRESS

### Develop exact canonical qualification

Status: `IN_PROGRESS`

Current Develop `f8a25be7...` canonical Quality `34883442620` is active. Windows path safety/release guards, Linux storage regressions, Local install/pypdf, validator, Ruff and mypy are already green. Canonical pytest is the only active lane. Do not classify a new Error-owned cluster until terminal exact-SHA evidence exists.

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

Older Error-worker canonical red belongs to the currently isolated UI geometry/readiness failures and is not a new Error-owned root cause.

## Persistent release guards

Current Spec/Core and Backend exact focused/canonical evidence is green. Current Develop already has successful Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy while pytest is still running. Current UI canonical diagnostics isolate only the three UI assertions above after guard/static/storage/install lanes passed. Keep pypdf packaging, fail-closed Frozen argv, Desktop/Worker executable separation, single Desktop with bounded workers, adaptive 2048-context reserve, Windows lane-lock escalation, duplicate-column, Core-startup and storage-bootstrap protections unchanged.

## Next root cause

1. Consume terminal Develop canonical `34883442620`; only exact current-SHA failure evidence may open a new Error-owned cluster.
2. Consume the next UI successor and verify `ERR-0067`, `ERR-0068`, `ERR-0069` independently; do not parallel-patch UI-owned product code while UI owns those root causes.
3. Consume the next current UI Visual candidate when one exists; UI owns truthful 11/11 review for `ERR-0054`.
4. Keep Spec/Core and Backend closed while current exact evidence stays green.
5. Keep `ERR-0059`, `ERR-0063`, `ERR-0064`, `ERR-0065` and `ERR-0066` closed absent new exact regression.
