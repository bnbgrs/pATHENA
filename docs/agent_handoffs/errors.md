# Error worker handoff

## Exact source of truth

- Develop: `f8a25be7fd7df9f2a8ca281a1567f79ddaabcfb6`; canonical Quality `34883442620 = IN_PROGRESS`. Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy are already `SUCCESS`; canonical pytest remains active.
- Error worker before this handoff refresh: `d4687c945df1c14f1e47321ef8f04d48a2a537e0`; no workflow existed on that exact SHA before this commit.
- Spec/Core: `63457beb6e96fb4dc48b3b1b217bcefab90c4a22`; Core Focused `34867476719 = SUCCESS`; canonical `34867476727 = SUCCESS`.
- Backend: `bef909bf9097000142822e210cec5407e5f4f77b`; Backend Focused `34881627018 = SUCCESS`; canonical `34881627010 = SUCCESS`.
- UI: `a6298adb68af02537b87b26433003d830adb569d`; Core Focused `34864146634 = SUCCESS`; UI Focused remains `FAILURE`; canonical `34864146660 = FAILURE`.
- Exact UI canonical diagnostics reproduce exactly three assertions: typography `(15, 11, 30)` versus `(15, 12, 42)`; offline placeholder `Ask anything…` versus `pATHENA reconnecting`; composer height `118` versus `94`. Full pytest result remains `3 failed, 5089 passed, 17 skipped`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Develop — IN_PROGRESS

Exact canonical Quality `34883442620` is active on current Develop. No competing canonical run was started. All visible guard/static/storage/install lanes are green; only full pytest remains active. Do not supersede or classify from historical signatures before terminal evidence.

## Spec/Core — held closed

Current Spec/Core exact Core Focused and canonical are both green. Prior Core error clusters remain closed.

## Backend — held closed

Current Backend successor `bef909bf...` is exact Backend Focused and canonical green. No current Storage/Recovery/backup root cause is reproduced. The older backend handoff text is historical relative to the current exact CI evidence and must not override these current runs.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS remain held.

## Current UI exact regressions — OPEN / UI-owned

Current exact UI canonical diagnostics on `a6298adb...` still directly reproduce:

- `ERR-0067 = OPEN`: `test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales` — actual `(15, 11, 30)` versus required `(15, 12, 42)`.
- `ERR-0068 = OPEN`: `test_pathena_offline_comprehension.py::test_readiness_copy_tracks_real_local_state` — actual `Ask anything…` versus required `pATHENA reconnecting`.
- `ERR-0069 = OPEN`: `test_pathena_shell_density.py::test_shell_density_converges_real_shell_to_reference_geometry` — composer height `118` versus required `94`.

The red UI-focused lineage remains deduplicated under `ERR-0069` rather than opening another shell-density ID. Error worker must not parallel-patch UI-owned product code while UI owns these fixes.

## ERR-0054 — OPEN — UI/Visual Review

No newer UI Visual run exists on the current UI head and no trustworthy current exact 11/11 review closes this item. Error worker does not create or accept a baseline. UI must provide current exact native artifacts and truthful reference/render review before closure.

## Persistent guards

No current exact evidence reopens pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap clusters. Current Develop has already passed Windows release guards, Linux storage, Local install/pypdf, validator, Ruff and mypy. Keep all guards unchanged.

## Next root cause

1. Consume terminal Develop canonical `34883442620` without superseding the candidate.
2. If Develop is green, keep its integrated Knowledge-read slice closed and move immediately to the next current exact failure cluster.
3. Consume the next UI successor and requalify `ERR-0067`, `ERR-0068`, `ERR-0069` independently from exact assertion evidence.
4. Keep Spec/Core and Backend closed while their current exact evidence remains green.
5. Keep `ERR-0059` and prior closed harness/Core clusters closed absent exact regression.
6. `ERR-0054` remains strictly UI/Visual-Review-owned until truthful current 11/11 review evidence exists.
