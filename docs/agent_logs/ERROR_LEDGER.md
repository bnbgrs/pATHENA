# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@8d34591f08ab1f1a42dbb032963769968aefab2e` (`docs(integrator): record exact worker qualification`).
- Error worker entered this run at `postmerge/errors@23b0c22e2b219fd28a44feb94296c883fab75327`.
- Current workers: Spec/Core `008345141aac276f9723b536a70497e2dec74b20`; Backend `38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`; UI `51c109f6a0e31f82392be6c5bfe1d7d167377499`.
- Exact-current Develop canonical Quality: `34689663093@8d34591f08ab1f1a42dbb032963769968aefab2e = IN_PROGRESS` at observation time. No competing canonical run was started.
- Latest completed Develop canonical Quality: `34687050578@63423bccaf9bf5b4049e55998e2d3303f59ecaf7 = SUCCESS`.
- Backend exact `38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`: Backend Focused `34689028510 = SUCCESS`; canonical Quality `34689028433 = FAILURE`. Canonical jobs show Specification Validator, Ruff, mypy, Windows Path Safety, Linux Storage Regressions and Local Install green; only full pytest failed.
- Spec/Core exact `008345141aac276f9723b536a70497e2dec74b20`: Core Focused `34688220222 = SUCCESS`; canonical Quality `34688220225 = IN_PROGRESS` at observation time.
- UI exact `51c109f6a0e31f82392be6c5bfe1d7d167377499`: UI Focused `34686843794 = SUCCESS`; Integrator reports exact canonical SUCCESS but exact visual regression FAILURE; no UI product mutation is owned here.
- `postmerge/errors@23b0c22e2b219fd28a44feb94296c883fab75327` had zero workflow runs immediately before this mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0040`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0040 — Backend scheduled-materialization candidate full-suite regression

- Severity: P1 integration blocker.
- Status: `OPEN`.
- Exact reproducer: `postmerge/backend@38a61d5f6b41bd151c3662bd1ef2a5a35f240a87`.
- Exact canonical evidence: ATHENA Quality Gate `34689028433 = FAILURE`; Python 3.12 quality fails only at `Quality — pytest`. Specification Validator, Ruff and mypy pass; Windows Path Safety, Linux Storage Regressions and Local Install all pass.
- Exact focused evidence: Backend Focused Candidate `34689028510 = SUCCESS` on the same SHA.
- Parent/integration discriminator: the Develop parent `63423bccaf9bf5b4049e55998e2d3303f59ecaf7` is canonical-green via `34687050578 = SUCCESS`. The exact Backend candidate adds the scheduled-occurrence materialization slice, including `src/athena/jobs/scheduled_materialization.py` and `tests/unit/test_scheduled_materialization.py`, while its focused lane remains green.
- Current diagnosis: this is a real full-suite-only integration regression on the exact Backend candidate, but the failing pytest node/root cause is not exposed by the available workflow metadata. The canonical diagnostics artifact `canonical-quality-diagnostics-38a61d5f6b41bd151c3662bd1ef2a5a35f240a87` exists and must be consumed by the Backend owner before product mutation. Do not guess the failing test and do not attribute the failure to a historical UI or Storage signature without exact diagnostic evidence.
- Ownership: Backend owns the candidate and should consume the canonical diagnostics, reproduce the exact failing test first, then apply the smallest root-cause fix. Errors will not parallel-edit the product while Backend owns this active slice.
- Closure requirement: named failing test/check reproduced on the exact lineage, minimal fix, focused regression set, then exact canonical Quality success. No guard/test weakening, Skip/XFail, or test deletion.

## ERR-0035 — SQLite preflight-to-writer file-set identity continuity

- Severity: P1.
- Status: `FIXED`.
- Specialist owner: Backend / BE-052; integrated repair by Integrator.
- Integrated closure SHA: `develop/pathena-next@8c885669ce3a3d718588d0327828341684c88c71`.
- The integrated `SQLiteDatabase.start()` now consumes an identity-bearing `DatabasePreflightReport`, validates primary DB/WAL/SHM identity before writer open, creates a missing primary exclusively, forces an initial SQLite read, and validates the same accepted identity again before schema initialization or connection-policy mutation.
- Controlled migration is not handled by weakening the guard. `StorageBootstrapService` reacquires a fresh read-only identity-bearing preflight after authorized migration activation and binds that fresh post-migration identity to the live writer transition.
- Exact integrated adversarial coverage exists in `tests/unit/test_storage_database_startup_identity.py` for primary replacement, file-set member replacement, missing-primary foreign creation, sidecar mutation, and replacement during writer establishment.
- Exact integrated controlled-migration coverage exists in `tests/unit/test_storage_bootstrap_identity.py`; it proves a migration receives a fresh activated-database identity and rejects another replacement after that refreshed preflight but before writer startup.
- Exact integrated canonical Quality `34680853488@8c885669ce3a3d718588d0327828341684c88c71 = SUCCESS`. This satisfies the required post-integration exact-SHA verification. Reopen only with a new current exact-SHA reproduction.

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
