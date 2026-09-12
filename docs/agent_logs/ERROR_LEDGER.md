# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@712376f561e10ea8d579fa316e8deca19ce3a7a1` (`ci(core): scope focused candidate triggers`).
- Error worker entered this run at `postmerge/errors@9b51bc0cea8f3d32eb9fd232a1711a848d74af39`.
- Current workers: Spec/Core `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`; Backend `736fb66085084f3d0080c0918cdfba00d63558fc`; UI `626c7e0dead504b57f331c9b011d99c96cee6c4d`.
- Exact-current Develop canonical Quality: `34668822579@712376f561e10ea8d579fa316e8deca19ce3a7a1 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running and no competing canonical run was started.
- Spec/Core exact `ea4211fe5a375698c72dbfdd1d2a5778ea2df0dd`: canonical `34667286138 = SUCCESS`; Core Focused Candidate `34667286211 = SUCCESS`.
- Backend exact `736fb66085084f3d0080c0918cdfba00d63558fc`: Storage Focused Candidate `34668097963 = SUCCESS`; canonical `34668098022 = IN_PROGRESS`. A parallel Core Focused Candidate failure on this Backend SHA is not used as Storage evidence.
- UI exact `626c7e0dead504b57f331c9b011d99c96cee6c4d`: canonical `34668610457 = IN_PROGRESS`.
- `postmerge/errors@9b51bc0cea8f3d32eb9fd232a1711a848d74af39` had zero workflow runs immediately before this mutation.
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
- Closure evidence is now complete: exact integrated Develop canonical Quality `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = SUCCESS`. This satisfies the required integrated exact-SHA verification; `ERR-0033` is closed and must not be reopened without a new current exact-SHA reproduction.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052.
- Fresh exact reproduction remains `develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49` until the Backend fix is integrated and independently verified.
- Backend now has a bounded candidate at `736fb66085084f3d0080c0918cdfba00d63558fc` (`fix(storage): bind SQLite preflight identity to live writer`). The candidate carries a DB/WAL/SHM identity token from accepted preflight into writer startup, checks it before and after writer establishment, binds the preflight through `StorageBootstrapService`, and adds adversarial replacement/creation coverage.
- Relevant exact focused evidence is green: Storage Focused Candidate `34668097963 = SUCCESS` on `736fb66085084f3d0080c0918cdfba00d63558fc`.
- Status remains `OPEN`, not `FIXED_PENDING_VERIFY`, in this run because Backend canonical Quality `34668098022` is still `IN_PROGRESS`; do not start a competing run or promote the candidate before that exact canonical result is consumed.

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
