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
- Baseline SHA: `edae673243cfea9114302bd0b52655a7034b106e`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Error worker synchronized history-preservingly and NON-FORCE with current Develop via merge commit `26096356bcd00614e65f01c7f326f404d46862c8`, retaining the prior Error Ledger/Handoff plus the complete current Develop product tree.
- Latest newly integrated product/test slice is UI-GAP-0001; its bounded product/test lineage had already passed canonical Quality before integration. Current exact Develop head is an integration-handoff commit.

## Current error state

- OPEN: none currently assigned to error-worker product mutation.
- IN_PROGRESS: none.
- BLOCKED: `ERR-0001` is a confirmed current-lineage persistence-boundary defect cluster already claimed by `postmerge/backend`; error worker must not patch the same root cause in parallel.

## Current scan

- Current Develop advanced to `edae673243cfea9114302bd0b52655a7034b106e` through the verified UI-GAP-0001 integration path; no deletion-ledger product fix was integrated.
- `postmerge/backend@ef88bbf9e649a6524f110d88b62e6126299d3a64` still contains only the documented ERR-0001 root-cause handoff for this slice, not a product fix.
- Therefore `ERR-0001` remains current and BLOCKED from error-worker mutation by ownership, not resolved.
- No fresh canonical CI failure tied to the current Develop SHA was found in this cycle. The latest UI exact-head Quality run observed remains pending, not failed; pending status is not opened as an error.
- Historical recovery/platform failures remain stale unless their signature recurs on current Develop evidence.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `edae673243cfea9114302bd0b52655a7034b106e`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `BLOCKED`
- exact evidence:
  - `record_deletion()` calls `entity_type.strip()` before validating that `entity_type` is text.
  - `deleted_at_us` and `deletion_commit_seq` rely on relational guards without exact-int/bool-safe validation.
  - `read_deletion_records(after_seq=...)` has the same exact-int/bool-safe cursor-boundary gap.
  - Backend independently owns the repair as tasks 290-293 and has not yet published a product fix commit.
- reproducible path:
  1. `record_deletion(..., entity_type=None, ...)` reaches `.strip()` before intended boundary validation.
  2. `record_deletion(..., deleted_at_us=False, deletion_commit_seq=True, ...)` permits bool-as-int values toward SQLite.
  3. `read_deletion_records(..., after_seq=False)` treats bool as numeric zero.
- primary root cause: durable deletion-ledger APIs rely on annotations/relational comparisons instead of explicit exact runtime validation before SQL access.
- affected files: `src/athena/lifecycle/deletion.py`; focused deletion-ledger/lifecycle regression tests.
- fix_commit: none yet.
- verification executed: exact branch/head and Backend ownership review in this cycle; no focused runtime regression executed by Error worker because Backend owns the root cause.
- remaining risks: malformed types can fail inconsistently; bool-as-int values may silently cross persistence/query boundaries and weaken recovery guarantees.
- integrator handoff: accept a Backend fix only with focused proof that malformed values fail before SQL/query side effects, bool is rejected for integer fields/cursors, valid boundary values remain valid, idempotent replay remains unchanged, and ordered cursor behavior remains unchanged. After integration, Error worker must verify on the exact new Develop SHA before moving to `FIXED`.
- blocked reason: active ownership collision avoidance with `postmerge/backend`.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
