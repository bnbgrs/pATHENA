# pATHENA Error Handoff

## Baseline

- Develop: `305703362d539ed467dec27cbc7300a495b3ca03`; canonical Quality `34726544110 = SUCCESS`; exact PR-triggered canonical `34728645613 = SUCCESS`.
- Workers: Spec/Core `80e7c8f8bb3c15c41ec8483dd0a57687016ba99c`; Backend `185662aafe7ab539fafd698e021635debfcc2a60`; UI `722ca4fd3afa6af9b2eecc3c82700efe287e77ed`.
- Error worker entered at `f8333575c7d93938c03aec7e61039b6293112058`; no workflow runs existed before either mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0047`, `ERR-0048`.
- FIXED this run: `ERR-0046`.
- Prior closures remain closed unless a current exact-SHA reproducer proves the same root cause again.

## ITERATION-1 — ERR-0046 closed

`ERR-0046 = FIXED / P2`.

Develop `305703362d539ed467dec27cbc7300a495b3ca03` contains the bounded Core-Focused ownership selector fix and canonical `34726544110 = SUCCESS`. The required successor UI proof now exists too: `postmerge/ui@722ca4fd3afa6af9b2eecc3c82700efe287e77ed` synchronized this Develop lineage and Core Focused `34728654619 = SUCCESS`; UI Focused `34728654616 = SUCCESS`. The former PySide-only UI test contamination no longer reproduces, while the existing exact-SHA, deleted-file, tracked-worktree and final-outcome guards remain intact.

## ITERATION-2 — ERR-0048 owner fix verified

`ERR-0048 = FIXED_PENDING_VERIFY / P2`.

Spec/Core successor `80e7c8f8bb3c15c41ec8483dd0a57687016ba99c` (`fix(core): normalize revision history candidate`) replaces the prior exact reproducer `6cc6977b...`.

Exact evidence:

- Core Focused `34727449865 = SUCCESS`;
- canonical Quality `34727449740 = SUCCESS`.

The previous sole Ruff `I001` in `tests/unit/test_knowledge_history_api.py` is no longer current. Final closure requires bounded integration into Develop plus exact integrated canonical success.

## ITERATION-3 — ERR-0047 original root cause removed

`ERR-0047 = FIXED_PENDING_VERIFY / P2`.

Backend successor `185662aafe7ab539fafd698e021635debfcc2a60` (`fix(jobs): use stable schedule priority contract`) now uses `JobPriority.TIME_CRITICAL` both when materializing and when asserting the persisted priority. Backend Focused `34728206760 = SUCCESS`.

Canonical `34728206821` is still red, but downloaded exact diagnostics prove the schedule-startup failure is gone. Full pytest reports `1 failed, 5029 passed, 17 skipped`; its sole failure is the independent storage-startup race now tracked as `ERR-0049`. Therefore do not keep `ERR-0047` OPEN merely because the whole canonical run is red for another root cause.

## ITERATION-4 — new ERR-0049 concurrent writer startup race

`ERR-0049 = OPEN / P1`.

Exact reproducer:

- `postmerge/backend@185662aafe7ab539fafd698e021635debfcc2a60`;
- canonical `34728206821 = FAILURE`;
- Backend Focused `34728206760 = SUCCESS`;
- Linux Storage, Windows Path Safety/release guards, Local Install/pypdf, Ruff, mypy and Specification Validator all PASS.

Downloaded full-pytest diagnostics isolate one failure:

`tests/integration/test_deletion_process_reliability.py::test_process_separated_public_delete_offline_sync_purge_and_restore`

The second legitimate race process exits because storage bootstrap raises `DatabaseStartupIdentityChangedError: ATHENA SQLite database/WAL/SHM identity changed after startup preflight` from `SQLiteDatabase._revalidate_existing_identity()`.

Current code permits only: exact unchanged identity, complete absent→complete sidecar publication, or complete→absent sidecar withdrawal. If WAL+SHM remain complete but their object identities transition while another legitimate writer is active, the guard currently rejects the startup as a generic identity change.

Important deduplication: Backend differs from Develop `305703362...` only in `src/athena/jobs/schedule_startup.py` and `tests/unit/test_schedule_startup.py`; storage/recovery code is shared. Develop canonical on the same shared storage code is green, so this is a concurrency-sensitive current storage race, not evidence that the schedule-startup change caused it.

Safe repair requirements:

1. Reproduce the process-separated reliability test first.
2. Distinguish legitimate concurrent sidecar lifecycle from replacement/tamper using stable evidence; do not accept arbitrary complete→complete identity replacement.
3. Preserve fail-closed foreign sidecar replacement and partial publication/withdrawal behavior from `ERR-0043`/`ERR-0045`.
4. Re-run storage-startup identity tests plus the process-separated reliability reproducer before canonical.

Ownership: Backend/Storage should own this product repair. Error worker should verify, deduplicate and close; it should not parallel-modify the guard while Backend is active.

## ITERATION-5 — current cascade/release-guard classification

No persistent historical release-guard signature was reopened by the current canonical failure. On Backend `185662aa...`, Windows Path Safety including packaged-runtime, adaptive reserve and pypdf checks is green; Linux Storage and Local Install are green. `ERR-0049` is specifically the current process-separated storage-bootstrap race and must be repaired without loosening those existing guards.

## CI discipline

- No competing canonical run was started.
- `postmerge/errors` had zero workflow runs before the Ledger commit and again before this Handoff commit.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail or guard relaxation occurred.

## Integrator handoff

- `ERR-0046 = FIXED / P2`: Develop canonical `34726544110@305703362d539ed467dec27cbc7300a495b3ca03 = SUCCESS`; successor UI Core Focused `34728654619@722ca4fd3afa6af9b2eecc3c82700efe287e77ed = SUCCESS`.
- `ERR-0048 = FIXED_PENDING_VERIFY / P2`: Spec/Core `80e7c8f8bb3c15c41ec8483dd0a57687016ba99c`; Core Focused `34727449865 = SUCCESS`; canonical `34727449740 = SUCCESS`; integrate bounded revision-history fix before closure.
- `ERR-0047 = FIXED_PENDING_VERIFY / P2`: Backend `185662aafe7ab539fafd698e021635debfcc2a60`; Backend Focused `34728206760 = SUCCESS`; the previous `JobPriority.HIGH` failure is absent from exact canonical diagnostics.
- `ERR-0049 = OPEN / P1`: same Backend exact SHA; canonical `34728206821 = FAILURE` only at the process-separated concurrent startup identity race. Treat this as the highest current error cluster before selecting Backend for integration.

## NEXT_ROOT_CAUSE

1. Consume the next Backend successor for `ERR-0049`; focused process-separated reliability must pass without weakening foreign/partial-sidecar identity guards.
2. If `ERR-0049` is owner-green, re-run/consume exact Backend canonical; then `ERR-0047` can close after integration evidence.
3. Consume the next Develop integration of Spec/Core `80e7c8f8...`; close `ERR-0048` only on exact integrated canonical success.
4. Immediately inspect any remaining current exact worker/canonical failure for a new independent root cause rather than recycling historical IDs.
