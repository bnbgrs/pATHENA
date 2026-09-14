# Error worker handoff

## Exact source of truth

- Develop: `42614da4d235c2613b7a683d357a5af17a271817`; canonical `34876523610 = IN_PROGRESS`.
- Error worker before this run: `6eb07f7aec9a109f6f3875540a013c01afc9e7fa`; no workflow existed on that exact SHA.
- Spec/Core: `63457beb6e96fb4dc48b3b1b217bcefab90c4a22`; Core Focused `34867476719 = SUCCESS`; canonical `34867476727 = SUCCESS`.
- Backend: `379b968f63e42e293ded342fa65bac557f1ef993`; Backend Focused `34875026423 = SUCCESS`; canonical `34875026503 = SUCCESS`.
- UI: `a6298adb68af02537b87b26433003d830adb569d`; Core Focused `34864146634 = SUCCESS`; UI Focused `34864146677 = FAILURE`; canonical `34864146660 = FAILURE`.
- Exact UI canonical diagnostics now expose all failing assertions directly: typography `(15, 11, 30)` versus `(15, 12, 42)`; offline placeholder `Ask anything…` versus `pATHENA reconnecting`; composer height `118` versus `94`. Full pytest result: `3 failed, 5089 passed, 17 skipped`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Develop — IN_PROGRESS

Exact canonical Quality `34876523610` is active on current Develop. Do not supersede or classify from historical signatures before terminal evidence.

## Spec/Core — held closed

Current Spec/Core exact Core Focused and canonical are both green. Prior Core error clusters remain closed.

## Backend — held closed

Current Backend successor `379b968f...` is exact focused and canonical green. No current Storage/Recovery/backup root cause is reproduced; keep Backend closed.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS remain held.

## Current UI exact regressions — OPEN / UI-owned

The previously unqualified historical candidates now have direct exact-SHA reproduction from the current canonical diagnostics artifact on `a6298adb...`:

- `ERR-0067 = OPEN`: `test_pathena_design_system.py::test_spacing_and_motion_are_small_bounded_scales` reproduces actual `(15, 11, 30)` versus required `(15, 12, 42)`.
- `ERR-0068 = OPEN`: `test_pathena_offline_comprehension.py::test_readiness_copy_tracks_real_local_state` reproduces actual `Ask anything…` versus required `pATHENA reconnecting`.
- `ERR-0069 = OPEN`: `test_pathena_shell_density.py::test_shell_density_converges_real_shell_to_reference_geometry` reproduces composer height `118` versus required `94`.

Canonical has exactly these three failures after storage, Windows release guards/pypdf, Local install/pypdf, validator, Ruff and mypy pass. Deduplicate the red UI-focused lineage under `ERR-0069` rather than opening another shell-density ID. Error worker must not parallel-patch UI-owned product code while UI owns these fixes.

## ERR-0054 — OPEN — UI/Visual Review

No trustworthy current exact 11/11 visual review closes this item. Error worker does not create or accept a baseline. UI must provide current exact native artifacts and truthful reference/render review before closure.

## Persistent guards

No current exact evidence reopens pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap clusters. Keep all guards unchanged.

## Next root cause

1. Consume terminal Develop canonical `34876523610` without superseding the candidate.
2. Consume the next UI successor and requalify `ERR-0067`, `ERR-0068`, `ERR-0069` independently from exact assertion evidence.
3. Keep Spec/Core and Backend closed while their current exact evidence remains green.
4. Keep ERR-0059 and prior closed harness/Core clusters closed absent exact regression.
5. ERR-0054 remains strictly UI/Visual-Review-owned until truthful current 11/11 review evidence exists.
