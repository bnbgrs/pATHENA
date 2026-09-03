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
- Baseline SHA: `280066cc5450f172693e2ee913bd269b6755f7bb`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Error worker synchronized history-preservingly and NON-FORCE with current Develop via merge commit `253df53a23d7e5b9ccfbed4e29fa568fe8efa675`, retaining the prior Error Ledger/Handoff plus the complete current Develop product tree.

## Current error state

- OPEN: none currently assigned to error-worker product mutation.
- IN_PROGRESS: none.
- BLOCKED: `ERR-0001` is a confirmed current-lineage persistence-boundary defect cluster already claimed by `postmerge/backend`; error worker must not patch the same root cause in parallel.

## Current scan

- Exact current Develop `280066cc5450f172693e2ee913bd269b6755f7bb` was re-read directly.
- `src/athena/lifecycle/deletion.py` still has no exact runtime guards before the durable SQL boundary: `entity_type.strip()` occurs before type validation; integer fields/cursors rely on relational comparisons that accept bool as an int subtype.
- `postmerge/backend@a05c9b7da1dd865ece0f390074a7fb36928ed3fc` retains focused fail-before-SQL regression coverage but still has no product fix commit.
- Canonical Quality run `33728141579` for the focused-test lineage completed with conclusion `cancelled`; this is not a PASS and does not close the defect.
- Exact current Develop has no combined commit-status contexts attached; absence of status is not treated as green evidence.
- No unrelated current-Develop failure signature was established in this cycle; historical recovery/platform failures remain stale unless their signature recurs on current Develop evidence.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `280066cc5450f172693e2ee913bd269b6755f7bb`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `BLOCKED`
- exact evidence:
  - On exact current Develop, `record_deletion()` calls `entity_type.strip()` before validating that `entity_type` is text.
  - `deleted_at_us` and `deletion_commit_seq` rely on relational guards without exact-int/bool-safe validation.
  - `read_deletion_records(after_seq=...)` has the same exact-int/bool-safe cursor-boundary gap.
  - Backend owns the repair and has pinned malformed-input fail-before-SQL behavior in `tests/unit/test_deletion_ledger_boundaries.py`, but has not published the product guard fix.
  - Quality run `33728141579` on the focused-test lineage was cancelled, so verification is incomplete.
- reproducible path:
  1. `record_deletion(..., entity_type=None, ...)` reaches `.strip()` before intended boundary validation.
  2. `record_deletion(..., deleted_at_us=False, deletion_commit_seq=True, ...)` permits bool-as-int values toward SQLite.
  3. `read_deletion_records(..., after_seq=False)` treats bool as numeric zero.
- primary root cause: durable deletion-ledger APIs rely on annotations/relational comparisons instead of explicit exact runtime validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`; existing deletion-ledger/lifecycle recovery regressions.
- fix_commit: none yet.
- verification executed: exact current Develop source re-read; Backend head reviewed; canonical workflow evidence remains `completed/cancelled`. No product verification was claimed.
- remaining risks: malformed types can fail inconsistently; bool-as-int values may silently cross persistence/query boundaries and weaken recovery guarantees.
- integrator handoff: accept a Backend fix only with focused proof that malformed values fail before SQL/query side effects, bool is rejected for integer fields/cursors, valid boundary values remain valid, idempotent replay remains unchanged, ordered cursor behavior remains unchanged, and exact product-head Quality/regressions pass. After integration, Error worker must verify on the exact new Develop SHA before moving to `FIXED`.
- blocked reason: active ownership collision avoidance with `postmerge/backend`.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
