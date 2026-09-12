# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@4dbefe2167b28bffab2c6b69b7a8df4b43770a6f` (`feat(ui): integrate deterministic Help focus targets`).
- Error worker entered this run at `postmerge/errors@a2ab7e0a59edf2ad45695effd23b1b47a428f6b1`.
- Current workers: Spec/Core `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`; Backend `a8b30e42a22225728c3b9f6efcb3fceba3ee2315`; UI `dce6d463b17474ec2da702a14b7a4365123df45d`.
- Exact-current Develop canonical Quality: `34674406807@4dbefe2167b28bffab2c6b69b7a8df4b43770a6f = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running and no competing canonical run was started.
- Spec/Core exact `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`: Core Focused `34672548118 = SUCCESS`; canonical Quality `34672548120 = SUCCESS`.
- UI exact `dce6d463b17474ec2da702a14b7a4365123df45d`: UI Focused `34671153433 = SUCCESS`; canonical Quality `34671153472 = SUCCESS`.
- Backend exact `a8b30e42a22225728c3b9f6efcb3fceba3ee2315`: Backend Focused `34673089208 = FAILURE`; canonical Quality `34673089183 = FAILURE`. Canonical full pytest, mypy, Windows path safety, Linux storage regressions and Local install are green; Ruff is red.
- `postmerge/errors@a2ab7e0a59edf2ad45695effd23b1b47a428f6b1` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity regressed on current Backend head

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052.
- Previous Backend exact `7c1af4402aed6c86c41fcc5eddbaab6a845445a8` carried an identity-bearing startup preflight into `SQLiteDatabase.start()`, asserted DB/WAL/SHM identity before writer open, created a missing primary exclusively, then asserted identity again after writer establishment.
- Current exact Backend head `a8b30e42a22225728c3b9f6efcb3fceba3ee2315` has regressed that protection: `src/athena/storage/database.py` no longer stores or binds `DatabasePreflightReport`, no longer imports/calls the file-set identity helpers, and `start()` now performs only an independent `inspect_database_read_only(self.path)` followed by `sqlite3.connect()`.
- Exact branch comparison from `7c1af440...` to `a8b30e42...` confirms 65 deletions in `src/athena/storage/database.py`, 133 deletions in `src/athena/storage/recovery.py`, and complete removal of `tests/unit/test_database_startup_identity.py` (127 lines), while `src/athena/storage/bootstrap.py` also changes in the same startup cluster.
- Therefore the earlier BE-052 failure mode is current again on an exact active worker SHA: the accepted read-only snapshot is not identity-bound across the preflight-to-writer transition. The current full pytest PASS cannot close this root cause because the dedicated adversarial startup-identity test file was removed in the same candidate.
- This is release-guard weakening and must not be integrated. The current Backend candidate is not integration-ready even aside from its separate Ruff failure.
- Required owner correction: restore identity-bearing DB/WAL/SHM preflight continuity, including fail-closed assertions before and after writer establishment and exclusive missing-primary creation; then fix the controlled-migration orchestration by reacquiring a fresh identity-bearing preflight after an authorized migration rather than deleting the guard. Restore the adversarial startup-identity regression coverage. No Skip/XFail or guard/test removal is acceptable.
- Required verification: focused startup-identity tests including primary replacement and WAL/SHM sidecar creation/replacement, the two controlled-migration regressions previously exposed by canonical Quality, smallest storage/bootstrap regression set, then canonical Quality on one unchanged exact Backend SHA.
- Error worker did not mutate Backend product code because Backend actively owns BE-052 and is changing the same Storage/Recovery files.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-046.
- Exact integrated Develop closure remains `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

## ERR-0039 — Historical Spec/Core exact-head Ruff import-format blocker

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Historical exact reproducer `58b8040f84d5cac2530aaaac349c695361a78996` is superseded. Reopen only with a current exact-SHA reproduction.

## ERR-0038 — Historical Spec/Core exact-head Ruff failure

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Historical exact reproducer `53c3824e214b66e989cba1f425bfe7881190e12f` is superseded. Reopen only with a current exact-SHA reproduction.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature or a removed release guard is current.
