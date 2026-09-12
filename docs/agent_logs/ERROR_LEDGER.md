# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71` (`Integrator: combine all current Develop repair candidates`).
- Error worker entered this run at `postmerge/errors@df2e1a552e9151b46a7c54d86746c30fe22d45da`.
- Current workers: Spec/Core `1cef32d5f1479872d2f78cca29b2ed80fce05076`; Backend `2213d007266ac50c0500d61cb8d91fededbfda40`; UI `07721cfc86cb7e6c4137f7a5aa3396495a21cd8c`.
- Exact-current Develop canonical Quality: `34680853488@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`.
- Exact-current Develop Windows Runtime Boundary: `34680853496@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`.
- Backend exact `2213d007266ac50c0500d61cb8d91fededbfda40`: Backend Focused `34680797071 = SUCCESS`; canonical Quality `34680797081 = SUCCESS`.
- Spec/Core exact `1cef32d5f1479872d2f78cca29b2ed80fce05076`: Core Focused `34680250793 = FAILURE`; canonical Quality `34680250851 = FAILURE`.
- UI exact `07721cfc86cb7e6c4137f7a5aa3396495a21cd8c`: UI Focused `34681610012 = SUCCESS`; canonical Quality `34681610023 = IN_PROGRESS` at observation time.
- `postmerge/errors@df2e1a552e9151b46a7c54d86746c30fe22d45da` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-052; integrated repair by Integrator.
- Integrated closure SHA: `develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71`.
- The integrated `SQLiteDatabase.start()` now consumes an identity-bearing `DatabasePreflightReport`, validates primary DB/WAL/SHM identity before writer open, creates a missing primary exclusively, forces an initial SQLite read, and validates the same accepted identity again before schema initialization or connection-policy mutation.
- Controlled migration is not handled by weakening the guard. `StorageBootstrapService` reacquires a fresh read-only identity-bearing preflight after authorized migration activation and binds that fresh post-migration identity to the live writer transition.
- Exact integrated adversarial coverage exists in `tests/unit/test_storage_database_startup_identity.py` for primary replacement, file-set member replacement, missing-primary foreign creation, sidecar mutation, and replacement during writer establishment.
- Exact integrated controlled-migration coverage exists in `tests/unit/test_storage_bootstrap_identity.py`; it proves a migration receives a fresh activated-database identity and rejects another replacement after that refreshed preflight but before writer startup.
- Exact integrated canonical Quality `34680853488@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`. This satisfies the required post-integration exact-SHA verification. Reopen only with a new current exact-SHA reproduction.

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
