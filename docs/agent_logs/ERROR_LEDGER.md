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
- Baseline SHA: `7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Error worker synchronized history-preservingly and NON-FORCE with current develop via merge commit `d452accc8dc5fa7facff9845f84aebd73ee4fbe1`, retaining the prior error-ledger history and the full current Develop product tree.
- Latest product/test-bearing SHA on the current Develop lineage is Backend merge `0ee051eac32cd6156d464475571ee1b0995999b0`; later Develop commits `7bd3a5dd670655f96bedaa6061e73c09a0bf5613` and `7c15b44818e9ac5c3484ee30d4a20d6f0d56087e` are integration tracker/handoff documentation.
- Canonical ATHENA Quality Gate run `33718973461` for exact product SHA `0ee051eac32cd6156d464475571ee1b0995999b0` completed `SUCCESS`.

## Current error state

- OPEN: none currently assigned to error-worker product mutation.
- IN_PROGRESS: none.
- BLOCKED: `ERR-0001` is a confirmed current-lineage persistence-boundary defect cluster already claimed by `postmerge/backend`; error worker must not patch the same root cause in parallel.

## Current scan

- Exact current Develop product code was re-read after synchronization.
- `ERR-0001` remains present on `develop/pathena-next@7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`: `record_deletion()` still strips `entity_type` before runtime type validation, its deletion timestamp/commit sequence checks are bool-permissive relational guards, and `read_deletion_records()` still applies only a relational guard to `after_seq`.
- Canonical Quality for the latest product-bearing Develop lineage (`0ee051eac32cd6156d464475571ee1b0995999b0`) is green via run `33718973461`; no new canonical CI regression is evidenced by this scan.
- Current exact Develop head has no separate workflow run because its commits after the verified product SHA are documentation-only.
- Historical failing recovery/platform-parity runs remain stale unless their signature recurs on current Develop evidence.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `7c15b44818e9ac5c3484ee30d4a20d6f0d56087e`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `BLOCKED`
- exact evidence:
  - `src/athena/lifecycle/deletion.py` on current Develop calls `entity_type.strip()` before validating that `entity_type` is text; malformed values such as `None` therefore fail outside the intended durable-boundary validation contract.
  - `deleted_at_us < 0` and `deletion_commit_seq <= 0` are used without exact-int validation. Python `bool` values therefore pass as integers and can cross the persistence boundary.
  - `read_deletion_records(after_seq=...)` checks only `after_seq < 0`, allowing bool-as-int cursors and uncontrolled comparison failures for unrelated malformed runtime values.
  - `postmerge/backend` independently owns the same repair as tasks 290-293.
- reproducible path:
  1. Call `record_deletion(..., entity_type=None, ...)` -> `.strip()` is invoked before type validation.
  2. Call `record_deletion(..., deleted_at_us=False, deletion_commit_seq=True, ...)` -> both relational checks permit bool-as-int values to proceed toward SQLite.
  3. Call `read_deletion_records(..., after_seq=False)` -> cursor is treated as numeric zero rather than rejected as a malformed runtime type.
- primary root cause: durable deletion-ledger APIs rely on annotations and relational comparisons instead of explicit runtime boundary validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; focused regression tests owned by Backend for this slice.
- fix_commit: none yet.
- verification executed: exact-current-SHA source inspection, Backend ownership cross-check, and canonical Quality confirmation for the latest product-bearing Develop SHA (`33718973461` => `SUCCESS`). No product fix or focused runtime regression test has yet been executed by the error worker because Backend owns the root cause.
- remaining risks: malformed type failures vary by input shape; bool-as-int values may silently persist as integer values and weaken deletion/recovery API boundary guarantees.
- integrator handoff: accept the Backend fix only with focused proof that malformed values fail before SQL/query side effects, bool is rejected for integer fields/cursors, valid boundary values remain valid, idempotent replay remains unchanged, and ordered cursor behavior remains unchanged. After integration, the error worker must verify on the new exact Develop SHA before moving this entry to `FIXED`.
- blocked reason: active ownership collision avoidance — Backend has already claimed tasks 290-293 for this exact root cause.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
