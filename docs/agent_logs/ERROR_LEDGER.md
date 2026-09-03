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

- Baseline branch: `main` (read-only)
- Baseline SHA: `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Baseline canonical Quality: GitHub Actions run `33694896994` — `SUCCESS`
- Verified jobs on baseline: Python 3.12 quality, Spec Validator, Ruff, mypy, full pytest, diagnostics enforcement, Windows path safety, Linux storage regressions, local install smoke — all `SUCCESS`.

## Open errors

None confirmed on baseline SHA `0d4d621f8a38ddf8eccfa09622bf193687619943` as of 2026-09-03.

## Historical/stale evidence

Historical pre-consolidation failures are not open entries unless their signature recurs on the current baseline. In particular, old bootstrap/recovery failures predating PR #26 are classified as stale evidence because the post-merge canonical Quality run on the exact current `main` SHA is fully green.

## Entries

_No `ERR-####` entries yet. The first newly evidenced current-baseline defect will receive `ERR-0001`._
