# Error worker handoff

## Exact source of truth

- Develop: `ba5e541f780c3b650060f8ac65085032873088a3`; canonical `34871137412 = IN_PROGRESS`.
- Error worker before this refresh: `f06a13c3538143a80c1a7d58396bc71f6289a34a`; no queued/in-progress workflow exists on that exact SHA.
- Spec/Core: `63457beb6e96fb4dc48b3b1b217bcefab90c4a22`; Core Focused `34867476719 = SUCCESS`; canonical `34867476727 = SUCCESS`.
- Backend: `b6cc4cf5a91816d946ca24f8f911a0470a13c280`; Backend Focused `34857759374 = SUCCESS`; canonical `34857759296 = SUCCESS`.
- UI: `a6298adb68af02537b87b26433003d830adb569d`; Core Focused `34864146634 = SUCCESS`; UI Focused `34864146677 = FAILURE`; canonical `34864146660 = FAILURE`.
- Current UI canonical has Linux storage, Windows release guards/pypdf, Local install/pypdf, validator, Ruff and mypy green; only pytest/enforcement is red.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Develop — IN_PROGRESS

Current Develop integrates the PALLAS/ComfyUI shell candidate. Exact canonical Quality `34871137412` is active, so no Develop mutation or competing canonical run is permitted. Consume terminal evidence before any classification.

## Spec/Core — held closed

Current Spec/Core exact Core Focused and canonical are both green on `63457beb...`. Prior Core error clusters remain closed.

## Backend — held closed

Current Backend exact focused and canonical remain green on `b6cc4cf5...`. No current Storage/Recovery/backup root cause is reproduced.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS remain held.

## Current UI successor — IN_PROGRESS / UI-owned

Current exact evidence on `a6298adb...` is now terminal:

- Core Focused `34864146634 = SUCCESS`.
- UI Focused `34864146677 = FAILURE`; job-level evidence identifies `Run exact changed UI tests plus navigation invariant` as the failing step but does not expose the concrete assertion.
- canonical `34864146660 = FAILURE`; storage, Windows release guards, Local install/pypdf, validator, Ruff and mypy all pass; pytest/enforcement is the only red canonical lane.
- current tip commit only adds `test_ground_action_label_remains_semantically_stable_across_layout_densities`; the exact product refinement already sets `groundButton` text to `Ground`, so that source inspection alone is not sufficient to assign the aggregate focused failure to a historical ERR ID.

Therefore prior `ERR-0067`, `ERR-0068`, `ERR-0069` remain `IN_PROGRESS`, not `OPEN`, until direct current-SHA assertion evidence reproduces them. Do not patch UI product code in parallel.

## ERR-0054 — OPEN — UI/Visual Review

No trustworthy current exact 11/11 visual review closes this item. Error worker does not create or accept a baseline. UI must provide current exact native artifacts and truthful reference/render review before closure.

## Persistent guards

No current exact evidence reopens pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap clusters. Keep all guards unchanged.

## Next root cause

1. Consume terminal Develop canonical `34871137412` without superseding the candidate.
2. Obtain direct exact UI pytest assertion evidence before re-opening `ERR-0067`, `ERR-0068`, `ERR-0069` or creating a new UI error ID.
3. Keep Spec/Core and Backend closed while their current exact evidence remains green.
4. Keep ERR-0059 and prior closed harness/Core clusters closed absent exact regression.
5. ERR-0054 remains strictly UI/Visual-Review-owned until truthful current 11/11 review evidence exists.
