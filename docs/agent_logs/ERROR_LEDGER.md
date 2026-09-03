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
- Baseline SHA: `e76b4cb2cca1612fe68b1ddd66554213352d32a9`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Error worker synchronized NON-FORCE with current develop through PR #46 / merge commit `ed032b8cca14461de4d5e1087e12ab1428627ef1`.
- Latest product/test-bearing SHA on the develop lineage: `3a5dfffaea7b3a1bc3e0f376e2edac6cf1a8dc5c`.
- The two commits after that product/test SHA on develop are documentation-only tracker/handoff updates.
- Canonical Quality run `33710799386` for exact SHA `3a5dfffaea7b3a1bc3e0f376e2edac6cf1a8dc5c` completed `SUCCESS`.
- Verified jobs on that exact SHA include Python 3.12 Quality (Spec Validator, Ruff, mypy, full pytest), Linux storage regressions, local install/restart smoke, and Windows path safety.

## Current error state

- OPEN: none currently assigned to error-worker mutation.
- IN_PROGRESS: none.
- BLOCKED: `ERR-0001` is a confirmed current-lineage persistence-boundary defect cluster already claimed by `postmerge/backend`; error worker must not patch the same root cause in parallel.

## Current scan

- The newly integrated archive Search source-anchor product/test SHA `3a5dfffaea7b3a1bc3e0f376e2edac6cf1a8dc5c` retains successful canonical Quality evidence via run `33710799386`.
- No new canonical CI, Windows path, Linux storage, install/restart, Ruff, mypy or pytest regression was found on that exact product/test lineage.
- Recent repository-wide failing Actions are historical recovery/platform-parity runs from an older lineage; they are not reopened against current develop without recurrence.
- Static current-lineage persistence-boundary review confirmed `ERR-0001` below.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `e76b4cb2cca1612fe68b1ddd66554213352d32a9`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `BLOCKED`
- exact evidence:
  - `src/athena/lifecycle/deletion.py` on current develop calls `entity_type.strip()` before validating that `entity_type` is actually text; malformed values such as `None` therefore escape as an uncontrolled attribute/type failure instead of the durable-boundary validation contract.
  - The same function checks `deleted_at_us < 0` and `deletion_commit_seq <= 0` without exact-int validation. In Python, `bool` is a subclass of `int`, so `False`/`True` can pass numeric guards and reach persistence.
  - `read_deletion_records(after_seq=...)` likewise checks only `after_seq < 0`, allowing bool-as-int cursors and leaking uncontrolled comparison `TypeError` for unrelated malformed runtime values.
  - `postmerge/backend` independently records these exact residual findings as its next tasks 290-293 and owns the repair slice.
- reproducible path:
  1. Call `record_deletion(..., entity_type=None, ...)` -> `.strip()` is invoked before type validation.
  2. Call `record_deletion(..., deleted_at_us=False, deletion_commit_seq=True, ...)` -> both numeric comparisons evaluate without rejecting bool-as-int, so malformed values can proceed toward SQLite persistence.
  3. Call `read_deletion_records(..., after_seq=False)` -> cursor is accepted as numeric zero rather than rejected as a malformed runtime type.
- primary root cause: durable deletion-ledger API relies on annotations and relational comparisons instead of explicit runtime boundary validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; focused regression tests to be added by Backend owner.
- fix_commit: none yet.
- verification executed: source-level exact-SHA inspection plus current backend handoff cross-check; no product fix or focused runtime regression test has yet been executed by the error worker.
- remaining risks: malformed type failures can be nondeterministic by input shape; bool-as-int values may silently persist as integer values and weaken API boundary guarantees used by deletion/recovery flows.
- integrator handoff: do not ask `postmerge/errors` and `postmerge/backend` to patch this root cause concurrently. Backend should land one coherent fail-before-SQL validation slice with focused idempotency/cursor regressions; after integration, error worker must verify on the new exact develop SHA before moving this entry to `FIXED`.
- blocked reason: active ownership collision avoidance — Backend has already claimed tasks 290-293 for this exact root cause.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
