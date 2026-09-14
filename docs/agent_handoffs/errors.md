# Error worker handoff

## Exact source of truth

- Develop: `b2063a274984448d5f0db5d1c917c7ee93ae80be`; canonical `34862330981 = SUCCESS`.
- Error worker before this refresh: `9511f2eea99264c6bca84fa1fd46558c7da041c8`; no workflow run exists on that exact SHA.
- Spec/Core: `1d1334d82af52f8055d7da06b2afa3db575eac4b`; Core Focused `34861762468 = SUCCESS`; canonical `34861762425 = SUCCESS`.
- Backend: `b6cc4cf5a91816d946ca24f8f911a0470a13c280`; Backend Focused `34857759374 = SUCCESS`; canonical `34857759296 = SUCCESS`.
- UI: `a6298adb68af02537b87b26433003d830adb569d`; Core Focused `34864146634 = SUCCESS`; UI Focused `34864146677 = FAILURE`; canonical `34864146660 = IN_PROGRESS`.
- Current UI canonical already has Linux storage, Windows release guards/pypdf, Local install/pypdf, validator, Ruff and mypy green; full pytest is active.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Develop — held closed

Current Develop exact canonical is green. The PR-only concurrency change is integrated without a current Error-owned regression.

## Spec/Core — held closed

Current Spec/Core exact Core Focused and canonical are green. Prior Core error clusters remain closed.

## Backend — held closed

Backend canonical `34857759296` is now terminal `SUCCESS`, matching Backend Focused `34857759374 = SUCCESS`. No current Storage/Recovery/backup root cause is reproduced.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS remain held.

## Current UI successor — IN_PROGRESS / UI-owned

The previous UI line's three exact pytest signatures must not be copied forward automatically to current UI SHA `a6298adb...`.

Current exact evidence:

- Core Focused `34864146634 = SUCCESS`.
- UI Focused `34864146677 = FAILURE`; available job evidence shows failure in `Run exact changed UI tests plus navigation invariant`, but not the specific assertion.
- canonical `34864146660 = IN_PROGRESS`; release guards, storage, install/pypdf, validator, Ruff and mypy are green and full pytest is active.
- the current UI successor changes only `src/athena/desktop/pathena_layout_refinement_2200.py` and `tests/unit/test_pathena_layout_refinement_2200.py` relative to prior UI `575b8de0...`; current refinement explicitly stabilizes the Ground action label across responsive densities.

Therefore prior `ERR-0067`, `ERR-0068`, `ERR-0069` are `IN_PROGRESS` pending current exact-SHA reproduction, not asserted `OPEN` merely from historical evidence. Do not patch UI product code in parallel.

## ERR-0054 — OPEN — UI/Visual Review

No new Visual run exists yet on current UI SHA. The last trustworthy Visual lineage proved the technical eleven-surface capture/route path but did not complete 11/11 review. Error worker does not create or accept a baseline. UI must provide current exact native artifacts and truthful 11/11 review before closure.

## Persistent guards

No current exact evidence reopens pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap clusters. Keep all guards unchanged.

## Next root cause

1. Consume terminal UI canonical `34864146660`; classify only exact current-SHA failure signatures.
2. If current canonical reproduces typography, offline-readiness or shell-density assertions, re-open the corresponding deduplicated IDs individually; otherwise close/stale them from exact evidence.
3. Keep Develop, Spec/Core and Backend closed while current exact evidence remains green.
4. Keep ERR-0059 and prior closed harness/Core clusters closed absent exact regression.
5. ERR-0054 remains strictly UI/Visual-Review-owned until truthful current 11/11 review evidence exists.
