# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@c670d7809c9f0aa5e6c31956b57e897091f1b9d6`.
- Error worker entered this run at `postmerge/errors@6ada3662333696a2373f0b6eb30eff9e5367e373`.
- Current workers: Spec/Core `8019ff39c2352e40513532814760804eaa3c2df4`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `4eeb75a6f5909fb1aa194c2c6df2d5ce1b431748`.
- Exact-current Develop canonical Quality: `34635967020@c670d7809c9f0aa5e6c31956b57e897091f1b9d6 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running.
- Latest Backend exact-head canonical Quality: `34604847434@195814616f394e1794aa4f3b2a16a584c092ab31 = SUCCESS`; this baseline-green run does not close BE-046 because no BE-046 product candidate exists on that SHA.
- Current Spec/Core `8019ff39c2352e40513532814760804eaa3c2df4` and UI `4eeb75a6f5909fb1aa194c2c6df2d5ce1b431748` have no exact-head workflow run yet; older exact-green or in-progress evidence is not promoted to those newer SHAs.
- `postmerge/errors@6ada3662333696a2373f0b6eb30eff9e5367e373` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`.
- BLOCKED: none at top level.

## ERR-0038 — Spec/Core exact-head Ruff failure

- Severity: P1 integration blocker when reproduced.
- Status: `STALE`.
- Previous reproducer: `53c3824e214b66e989cba1f425bfe7881190e12f`, canonical `34609297666 = FAILURE`, with Ruff `I001` at `src/athena/knowledge/revision_diff.py:3:1`.
- The superseding exact Spec/Core candidate `e9a6a1d28281e78c9b8ee0548582ed4a39d424b4` passed canonical Quality `34621318923` and focused candidate `34621318964`, and removed the file carrying the old reproducer. Current Spec/Core has advanced again to `8019ff39c2352e40513532814760804eaa3c2df4` without a new exact-head reproduction of the historical `I001` defect.
- This remains `STALE`, not `FIXED`: the old revision-diff candidate was abandoned/superseded rather than repaired in place.
- Reopen only if a current exact candidate reintroduces/reproduces the Ruff failure.

## ERR-0033 — Emergency-reserve filesystem-object identity and capacity-attestation gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current source trace: `develop/pathena-next@c670d7809c9f0aa5e6c31956b57e897091f1b9d6`. Changes since the last Develop storage trace are UI/Core/docs-only; `src/athena/storage/emergency_reserve.py` remains the same storage implementation. Develop canonical `34635967020` is still in progress and cannot close this semantic Recovery gap.
- Existing focused coverage contains adversarial parent-directory replacement tests only for POSIX. Native-Windows parent-swap coverage is absent.
- POSIX creation/release binds `reserve_root` to a directory descriptor for relative create/unlink and directory fsync. Windows/non-POSIX creation instead opens `self.path` by pathname, compares opened-file `fstat` with pathname `stat`, then returns to pathname-based parent resolution for cleanup/durability; normal release is pathname-based.
- Parent-directory binding alone is insufficient. Non-POSIX failure cleanup validates `self.path.stat()` against `created_identity`, then separately calls `self.path.unlink()`, leaving a same-parent filename-substitution window. Normal non-POSIX release has the wider `exists/is_file/stat -> unlink` pathname window.
- POSIX release attests the opened reserve with `fstat`, captures its logical size, closes pATHENA's reserve descriptor, then re-validates only the parent-directory identity before `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)` and returns the previously captured size. The filename/object identity is not carried across the attestation-to-unlink boundary.
- Inspection/acceptance can also lose object identity on both POSIX and non-POSIX paths, including concurrent creation. Admission/release do not establish exclusive ownership against hardlinks.
- Physical-capacity attestation is incomplete where allocation metadata is unavailable: `_allocated_bytes_from_stat()` can return `None`, while `EmergencyReserveStatus` only enforces minimum allocation when allocation is known. Logical length alone must not be treated as proof of physically recoverable reserve capacity.
- Previously established open-handle evidence remains: an independently pre-opened descriptor can survive unlink and keep the inode/data blocks referenced, so successful pathname removal does not prove physical reclamation; a writable second descriptor can also mutate the same inode after attestation.
- New exact-current closure evidence: a one-time `st_nlink == 1` or equivalent single-link check at attestation would still be insufficient. Because the validated file descriptor is closed before unlink and there is no object/namespace lock spanning that boundary, another actor can create a second hardlink to the already-attested inode after the check but before pATHENA unlinks the canonical name. The unlink can then succeed while the new hardlink retains the inode and blocks, yet `release()` would return the pre-race logical size as released bytes. This is the same BE-046 physical-reclamation root cause, not a new error ID.
- Current `tests/unit/test_emergency_reserve.py` covers stable release, POSIX parent-directory replacement, allocation under-reporting and creation cleanup, but has no adversarial hardlink insertion between release attestation and unlink. Therefore a static single-link admission assertion would not constitute closure evidence.
- Closure requires a bounded Backend candidate with focused adversarial tests covering parent substitution, same-parent target substitution across inspection/cleanup/release, hardlink ownership/release accounting including the attestation-to-unlink hardlink-insertion race, unknown-allocation fail-closed behavior, and the pre-opened second-descriptor case. The release contract must maintain a bounded physical-reclamation guarantee across the entire attestation-to-accounting interval rather than sampling link count once. Preserve non-sparse allocation and all Storage/Recovery semantics.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Current source evidence remains applicable: `SQLiteDatabase.start()` performs read-only preflight against the configured path and later independently opens the writable SQLite connection by pathname, without carrying an identity token/handle/descriptor from preflight into writer establishment.
- Distinct from `ERR-0033`: ERR-0033 concerns EmergencyReserve filesystem-object identity/capacity across mutation and acceptance; ERR-0035 concerns the primary SQLite database object between startup preflight and live writer open.
- Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, WAL/SHM checks and fail-closed Recovery/Storage semantics. A second pathname-only preflight is insufficient.
- Closure requires a bounded Backend candidate plus focused cross-platform identity-swap regression evidence, followed by exact-SHA canonical evidence when integration/closure requires it.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.