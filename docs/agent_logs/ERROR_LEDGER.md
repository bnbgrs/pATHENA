# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@85bd5f19c8aca56273ad43ac708fe13ac4798415`.
- Error worker entered this run at `postmerge/errors@d16707612361e46849b326e1a207612f9e3ba2ad`.
- Current workers: Spec/Core `0d7e6281a584a302350a6b3aea0ac63e6eac744a`; Backend `fa995bf462aa8135d24f4e9e7059bc24f6992622`; UI `4ea0004fded7a169f18abc6fecd59461f86ee9bd`.
- Exact-current Develop canonical Quality: `34591859521@85bd5f19c8aca56273ad43ac708fe13ac4798415 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous exact Develop canonical: `34586893958@ccfbeb620cf009b75c6c53e5821438bf869ab114 = SUCCESS`.
- The Develop delta from `ccfbeb620cf009b75c6c53e5821438bf869ab114` to `85bd5f19c8aca56273ad43ac708fe13ac4798415` is CI/test workflow work; EmergencyReserve product/tests are unchanged.
- `postmerge/errors@d16707612361e46849b326e1a207612f9e3ba2ad` had zero canonical Quality runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0033 — Emergency-reserve filesystem-object identity and capacity-attestation gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Exact-current source verification: `develop/pathena-next@85bd5f19c8aca56273ad43ac708fe13ac4798415`; EmergencyReserve product/tests are source-equivalent to the previous canonical-green `ccfbeb620cf009b75c6c53e5821438bf869ab114`.
- Existing focused coverage contains adversarial parent-directory replacement tests only for POSIX. Native-Windows parent-swap coverage is absent.
- POSIX creation/release binds `reserve_root` to a directory descriptor for relative create/unlink and directory fsync. Windows/non-POSIX creation instead opens `self.path` by pathname, compares opened-file `fstat` with pathname `stat`, then returns to pathname-based parent resolution for cleanup/durability; normal release is pathname-based.
- Parent-directory binding alone is insufficient. Non-POSIX failure cleanup validates `self.path.stat()` against `created_identity`, then separately calls `self.path.unlink()`, leaving a same-parent filename-substitution window. Normal non-POSIX release has the wider `exists/is_file/stat -> unlink` pathname window.
- POSIX release closes the opened reserve-file descriptor before `os.unlink(..., dir_fd=root_fd)`, so the directory identity is bound but the filename can be replaced inside that directory before unlink.
- POSIX failure cleanup has the same target-identity discontinuity: after creation, the descriptor is closed before unconditional `os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)` when `created` is true.
- Non-POSIX `inspect()` does not attest one stable file identity: it can obtain size and allocation metadata through separate pathname observations, and `_wait_for_concurrent_creation()` can transition from one pathname observation to later inspection of a replacement object. Acceptance therefore needs the same single-object identity continuity as destructive mutation.
- Admission and release do not reject a multiply-linked regular reserve file. The source contains no `st_nlink`/single-link invariant, so a hard-linked `emergency.reserve` can satisfy regular-file, exact-size and allocation checks; release can then unlink only one name and report logical bytes as released while another hardlink keeps the same allocation live.
- POSIX inspection/acceptance also loses target identity before the status escapes. `_inspect_posix_with_root_fd()` opens `emergency.reserve` relative to bound `root_fd`, derives status from `fstat(descriptor)`, closes that descriptor, then verifies only that `reserve_root` still names the same directory. A same-directory filename substitution can therefore make returned status describe object A while `status.path` resolves to object B; the `O_EXCL` loser path can directly accept that status.
- **New exact-current refinement this run — physical-capacity attestation can become unknown yet still be accepted.** `_allocated_bytes_from_stat()` returns `None` whenever the platform stat result does not provide a non-negative integer `st_blocks`. `EmergencyReserveStatus.__post_init__()` enforces `allocated_bytes >= required_bytes` only when `allocated_bytes is not None`. Non-POSIX `inspect()` passes `_allocated_bytes(self.path)` directly into that status, so an exact-size regular existing reserve is accepted when physical allocation metadata is unavailable; there is no alternate fail-closed allocation proof in that branch. This violates the reserve's recovery purpose because logical length alone does not prove that the promised disk capacity is actually committed/recoverable.
- Existing focused coverage codifies the gap rather than closing it: `test_store_creates_small_physically_allocated_test_reserve` checks `allocated_bytes >= required` only conditionally when allocation metadata is present, and `test_store_inspect_detects_underallocated_file_when_platform_reports_blocks` explicitly verifies rejection only when allocation is observable. There is no focused test requiring unknown allocation metadata to fail closed or proving an equivalent platform-native capacity attestation.
- This new capacity-attestation seam is deduplicated into BE-046/ERR-0033 because it concerns whether the filesystem object accepted as `emergency.reserve` is demonstrably the exact, physically recoverable object/capacity pATHENA claims to own. It does not justify a competing Errors product patch while Backend owns BE-046.
- Consequence for closure: the bounded Backend fix must bind one reserve-file identity across inspection/acceptance/destructive release, require exclusive/safe ownership (including hardlink semantics), and never accept a reserve as physically recoverable when allocation is unknown. Where `st_blocks` is unavailable, use an equivalently strong platform-native allocation/capacity proof or fail closed; do not treat logical size as proof of physical reservation.
- Backend handoff still marks BE-046 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED` and has no tested bounded product candidate. No competing Errors product mutation is justified.
- Preserve physical non-sparse allocation, exact release accounting and fail-closed Storage/Recovery semantics.
- Closure requires a bounded Backend candidate plus focused adversarial tests for: native-Windows parent substitution over create-success/failure-cleanup/release; same-parent reserve-name substitution between identity validation and unlink in non-POSIX cleanup/release; POSIX same-parent filename substitution on release and `_ensure_posix()` failure cleanup; non-POSIX inspection/concurrent-creation substitution proving accepted metadata comes from one stable object; POSIX inspection/acceptance substitution proving the returned status still refers to the object named by `emergency.reserve`; hardlink admission/release proving a multiply-linked reserve is never accepted as uniquely recoverable capacity or reported as released while blocks remain referenced; and **unknown-allocation admission proving an exact-size file cannot be accepted merely because the platform cannot report `st_blocks`**. Then obtain exact-SHA canonical evidence as appropriate.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Current source evidence remains applicable: `SQLiteDatabase.start()` performs read-only preflight against the configured path and later independently opens the writable SQLite connection by pathname, without carrying an identity token/handle/descriptor from preflight into writer establishment.
- Distinct from `ERR-0033`: ERR-0033 concerns EmergencyReserve filesystem-object identity/capacity across mutation and acceptance; ERR-0035 concerns the primary SQLite database object between startup preflight and live writer open.
- Backend marks the same root cause BE-052 `OPEN / P1 / CURRENT SOURCE TRACE CONFIRMED`; Errors makes no parallel product mutation.
- Preserve read-only preflight, application-id/schema/quick-check validation, locality, symlink/reparse rejection, WAL/SHM checks and fail-closed Recovery/Storage semantics. A second pathname-only preflight is insufficient.
- Closure requires a bounded Backend candidate plus focused cross-platform identity-swap regression evidence, followed by exact-SHA canonical evidence when integration/closure requires it.

## Closed/stale historical clusters

All previously recorded FIXED and STALE clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent Beta/release guards remain binding: Windows `pypdf` metadata/`PackageNotFoundError`; fail-closed frozen child argv and two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context Chat reserve including requested-vs-effective provenance and boundary cases; lane-lock `PermissionError [Errno 13]` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError [Errno 22]`; `duplicate column name: source_processing_job_id`; `ATHENA Core startup failed`; `Failed to start service 'storage-bootstrap'`.

Before Beta/release promotion, execute the known-crash regression matrix on the exact candidate SHA. No promotion-ready claim while a known crash signature is reproducible.
