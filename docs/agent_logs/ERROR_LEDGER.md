# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49` (`fix(storage): integrate fail-closed reserve release`).
- Error worker entered this run at `postmerge/errors@5464243058495896783116ccd3610311e4e823db`.
- Current workers: Spec/Core `52aaf68001bf141c779491ac005bb1d3e367700c`; Backend `b778b6af57f24f5edd19c699395c995818b959ed`; UI `0c1b746bf4e2060a9630258db49bca3a98b991cf`.
- Exact-current Develop canonical Quality: `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running and no competing canonical run was started.
- The current Spec/Core, Backend and UI worker HEADs have no workflow runs attached to those exact SHAs; prior exact-green candidate evidence remains historical evidence only and is not promoted to these newer heads.
- `postmerge/errors@5464243058495896783116ccd3610311e4e823db` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0033`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0033 — Emergency-reserve filesystem-object identity and physical-reclamation gap

- Severity: P1.
- Status: `FIXED_PENDING_VERIFY`.
- Specialist owner: Backend / BE-046.
- Backend exact candidate `b595c960a747d9805b0865ea9f7237094318b706` is canonical-green (`34662086156 = SUCCESS`) and is now integrated into current Develop `ca87e42c8820c47db7d6626feb17698560cd3b49`.
- Current Develop source contains the fail-closed reserve-release implementation: the POSIX reserve descriptor remains identity-bound through release, alternate-link ownership is rejected, and release does not claim unproven physical reclamation merely from logical file length.
- Final status remains `FIXED_PENDING_VERIFY`, not `FIXED`, because the exact integrated Develop canonical `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49` is still `IN_PROGRESS`. Consume that run before closure; do not start a competing run.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052.
- Fresh exact reproduction: `develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49`.
- Current `src/athena/storage/recovery.py` blob `1bb6adaaccc3703b4334daa3ea753aae9d3cb3e7` performs the read-only preflight. It samples primary DB and WAL/SHM path state, opens SQLite with `mode=ro`, validates application/schema metadata plus `PRAGMA quick_check`, then unconditionally closes that preflight connection in `finally`. Only after close does it return `DatabasePreflightReport`, with `wal_present` / `shm_present` sampled from path existence.
- Current `src/athena/storage/database.py` blob `aa6f8a285e8c730302441979ca4b26bb1646a0f1` reproduces the continuity gap directly: `SQLiteDatabase.start()` calls `inspect_database_read_only(self.path)` and discards the returned report, then separately invokes writable `sqlite3.connect(self.path, ...)`. No DB/WAL/SHM identity token, descriptor, stat tuple or equivalent preflight attestation is carried into or revalidated immediately against the live writer establishment.
- Therefore the exact-current code has an observation gap after accepted preflight and before writer open in which the primary file set can change without being bound to the accepted preflight identity. This finding is limited to missing attestation continuity; it does not claim SQLite will accept arbitrary corrupted WAL/SHM contents.
- Closure requires a bounded Backend candidate that binds or fail-closed revalidates the primary DB plus WAL/SHM identity across preflight-to-writer establishment, plus adversarial post-inspection/pre-writer mutation coverage. The focused regression must mutate the file set in that interval and prove startup rejects the changed identity while retaining all locality, schema, quick-check, Storage and Recovery guards.
- Backend continues to own BE-052, so `postmerge/errors` did not make a competing product-code mutation.

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
