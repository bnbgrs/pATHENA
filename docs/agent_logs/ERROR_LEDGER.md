# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `b4cba3d5cba31213e789cb2cbbc91f651e465e71`; canonical Quality `34731514082 = IN_PROGRESS`.
- Error worker entered this run at `4d56cdbde52af238917568948daf86bd7c112930`; zero workflow runs existed before mutation.
- Workers: Spec/Core `78d51621cbdfa3282cd236b5d0c7f5984abedcae`; Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56`; UI `031f291bbbb215e6319bb30e7aed92768e6aac18`.
- Spec/Core exact: Core Focused `34730134596 = SUCCESS`; canonical `34730134589 = SUCCESS`.
- Backend exact: Backend Focused `34730587835 = SUCCESS`; Storage Focused `34730587918 = SUCCESS`; canonical `34730587873 = SUCCESS`.
- UI exact: UI Focused `34731122725 = SUCCESS`; Core Focused `34731122738 = SUCCESS`; canonical `34731122731 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0047`, `ERR-0048`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030` through `ERR-0037`, `ERR-0040` through `ERR-0046`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Previous exact reproducer: canonical `34728206821@postmerge/backend:185662aafe7ab539fafd698e021635debfcc2a60 = FAILURE`; sole Full-Pytest failure was `tests/integration/test_deletion_process_reliability.py::test_process_separated_public_delete_offline_sync_purge_and_restore`, where the second legitimate process failed storage bootstrap with `DatabaseStartupIdentityChangedError`.
- Current Backend successor: `a709c229d6994c159490c2c1eaf3f2549f12cf56` (`fix(storage): validate complete sidecar rotation`). Exact Backend Focused `34730587835 = SUCCESS`, Storage Focused `34730587918 = SUCCESS`, canonical `34730587873 = SUCCESS`.
- The current candidate removes the race by adding `complete_rotation` in `_revalidate_existing_identity()`. The predicate accepts any transition where primary DB identity is unchanged, WAL+SHM existed before and after, and both sidecar filesystem identities changed.
- This does not yet satisfy the binding fail-closed requirement. Current code does not establish that the pair rotation was produced by the legitimate SQLite lifecycle; it only proves both sidecars are complete and both inode/device identities differ, then performs a read-only refresh. A simultaneous foreign replacement of both sidecars reaches the same `complete_rotation` predicate. Existing focused tests cover single-member sidecar replacement, partial publication, complete publication and complete withdrawal, but do not cover simultaneous replacement of both previously present sidecars.
- Therefore canonical green is necessary but insufficient for closure: the repair broadens the accepted identity transition exactly where the Error handoff required that arbitrary complete→complete replacement must not be accepted.
- Required next evidence: first add a focused regression that replaces both WAL and SHM after accepted preflight and proves fail-closed rejection. Then distinguish legitimate concurrent SQLite rotation from foreign/tampered replacement using stable evidence rather than the fact that both members changed. Re-run the process-separated race plus foreign single-sidecar, foreign paired-sidecar, partial publication/withdrawal, complete publication/withdrawal and live-writer startup tests before canonical.
- Ownership remains Backend/Storage. Error worker must not parallel-edit this product guard while Backend owns the slice.

## ERR-0048 — Spec/Core knowledge-history Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner repair was previously exact-green at `80e7c8f8bb3c15c41ec8483dd0a57687016ba99c`; current descendant `78d51621cbdfa3282cd236b5d0c7f5984abedcae` is also exact-green: Core Focused `34730134596 = SUCCESS`, canonical `34730134589 = SUCCESS`.
- Develop `b4cba3d5cba31213e789cb2cbbc91f651e465e71` now contains the bounded Knowledge revision-history files and revision-change wording repair from this lineage. Integrated canonical `34731514082` is still `IN_PROGRESS`, so no `FIXED` claim yet.

## ERR-0047 — Backend schedule-startup test used nonexistent JobPriority.HIGH

- Severity: P2 test/integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner repair changed the test contract to the real `JobPriority.TIME_CRITICAL` value and the old schedule-startup failure disappeared on `185662aafe7ab539fafd698e021635debfcc2a60`.
- Stronger current successor evidence now exists: Backend `a709c229d6994c159490c2c1eaf3f2549f12cf56` has Backend Focused `34730587835 = SUCCESS`, Storage Focused `34730587918 = SUCCESS` and canonical `34730587873 = SUCCESS` with no recurrence of the old schedule-startup failure.
- Closure still requires bounded integration into Develop plus exact integrated canonical success. Do not integrate the Backend head wholesale while `ERR-0049` remains open on its storage portion; the schedule-startup fix can be treated as independently verified if the Integrator can import it without the unsafe storage acceptance change.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. `ERR-0049` remains current because its proposed owner fix has not yet proven foreign paired-sidecar replacement stays fail-closed.
