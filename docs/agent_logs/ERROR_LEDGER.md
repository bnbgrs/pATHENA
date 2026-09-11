# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@17d06d258ec2f5841049227504034ef601cdcdf8`.
- Error worker entered this run at `postmerge/errors@68fa85f7c6462b9454712b5d8dfb29fb9f49a2f7`.
- Current workers: Spec/Core `8019ff39c2352e40513532814760804eaa3c2df4`; Backend `4482958c3540b865ccc38a3ba5802366433c838b`; UI `ecb91b302c700b625af9ecb9d70452c974513c06`.
- Exact-current Develop canonical Quality: `34641291324@17d06d258ec2f5841049227504034ef601cdcdf8 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running.
- Current worker canonical evidence: Spec/Core `34636024267@8019ff39c2352e40513532814760804eaa3c2df4 = SUCCESS`; Backend `34638648498@4482958c3540b865ccc38a3ba5802366433c838b = SUCCESS`; UI `34638680643@ecb91b302c700b625af9ecb9d70452c974513c06 = SUCCESS`. Backend's green candidate is unrelated job-type registry work and does not close the open storage/recovery clusters.
- `postmerge/errors@68fa85f7c6462b9454712b5d8dfb29fb9f49a2f7` had zero workflow runs immediately before this mutation.
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
- Exact-current source trace remains applicable on `develop/pathena-next@17d06d258ec2f5841049227504034ef601cdcdf8`; the intervening job-type-registry change does not alter `src/athena/storage/emergency_reserve.py`.
- Existing focused coverage contains adversarial parent-directory replacement tests only for POSIX. Native-Windows parent-swap coverage is absent.
- POSIX creation/release binds `reserve_root` to a directory descriptor for relative create/unlink and directory fsync. Windows/non-POSIX creation instead opens `self.path` by pathname, compares opened-file `fstat` with pathname `stat`, then returns to pathname-based parent resolution for cleanup/durability; normal release is pathname-based.
- Parent-directory binding alone is insufficient. Non-POSIX failure cleanup validates `self.path.stat()` against `created_identity`, then separately calls `self.path.unlink()`, leaving a same-parent filename-substitution window. Normal non-POSIX release has the wider `exists/is_file/stat -> unlink` pathname window.
- POSIX release attests the opened reserve with `fstat`, captures its logical size, closes pATHENA's reserve descriptor, then re-validates only the parent-directory identity before `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)` and returns the previously captured size. The filename/object identity is not carried across the attestation-to-unlink boundary.
- Inspection/acceptance can also lose object identity on both POSIX and non-POSIX paths, including concurrent creation. Admission/release do not establish exclusive ownership against hardlinks.
- Physical-capacity attestation is incomplete where allocation metadata is unavailable: `_allocated_bytes_from_stat()` can return `None`, while `EmergencyReserveStatus` only enforces minimum allocation when allocation is known. Logical length alone must not be treated as proof of physically recoverable reserve capacity.
- Previously established open-handle evidence remains: an independently pre-opened descriptor can survive unlink and keep the inode/data blocks referenced, so successful pathname removal does not prove physical reclamation; a writable second descriptor can also mutate the same inode after attestation.
- A one-time `st_nlink == 1` or equivalent single-link check at attestation is insufficient. Because the validated file descriptor is closed before unlink and there is no object/namespace lock spanning that boundary, another actor can create a second hardlink to the already-attested inode after the check but before pATHENA unlinks the canonical name. The unlink can then succeed while the new hardlink retains the inode and blocks, yet `release()` would return the pre-race logical size as released bytes.
- Current `tests/unit/test_emergency_reserve.py` covers stable release, POSIX parent-directory replacement, allocation under-reporting and creation cleanup, but has no adversarial hardlink insertion between release attestation and unlink. Therefore a static single-link admission assertion would not constitute closure evidence.
- Closure requires a bounded Backend candidate with focused adversarial tests covering parent substitution, same-parent target substitution across inspection/cleanup/release, hardlink ownership/release accounting including the attestation-to-unlink hardlink-insertion race, unknown-allocation fail-closed behavior, and the pre-opened second-descriptor case. The release contract must maintain a bounded physical-reclamation guarantee across the entire attestation-to-accounting interval rather than sampling link count once. Preserve non-sparse allocation and all Storage/Recovery semantics.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current source evidence: `develop/pathena-next@17d06d258ec2f5841049227504034ef601cdcdf8`. `SQLiteDatabase.start()` calls `inspect_database_read_only(self.path, ...)`, consumes the returned preflight result, and only later establishes a separate writable connection with `sqlite3.connect(self.path, check_same_thread=False)`.
- The continuity gap is broader than primary-database pathname identity. `inspect_database_read_only()` also inspects the current `-wal` and `-shm` sidecar state and performs its read-only quick-check through a connection that is closed before the later writer connection is opened. No file-set identity token or equivalent binding carries the attested primary database plus WAL/SHM snapshot across that transition.
- Therefore WAL/SHM presence or filesystem-object identity can change after read-only inspection returns but before the writer connection is established, even if the primary database object itself remains unchanged. The live writer can consequently observe a different SQLite file set from the one whose sidecar state the preflight accepted.
- This evidence does **not** assert that SQLite will accept an arbitrary malformed or forged WAL/SHM file; SQLite's own format/checksum validation remains independent. The defect is the absence of fail-closed attestation continuity between the preflight file set and the writer-open file set.
- Distinct from `ERR-0033`: ERR-0033 concerns EmergencyReserve filesystem-object identity/capacity across mutation and acceptance; ERR-0035 concerns SQLite startup continuity between a validated read-only file-set snapshot and the live writable SQLite snapshot.
- Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, WAL/SHM checks and fail-closed Recovery/Storage semantics. Merely repeating another pathname-only preflight is insufficient unless it is made atomic/equivalent with writer establishment.
- Closure requires a bounded Backend candidate that binds or fail-closed revalidates the **whole SQLite file set** — primary DB, WAL and SHM — across preflight-to-writer establishment. Focused adversarial evidence must gate startup after `inspect_database_read_only()` returns and before writer `sqlite3.connect()`, then create/remove/replace a sidecar and prove startup detects the snapshot/identity mismatch rather than relying on stale sidecar preflight state. Exact-SHA canonical evidence follows when integration/closure requires it.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.