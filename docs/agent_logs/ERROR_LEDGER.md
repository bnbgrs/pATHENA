# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80` (`feat(core): integrate stale knowledge maintenance policy`).
- Error worker entered this run at `postmerge/errors@a762c0e5aebb7e015b8bfe66856de8ea5e35c48a`.
- Current workers: Spec/Core `58d76e1e3d7ce1723ca4a75a8cc0608185fae7e8`; Backend `f99f352050cbbcda889cd2a528d95c415992f3ec`; UI `67994fd72ba9f496b50aa407b36d789a4edfb804`.
- Exact-current Develop canonical Quality: `34676594675@cec77b6f8b64ec0bdf29cb546d8db4e1cf16ae80 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running and no competing canonical run was started.
- Previous Develop exact `4dbefe2167b28bffab2c6b69b7a8df4b43770a6f`: canonical Quality `34674406807 = SUCCESS`.
- Backend exact `f99f352050cbbcda889cd2a528d95c415992f3ec`: Backend Focused `34675706783 = SUCCESS`; canonical Quality `34675706788 = FAILURE`. Canonical specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install are green; the full pytest step is the sole failing canonical job step.
- Backend `f99f3520...` is exactly one commit ahead of prior reproducer `a8b30e42...`; that commit changes only `src/athena/jobs/schedule_policy.py`, so the Storage/Recovery regression described below is unchanged on the current Backend head.
- `postmerge/errors@a762c0e5aebb7e015b8bfe66856de8ea5e35c48a` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity regressed on current Backend head

- Severity: P1.
- Status: `OPEN`.
- Specialist owner: Backend / BE-052.
- Current exact Backend head `f99f352050cbbcda889cd2a528d95c415992f3ec` still has the startup identity protection removed. `src/athena/storage/database.py` performs `inspect_database_read_only(self.path)` and then independently opens `sqlite3.connect()`; it does not persist or bind an identity-bearing DB/WAL/SHM preflight token and does not assert that file-set identity before or after writer establishment.
- Direct current-head lookup confirms `tests/unit/test_database_startup_identity.py` is absent (`404 Not Found`). Therefore full-pytest success or failure cannot by itself close BE-052 because the dedicated adversarial startup-identity coverage remains removed.
- The current Backend head is exactly one commit ahead of prior exact reproducer `a8b30e42a22225728c3b9f6efcb3fceba3ee2315`; that one commit only adds `strict=True` to a `zip()` call in `src/athena/jobs/schedule_policy.py`. No Storage/Recovery file changed, so the current exact head inherits the same BE-052 regression without inference across unrelated Storage code.
- CI has materially changed since the prior run: Backend Focused `34675706783@f99f3520... = SUCCESS`; canonical Quality `34675706788@f99f3520... = FAILURE`. In canonical Quality, specification validator, Ruff, mypy, Windows path safety, Linux storage regressions and Local install are green; the full pytest step alone fails. Canonical diagnostics artifact `canonical-quality-diagnostics-f99f352050cbbcda889cd2a528d95c415992f3ec` exists. No unobserved failing-test name is asserted here.
- This remains release-guard weakening and is not integration-ready regardless of whether the current canonical pytest failure is related or unrelated to BE-052.
- Required owner correction remains: restore identity-bearing DB/WAL/SHM preflight continuity; assert exact file-set identity before writer open; retain exclusive fail-closed missing-primary creation; assert identity again after writer establishment; after a successful controlled migration, acquire a fresh post-migration identity-bearing preflight and bind that fresh token to writer startup; restore adversarial startup-identity coverage for primary replacement and WAL/SHM sidecar creation/replacement races.
- Required verification: restored startup-identity suite first, then the two controlled-migration regressions previously exposed by canonical Quality, the smallest storage/bootstrap regression set, Backend Focused, and canonical Quality on one unchanged exact Backend SHA.
- Error worker did not mutate Backend product code because Backend actively owns BE-052 and is changing the same worker lineage.

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
