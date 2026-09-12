# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@eab481a0901423ee5821e9d4101f0a0bbf804ef8`.
- Error worker entered this run at `postmerge/errors@4c21173a2bdd9f1a55ad41959ccb06069dd6a65b`.
- Current workers: Spec/Core `acacc2da478d7f7afad4cd44681201268d5b13b3`; Backend `b595c960a747d9805b0865ea9f7237094318b706`; UI `cc0ff61cb6d90b05368e4e1c112c217b5889a5d5`.
- Exact-current Develop canonical Quality: `34662951154@eab481a0901423ee5821e9d4101f0a0bbf804ef8 = IN_PROGRESS`; no Develop PASS/FAIL claim is derived while it is running.
- Previous Develop canonical Quality: `34659583545@5db4c92f40d5d14119a991796be38fb9248072de = SUCCESS`.
- Exact-current Spec/Core canonical Quality: `34661219465@acacc2da478d7f7afad4cd44681201268d5b13b3 = SUCCESS`; focused candidate `34661219526 = SUCCESS`.
- Exact-current Backend canonical Quality: `34662086156@b595c960a747d9805b0865ea9f7237094318b706 = SUCCESS`. Canonical jobs including Windows path safety, Linux storage regressions, Local install smoke, specification validator, Ruff, mypy and full pytest are green.
- Exact-current UI canonical Quality: `34662871880@cc0ff61cb6d90b05368e4e1c112c217b5889a5d5 = IN_PROGRESS`; no UI canonical verdict is inferred while running.
- `postmerge/errors@4c21173a2bdd9f1a55ad41959ccb06069dd6a65b` had zero workflow runs immediately before this mutation.
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
- Fresh reproducer on Develop was `5db4c92f40d5d14119a991796be38fb9248072de`: POSIX `release()` captured logical size, closed pATHENA's descriptor before unlink and then returned that size although a foreign open descriptor or alternate hardlink could retain the inode/blocks.
- Backend exact candidate: `b595c960a747d9805b0865ea9f7237094318b706` (`fix(storage): fail closed on unproven emergency reserve reclamation`).
- Candidate implementation keeps the POSIX reserve descriptor open through identity revalidation and unlink, rejects `st_nlink != 1`, revalidates directory and leaf identity around mutation, and returns `0` after successful POSIX unlink because POSIX cannot portably prove that another process is not retaining the unlinked inode. This removes the prior overstatement of recovered capacity without weakening recovery/storage guards.
- Focused adversarial coverage now includes `test_posix_release_never_overstates_reclamation_with_foreign_descriptor`, which keeps a second descriptor open through release and requires `released == 0` while the foreign descriptor still observes the 4096-byte inode; hardlink ownership and same-parent leaf substitution are also fail-closed covered.
- Exact candidate canonical Quality `34662086156@b595c960a747d9805b0865ea9f7237094318b706 = SUCCESS`; Linux storage regressions and full pytest are green, together with Windows path safety and the remaining canonical jobs.
- Classification is therefore advanced from `OPEN` to `FIXED_PENDING_VERIFY`, not `FIXED`: the bounded owner candidate is exact-green, but the fix is not yet verified after integration onto a current Develop exact SHA. Integrator may review/import this exact candidate; final closure requires integrated exact-SHA verification that preserves the same semantics and gates.

## ERR-0035 — SQLite preflight identity is not carried into live writer startup

- Severity: P1.
- Status: `OPEN` in the carried ledger; this cluster was not revalidated or advanced in this run.
- Specialist owner: Backend / BE-052.
- `SQLiteDatabase.start()` historically performs read-only inspection and later establishes an independent writable SQLite connection without carrying an identity token for the primary DB plus WAL/SHM file set across that interval.
- Closure still requires a bounded Backend candidate that binds or fail-closed revalidates primary DB, WAL and SHM across preflight-to-writer establishment, with adversarial post-inspection/pre-writer mutation coverage and all existing locality/schema/quick-check/Storage/Recovery guards preserved.

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
