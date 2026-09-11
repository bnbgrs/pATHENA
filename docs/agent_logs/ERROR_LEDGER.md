# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@deafa0531504a9cb34bff5cb29be7247c084cd16`.
- Error worker entered this run at `postmerge/errors@604e25bb1837065133eb6ecad8367bc8100e7e75`.
- Current workers: Spec/Core `4620299ffbdfd5a598f06c61e52750027f6c8d77`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `69773c189cabca3400f66101934b82b0d80bb38e`.
- Exact-current Develop canonical Quality: `34581635106@deafa0531504a9cb34bff5cb29be7247c084cd16 = IN_PROGRESS`. The previous exact Develop canonical `34576900899@69b16347bd4bab875c31b7a41830c6bab6a0bb7b = SUCCESS` is fully completed.
- The Develop delta from `69b16347bd4bab875c31b7a41830c6bab6a0bb7b` to `deafa0531504a9cb34bff5cb29be7247c084cd16` integrates only the bounded Core interpretation-provenance contract plus its focused tests and updates `integrator.md`; EmergencyReserve product/tests are unchanged.
- `postmerge/errors@604e25bb1837065133eb6ecad8367bc8100e7e75` had zero canonical Quality runs immediately before this mutation.
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
- Exact-current source verification: `develop/pathena-next@deafa0531504a9cb34bff5cb29be7247c084cd16`; its delta from the previous canonical-green Develop is disjoint Core interpretation-provenance code/tests plus integrator documentation, so EmergencyReserve product/tests remain exact-source-equivalent.
- Existing focused coverage contains adversarial parent-directory replacement tests only for POSIX. Native-Windows parent-swap coverage is absent.
- POSIX creation/release binds `reserve_root` to a directory descriptor for relative create/unlink and directory fsync. Windows/non-POSIX creation instead opens `self.path` by pathname, compares opened-file `fstat` with pathname `stat`, then returns to pathname-based parent resolution for cleanup/durability; normal release is pathname-based.
- Parent-directory binding alone is insufficient. Non-POSIX failure cleanup validates `self.path.stat()` against `created_identity`, then separately calls `self.path.unlink()`, leaving a same-parent filename-substitution window. Normal non-POSIX release has the wider `exists/is_file/stat -> unlink` pathname window.
- POSIX release closes the opened reserve-file descriptor before `os.unlink(..., dir_fd=root_fd)`, so the directory identity is bound but the filename can be replaced inside that directory before unlink.
- POSIX failure cleanup has the same target-identity discontinuity: after creation, the descriptor is closed before unconditional `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)` when `created` is true.
- Non-POSIX `inspect()` does not attest one stable file identity: it can obtain size and allocation metadata through separate pathname observations, and `_wait_for_concurrent_creation()` can transition from one pathname observation to later inspection of a replacement object. Acceptance therefore needs the same single-object identity continuity as destructive mutation.
- New exact-current refinement this run: admission and release do not reject a multiply-linked regular reserve file. `_prepare_root()` rejects symlink/junction/reparse boundaries, and inspection rejects non-regular objects, but the exact-current source contains no `st_nlink`/single-link invariant. A hard-linked `emergency.reserve` can therefore satisfy regular-file, exact-size and allocation checks. `release()` then unlinks only the reserve pathname and returns its logical byte count, while another hardlink can keep the same inode and all reserved blocks allocated. The Recovery caller can thus be told that reserve bytes were released when emergency capacity was not actually recovered.
- This hardlink case is part of the same BE-046 object-ownership/identity cluster, not a new error ID: the reserve contract must establish exclusive ownership of the filesystem object whose blocks are counted and released. Existing `test_store_releases_only_reserve_file` checks pathname removal and returned logical size only; the current focused suite contains no hardlink admission/release regression.
- Consequence for closure: the bounded fix must bind one reserve-file identity across inspection/acceptance/destructive release and require an exclusive single-link object (or an equivalently strong platform ownership invariant) before treating its allocation as recoverable reserve capacity. Release must fail closed rather than report recovered bytes when object linkage means the blocks can remain allocated.
- Backend handoff still marks BE-046 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED` and has no tested bounded product candidate. No competing Errors product mutation is justified.
- Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics.
- Closure requires a bounded Backend candidate plus focused adversarial tests for: native-Windows parent substitution over create-success/failure-cleanup/release; same-parent reserve-name substitution between identity validation and unlink in non-POSIX cleanup/release; POSIX same-parent filename substitution on release and `_ensure_posix()` failure cleanup; non-POSIX inspection/concurrent-creation substitution proving accepted metadata comes from one stable object; and hardlink admission/release proving a multiply-linked reserve is never accepted as uniquely recoverable capacity or reported as released while blocks remain referenced. Then obtain exact-SHA canonical evidence as appropriate.

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
