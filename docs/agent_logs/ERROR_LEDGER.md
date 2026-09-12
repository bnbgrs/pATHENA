# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@28b9585b49bf632401340735f05de20d95a70ead` (`feat(core): integrate stale claim revalidation planning`).
- Error worker entered this run at `postmerge/errors@2ca073c51acb726918cfe396ad4baa75a65ee80e`.
- Current workers: Spec/Core `8ee183e14ed2527d254def4946ce0b79104f1afa`; Backend `0ce1a70d421b41cd0ca4441399d97c82b9849285`; UI `f37b923b6f64f9c75d63febe64aef6c29147069f`.
- Exact-current Develop canonical Quality: `34679217397@28b9585b49bf632401340735f05de20d95a70ead = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running and no competing canonical run was started.
- Previous Develop exact `cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80`: canonical Quality `34676594675 = SUCCESS`.
- Backend exact `0ce1a70d421b41cd0ca4441399d97c82b9849285`: Backend Focused `34678280408 = SUCCESS`; canonical Quality `34678280400 = SUCCESS`.
- Spec/Core exact `8ee183e14ed2527d254def4946ce0b79104f1afa`: Core Focused `34677902970 = SUCCESS`; canonical Quality `34677903014 = IN_PROGRESS` at observation time.
- UI exact `f37b923b6f64f9c75d63febe64aef6c29147069f`: UI Focused `34678773685 = SUCCESS`; canonical Quality `34678773688 = PENDING` at observation time.
- `postmerge/errors@2ca073c51acb726918cfe396ad4baa75a65ee80e` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity absent on current Backend head

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052.
- Current exact Backend head `0ce1a70d421b41cd0ca4441399d97c82b9849285` still lacks the startup identity protection. `src/athena/storage/database.py` executes `inspect_database_read_only(self.path)` and then independently opens `sqlite3.connect()`; no identity-bearing DB/WAL/SHM preflight token is retained across that transition and no file-set identity assertion occurs immediately before or after writer establishment.
- Direct current-head lookup confirms `tests/unit/test_database_startup_identity.py` is still absent (`404 Not Found`).
- New exact-SHA evidence materially sharpens the cluster: Backend Focused `34678280408@0ce1a70d... = SUCCESS` and canonical Quality `34678280400@0ce1a70d... = SUCCESS` even though the product guard and dedicated adversarial coverage remain absent on that same exact SHA. Therefore a green current canonical Quality is not BE-052 closure evidence; the current gate does not exercise this removed release invariant.
- This remains a release-guard regression despite canonical green. Do not reclassify `FIXED_PENDING_VERIFY` or `FIXED` without restoring the invariant and adversarial coverage.
- Required owner correction remains: restore identity-bearing DB/WAL/SHM preflight continuity; assert exact file-set identity before writer open; retain exclusive fail-closed missing-primary creation; assert identity again after writer establishment; after a successful controlled migration, acquire a fresh post-migration identity-bearing preflight and bind that fresh token to writer startup; restore adversarial startup-identity coverage for primary replacement and WAL/SHM sidecar creation/replacement races.
- Required verification: restored startup-identity suite first, then controlled-migration regressions, smallest storage/bootstrap regression set, Backend Focused, and canonical Quality on one unchanged exact Backend SHA.
- Error worker did not mutate Backend product code because Backend actively owns BE-052.

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
