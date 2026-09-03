# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only failures reproduced or evidenced on the stated SHA are opened.
- Historical failures are not carried forward unless their signature recurs on the current baseline.
- Cascades are deduplicated under their primary root cause.
- `FIXED` requires observed verification; unverified fixes remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `fc3f6e44fcbeecdf1f4e817a4b9523a5ba2fbbaf`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Baseline delta versus `main`: documentation/coordination only; no production or test code changes observed in the compare.
- Exact `develop/pathena-next` Actions runs observed: none.
- Nearest exact production-code evidence: canonical post-merge Quality run `33694896994` on `main` SHA `0d4d621f8a38ddf8eccfa09622bf193687619943` — `SUCCESS`.
- Verified jobs on that code-equivalent production baseline: Python 3.12 quality, Spec Validator, Ruff, mypy, full pytest, diagnostics enforcement, Windows path safety, Linux storage regressions, local install smoke — all `SUCCESS`.

## Open errors

None confirmed on current `develop/pathena-next` SHA `fc3f6e44fcbeecdf1f4e817a4b9523a5ba2fbbaf` as of 2026-09-03.

The absence of an exact `develop/pathena-next` workflow run is not recorded as a product defect because the branch currently differs from the green post-merge code baseline only by documentation/coordination files. It remains an evidence gap to re-evaluate as soon as product/test code changes land.

## Current scan

- No `NotImplementedError` occurrences found by repository code search.
- No `TODO` occurrences found by repository code search.
- No current CI failure signature exists for `develop/pathena-next` because no Actions run is associated with the branch yet.
- No historical pre-merge failure was reopened without current-SHA reproduction/evidence.

## Historical/stale evidence

Historical pre-consolidation failures are not open entries unless their signature recurs on the current baseline. Old bootstrap/recovery failures predating PR #26 remain stale evidence because the merged production code received a fully green exact-SHA canonical Quality run and no production-code delta has yet landed on `develop/pathena-next`.

## Entries

_No `ERR-####` entries yet. The first newly evidenced current-baseline defect will receive `ERR-0001`._
