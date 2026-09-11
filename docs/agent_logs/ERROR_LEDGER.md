# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@69b16347bd4bab875c31b7a41830c6bab6a0bb7b`.
- Error worker entered this run at `postmerge/errors@cf438ffdf552cc3b0910bac2d2b3d5d030daa0b2`.
- Current workers: Spec/Core `4620299ffbdfd5a598f06c61e52750027f6c8d77`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `69773c189cabca3400f66101934b82b0d80bb38e`.
- Exact-current Develop canonical Quality: `34576900899@69b16347bd4bab875c31b7a41830c6bab6a0bb7b = IN_PROGRESS`. The previous exact Develop canonical `34572000094@b58964d577aba5d4fcb6c2969f48b445f3a1d4d7 = SUCCESS` is fully completed.
- The sole Develop delta from `b58964d577aba5d4fcb6c2969f48b445f3a1d4d7` to `69b16347bd4bab875c31b7a41830c6bab6a0bb7b` changes only `.github/workflows/quality.yml`: Windows release guards now remain independently observable and are aggregated by a final fail-closed enforcement step. EmergencyReserve product/tests are unchanged.
- `postmerge/errors@cf438ffdf552cc3b0910bac2d2b3d5d030daa0b2` had zero canonical Quality runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0033 — Emergency-reserve mutation identity binding gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current source verification: `develop/pathena-next@69b16347bd4bab875c31b7a41830c6bab6a0bb7b`; its only delta from the previous canonical-green Develop is the Quality workflow observability change, so EmergencyReserve product/tests remain exact-source-equivalent.
- Existing focused coverage still contains adversarial parent-directory replacement tests only for POSIX. Native-Windows parent-swap coverage is absent.
- POSIX creation/release binds `reserve_root` to a directory descriptor for relative create/unlink and directory fsync. Windows/non-POSIX creation instead opens `self.path` by pathname, compares opened-file `fstat` with pathname `stat`, then returns to pathname-based parent resolution for cleanup/durability; normal release is pathname-based.
- Parent-directory binding alone is insufficient. Non-POSIX failure cleanup validates `self.path.stat()` against `created_identity`, then separately calls `self.path.unlink()`, leaving a same-parent filename-substitution window. Normal non-POSIX release has the wider `exists/is_file/stat -> unlink` pathname window.
- POSIX release closes the opened reserve-file descriptor before `os.unlink(..., dir_fd=root_fd)`, so the directory identity is bound but the filename can be replaced inside that directory before unlink.
- POSIX failure cleanup has the same target-identity discontinuity: after creation, the descriptor is closed before unconditional `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)` when `created` is true.
- New exact-current refinement this run: non-POSIX `inspect()` does not attest one stable file identity even though `ensure()` and concurrent-creation paths rely on it for acceptance. It first obtains `file_size` via `self.path.stat(follow_symlinks=False)`, then calls `_allocated_bytes(self.path)`, which performs a second independent pathname `stat`. A same-name replacement between those calls can therefore synthesize one `EmergencyReserveStatus` from metadata belonging to two different filesystem objects. `_wait_for_concurrent_creation()` can also transition from one pathname `stat` to a later `inspect()` of a replacement object without identity continuity. This is read/acceptance-side evidence of the same root cause, not a separate error ID.
- Consequence for closure: the bounded fix must make the reserve-file identity stable not only across destructive unlink boundaries but also across acceptance/inspection boundaries used to decide that an existing or concurrently created reserve is valid. A single opened file handle/descriptor (or equivalent platform identity token) should supply size/allocation metadata for one object; repeated pathname-only checks are insufficient.
- Backend handoff still marks BE-046 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED` and has no tested bounded product candidate. No competing Errors product mutation is justified.
- Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics.
- Closure requires a bounded Backend candidate plus focused adversarial tests for: native-Windows parent substitution over create-success/failure-cleanup/release; same-parent reserve-name substitution between identity validation and unlink in non-POSIX cleanup/release; POSIX same-parent filename substitution on release and `_ensure_posix()` failure cleanup; and non-POSIX inspection/concurrent-creation substitution proving accepted metadata comes from one stable object. Then obtain exact-SHA canonical evidence as appropriate.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Current source evidence remains applicable: `SQLiteDatabase.start()` performs read-only preflight against the configured path and later independently opens the writable SQLite connection by pathname, without carrying an identity token/handle/descriptor from preflight into writer establishment.
- Distinct from `ERR-0033`: ERR-0033 concerns EmergencyReserve filesystem-object identity across mutation/acceptance; ERR-0035 concerns the primary SQLite database object between startup preflight and live writer open.
- Backend marks the same root cause BE-052 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED`; Errors makes no parallel product mutation.
- Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, WAL/SHM checks and fail-closed Recovery/Storage semantics. A second pathname-only preflight is insufficient.
- Closure requires a bounded Backend candidate plus focused cross-platform identity-swap regression evidence, followed by exact-SHA canonical evidence when integration/closure requires it.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
