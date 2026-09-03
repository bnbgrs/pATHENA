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
- Baseline SHA: `7e23616b79b65f759980ad98a27640b6c29bcea0`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Latest product/test-bearing SHA on the develop lineage: `ececd7741ca17a8c5c75af161359a5284fe88695`.
- `develop/pathena-next` is three documentation-only commits ahead of that product/test SHA; compare evidence shows no additional product/test file changes.
- Canonical Quality run `33703529634` for exact SHA `ececd7741ca17a8c5c75af161359a5284fe88695` completed `SUCCESS`.
- Exact `develop/pathena-next` branch Actions runs observed: none.

## Open errors

None confirmed on current `develop/pathena-next` SHA `7e23616b79b65f759980ad98a27640b6c29bcea0` as of 2026-09-03.

The absence of an exact develop-HEAD workflow run is an evidence gap, not a product defect. The current develop product/test tree is code-equivalent to the exact-SHA Quality-successful product/test commit above because only documentation changed afterward.

## Current scan

- Reviewed the newly integrated hybrid retrieval provenance diff (`8fb96f2333208e2f7f3c7048423dc6d2fd10e184`). It adds validated `retrieval_methods` provenance and preserves it through diversification; no current failure signature was identified.
- Exact product/test SHA `ececd7741ca17a8c5c75af161359a5284fe88695` has successful canonical Quality evidence.
- No historical pre-merge failure was reopened without current-lineage reproduction/evidence.
- Backend ResourceMode hardening remains an unverified backend candidate, not an error entry, because no failing current-lineage reproduction is recorded.

## Historical/stale evidence

Historical pre-consolidation failures remain stale unless their signature recurs on the current baseline. The previous post-merge baseline Quality success remains supporting historical evidence but has been superseded for the current product/test lineage by Quality run `33703529634`.

## Entries

_No `ERR-####` entries yet. The first newly evidenced current-baseline defect will receive `ERR-0001`._
