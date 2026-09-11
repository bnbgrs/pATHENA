# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@2ac4a605853fdc82b320f97b96494f3e17eaffa7`.
- Error worker entered this run at `postmerge/errors@685db6e76d68b32c620192d123edcb902e9b267a`.
- Current workers: Spec/Core `5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4`; Backend `195814616f394e1794aa4f3b2a16a584c092ab31`; UI `7f33ae92ec84d6a82052e4196bdd74c829fdf079`.
- Exact-current Develop canonical Quality: `34607013250@2ac4a605853fdc82b320f97b96494f3e17eaffa7 = IN_PROGRESS`; no PASS/FAIL is inferred until completion.
- Previous completed Develop canonical: `34601243038@b26eea46c89a8b628c2006d24d1fdac7492baa91 = SUCCESS`.
- Current Spec/Core exact canonical: `34603615414@5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4 = FAILURE`.
- Current Spec/Core exact focused candidate: `34603615415@5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4 = FAILURE`; the exact-head Ruff job failed, so no exact-head focused-test closure exists.
- `postmerge/errors@685db6e76d68b32c620192d123edcb902e9b267a` had zero check runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0038`, `ERR-0033`, `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`.
- BLOCKED: none at top level.

## ERR-0038 — Spec/Core exact-head Ruff failure blocks integration

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Specialist owner: Spec/Core. Errors does not parallel-mutate Core product code while that worker owns the candidate.
- Prior exact reproduction: canonical Quality `34598764602@2a9b76dd3581cb13052741907d0fad8357553536 = FAILURE`, isolated to Ruff `I001` in `src/athena/knowledge/revision_diff.py` while specification validator, mypy, pytest and platform lanes were otherwise green.
- New completed evidence: Spec/Core advanced to `5cbd31a5cf46c7cfcb75411d8216b3890aa5dec4` with commit message `fix(core): close revision diff lint regression`, but exact canonical `34603615414` still failed and exact focused candidate `34603615415` also failed its Ruff job. Therefore the attempted repair is not closure evidence and `ERR-0038` remains current.
- Source inspection of exact head `5cbd31a5...` shows the same standard-library import shape at the top of `revision_diff.py`: `import uuid` followed by `from dataclasses import dataclass`, `from enum import Enum`, and `from typing import TypeAlias`. Because the exact focused Ruff job still rejects this candidate, the specialist must consume the exact Ruff diagnostic rather than treating the commit message as proof of a fix.
- The candidate is bounded to `src/athena/knowledge/revision_diff.py` plus `tests/unit/test_claim_revision_diff.py`; no broad cross-worker cascade is inferred.
- Integrator evidence explicitly holds this Spec/Core candidate until exact-head Ruff and focused pytest are both observable and green. The focused workflow was subsequently improved on Develop to make Ruff and focused pytest independently observable while preserving a fail-closed aggregate result, but that workflow change does not retroactively qualify `5cbd31a5...`.
- Errors intentionally made no Core product mutation and did not start canonical Quality while Develop already has `34607013250` in progress.
- Closure requirement: a newer exact Spec/Core SHA with Ruff green for the bounded diff, relevant revision-diff focused tests green, and canonical exact-SHA success before `ERR-0038 = FIXED`.

## ERR-0033 — Emergency-reserve filesystem-object identity and capacity-attestation gap

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-046. Errors does not parallel-mutate Backend product code while that worker owns the root cause.
- Current source remains materially unchanged by the latest Develop CI/Core-only work; no new exact-SHA closure evidence exists from Backend.
- Existing focused coverage contains adversarial parent-directory replacement tests only for POSIX. Native-Windows parent-swap coverage is absent.
- POSIX creation/release binds `reserve_root` to a directory descriptor for relative create/unlink and directory fsync. Windows/non-POSIX creation instead opens `self.path` by pathname, compares opened-file `fstat` with pathname `stat`, then returns to pathname-based parent resolution for cleanup/durability; normal release is pathname-based.
- Parent-directory binding alone is insufficient. Non-POSIX failure cleanup validates `self.path.stat()` against `created_identity`, then separately calls `self.path.unlink()`, leaving a same-parent filename-substitution window. Normal non-POSIX release has the wider `exists/is_file/stat -> unlink` pathname window.
- POSIX release closes the opened reserve-file descriptor before `os.unlink(..., dir_fd=root_fd)`, so the directory identity is bound but the filename can be replaced inside that directory before unlink. POSIX failure cleanup has the same target-identity discontinuity.
- Inspection/acceptance can also lose object identity on both POSIX and non-POSIX paths, including concurrent creation. Admission/release do not establish exclusive ownership against hardlinks.
- Physical-capacity attestation is incomplete where allocation metadata is unavailable: `_allocated_bytes_from_stat()` can return `None`, while `EmergencyReserveStatus` only enforces minimum allocation when allocation is known. Logical length alone must not be treated as proof of physically recoverable reserve capacity.
- Closure requires a bounded Backend candidate with focused adversarial tests covering parent substitution, same-parent target substitution across inspection/cleanup/release, hardlink ownership/release accounting, and unknown-allocation fail-closed behavior, while preserving non-sparse allocation and Storage/Recovery semantics.

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
