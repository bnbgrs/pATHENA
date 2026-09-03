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
- Baseline SHA: `5eb99f4cc3baed1f4eef23a54d686d109a7da21c`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Error worker synchronized history-preservingly and NON-FORCE with current Develop via merge commit `a174c515c613c00332f1a69bcaa2befbf3c3e604`, retaining the prior Error Ledger/Handoff plus the complete current Develop product tree.
- Latest newly integrated product slice is the canonical Search API DTO + normal-Hybrid adapter; it does not touch the deletion-ledger root cause.

## Current error state

- OPEN: none currently assigned to error-worker product mutation.
- IN_PROGRESS: none.
- BLOCKED: `ERR-0001` is a confirmed current-lineage persistence-boundary defect cluster already claimed by `postmerge/backend`; error worker must not patch the same root cause in parallel.

## Current scan

- Current Develop is `5eb99f4cc3baed1f4eef23a54d686d109a7da21c`; no deletion-ledger product fix is present on that lineage.
- `postmerge/backend@b533c99e0b56c022f5ab22ec3413675d00f6ff86` added focused fail-before-SQL regression coverage for `ERR-0001` at test-bearing commit `de7da517f0cc0cd056de3cbe8aed19db44915884`, but still has no product fix commit.
- Canonical ATHENA Quality Gate run `33728141579` for that focused-test commit completed with conclusion `cancelled`; this is not a PASS and does not close the defect.
- Therefore `ERR-0001` remains current and BLOCKED from error-worker mutation by ownership, not resolved.
- No unrelated current-Develop failure signature was established in this cycle; historical recovery/platform failures remain stale unless their signature recurs on current Develop evidence.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `5eb99f4cc3baed1f4eef23a54d686d109a7da21c`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `BLOCKED`
- exact evidence:
  - `record_deletion()` calls `entity_type.strip()` before validating that `entity_type` is text.
  - `deleted_at_us` and `deletion_commit_seq` rely on relational guards without exact-int/bool-safe validation.
  - `read_deletion_records(after_seq=...)` has the same exact-int/bool-safe cursor-boundary gap.
  - Backend owns the repair and has now pinned malformed-input fail-before-SQL behavior in `tests/unit/test_deletion_ledger_boundaries.py`, but has not yet published the product guard fix.
  - Quality run `33728141579` on the focused-test commit was cancelled, so verification is incomplete.
- reproducible path:
  1. `record_deletion(..., entity_type=None, ...)` reaches `.strip()` before intended boundary validation.
  2. `record_deletion(..., deleted_at_us=False, deletion_commit_seq=True, ...)` permits bool-as-int values toward SQLite.
  3. `read_deletion_records(..., after_seq=False)` treats bool as numeric zero.
- primary root cause: durable deletion-ledger APIs rely on annotations/relational comparisons instead of explicit exact runtime validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`; existing deletion-ledger/lifecycle recovery regressions.
- fix_commit: none yet.
- verification executed: exact current Develop lineage rechecked; Backend handoff/test commit reviewed; canonical workflow run `33728141579` independently checked and observed `completed/cancelled`. No product verification was claimed.
- remaining risks: malformed types can fail inconsistently; bool-as-int values may silently cross persistence/query boundaries and weaken recovery guarantees.
- integrator handoff: accept a Backend fix only with focused proof that malformed values fail before SQL/query side effects, bool is rejected for integer fields/cursors, valid boundary values remain valid, idempotent replay remains unchanged, ordered cursor behavior remains unchanged, and exact product-head Quality/regressions pass. After integration, Error worker must verify on the exact new Develop SHA before moving to `FIXED`.
- blocked reason: active ownership collision avoidance with `postmerge/backend`.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
