# Error worker handoff

## Exact source of truth

- Develop: `b0bb67755ccd1e0df04c9988fa0a9416b9abd7c8`; canonical `34854516653 = SUCCESS`.
- Error worker before this refresh: `a80e39b8b1669086d8db00deea10a7d37041507f`; no workflow run exists on that exact SHA.
- Spec/Core: `fb7e923763cd9d376953a977281c3e7377fdd3cc`; Core Focused `34856366095 = SUCCESS`; canonical `34856370276 = SUCCESS`.
- Backend: `b6cc4cf5a91816d946ca24f8f911a0470a13c280`; Backend Focused `34857759374 = SUCCESS`; canonical `34857759296 = IN_PROGRESS`, with Windows guards, Linux storage, Local install/pypdf, validator, Ruff and mypy green while full pytest runs.
- UI: `575b8de0a4f25f512e423c78623bfa5b398c379d`; Core Focused `34845670246 = SUCCESS`; UI Focused `34845670143 = FAILURE`; canonical `34845670362 = FAILURE`; Visual `34845664472 = FAILURE`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.

## Develop — held closed

Current Develop exact canonical is green. No current Error-owned regression is reproduced there.

## Spec/Core — held closed

Current Spec/Core exact Core Focused and canonical are green. `ERR-0066`, `ERR-0065` and prior Core clusters remain closed.

## Backend — IN_PROGRESS

Current Backend Focused is exact green. Canonical remains active with all completed guard/static/storage/install lanes green and only full pytest running. Do not start a competing run, supersede the candidate, or open a Backend error without terminal failure evidence.

## ERR-0059 — FIXED

No new exact manifest-truth regression. Current Visual captures exactly eleven surfaces and verifies route identity. Capture-derived manifest fields, `assigned_reference_count = 11`, and fail-closed exact-eleven PASS remain held.

## Current UI regressions — OPEN / UI-owned

The exact UI line is now split by real logs rather than retained as one opaque cluster:

- `ERR-0067`: typography tokens are `(15, 11, 30)` while the binding design-system contract expects `(15, 12, 42)`.
- `ERR-0068`: readiness state is `core-offline`, but placeholder remains `Ask anything…` instead of `pATHENA reconnecting`.
- `ERR-0069`: composer height is `118` while shell-density contract requires `94`; this is the sole UI Focused failure and also one canonical failure, so it is one deduplicated root cause.

Canonical result: `3 failed, 5088 passed, 17 skipped`; validator, Ruff, mypy, Local install/pypdf, Linux storage and Windows release guards are green. Error worker must not patch these UI-owned product slices in parallel.

## ERR-0054 — OPEN — UI/Visual Review

Exact Visual `34845664472` passes harness Ruff/mypy/contracts, hierarchy/accessibility, exactly eleven native captures, route identity, compare/proposal and artifact upload. Only final visual verdict is red. Current UI handoff remains `PAIRS_VERIFIED_0_OF_11` / `MATCH_0_OF_11`; Error worker does not create or accept a baseline.

## Persistent guards

No current exact evidence reopens pypdf/Frozen-argv/two-EXE/bounded-worker/adaptive-2048/lane-lock/duplicate-column/Core-startup/storage-bootstrap clusters. Keep all guards unchanged.

## Next root cause

1. Consume terminal Backend canonical `34857759296`; classify only terminal exact failure evidence.
2. Consume the next UI successor and verify `ERR-0067`, `ERR-0068`, `ERR-0069` independently while preserving all UI contracts.
3. Keep Develop and Spec/Core closed while their current exact evidence stays green.
4. Keep ERR-0059, ERR-0063, ERR-0064, ERR-0065 and ERR-0066 closed absent exact regression.
5. ERR-0054 remains strictly UI/Visual-Review-owned until truthful 11/11 review evidence exists.
