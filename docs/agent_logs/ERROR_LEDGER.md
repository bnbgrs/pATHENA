# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@bfee081ff63e849b5d024299f0a7b9286dc737e7` (`feat(core): integrate contradiction resolution`).
- Error worker entered this run at `postmerge/errors@be3d01227f4d60678b4ab803fd515a2fddd26fec`.
- Current workers: Spec/Core `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`; Backend `7c1af4402aed6c86c41fcc5eddbaab6a845445a8`; UI `dce6d463b17474ec2da702a14b7a4365123df45d`.
- Exact-current Develop canonical Quality: `34671556177@bfee081ff63e849b5d024299f0a7b9286dc737e7 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running and no competing canonical run was started.
- Backend exact `7c1af4402aed6c86c41fcc5eddbaab6a845445a8`: Storage Focused Candidate `34670367115 = SUCCESS`; canonical Quality `34670367093 = FAILURE`. Canonical specification validator, Ruff, mypy, Linux storage regressions, Windows path safety and Local install are green; only full pytest is red with two storage-bootstrap startup failures.
- `postmerge/errors@be3d01227f4d60678b4ab803fd515a2fddd26fec` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-046.
- Backend exact candidate `b595c960a747d9805b0865ea9f7237094318b706` was canonical-green (`34662086156 = SUCCESS`) and was integrated into `develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49`.
- Integrated source keeps the POSIX reserve descriptor identity-bound through release, rejects alternate-link ownership, and does not claim unproven physical reclamation merely from logical file length.
- Closure evidence is complete: exact integrated Develop canonical Quality `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`. Reopen only with a new current exact-SHA reproduction.

## ERR-0035 — SQLite preflight identity is not carried safely across migration into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052.
- Current exact Backend candidate: `7c1af4402aed6c86c41fcc5eddbaab6a845445a8`.
- Focused Storage evidence is green: `34670367115 = SUCCESS`.
- Canonical Quality is red: `34670367093 = FAILURE`; the only canonical Python-quality failure is pytest, with exactly two failures: `tests/unit/test_archive_replication.py::test_v30_migration_backfills_existing_spool_blob` and `tests/unit/test_news_audit.py::test_v29_migration_backfills_legacy_event_assessment_without_model`. Both fail as `StartupError: Failed to start service 'storage-bootstrap'`, caused by `DatabaseStartupIdentityChangedError`.
- Root cause is now exact: `StorageBootstrapService.start()` captures the read-only preflight, may then execute a required controlled migration that legitimately replaces/changes the SQLite primary file, but afterwards binds the original pre-migration `preflight` into `SQLiteDatabase.start()`. The writer correctly rejects that stale identity at its first `assert_database_file_set_identity()`.
- This is not evidence that the identity guard should be weakened. The guard is detecting a real identity transition; the orchestration is wrong because the accepted identity token is stale after an authorized migration.
- Required minimal owner fix: after a successful controlled migration, acquire a fresh identity-bearing read-only preflight for the migrated DB/WAL/SHM file set and use that post-migration preflight for writer binding. Preserve all existing fail-closed checks before migration, migration-recovery checks, before-writer identity assertion, after-writer identity assertion, missing-primary exclusive creation, and sidecar race detection.
- Required focused regression: both failing legacy migration tests must pass while adversarial replacement/sidecar-creation tests remain red-before-fix/green-after-fix as appropriate; then run the smallest storage/bootstrap regression set followed by canonical Quality on one unchanged exact Backend SHA.
- No Error-worker product mutation was made because Backend owns BE-052 and is actively changing the same root-cause area.

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

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
